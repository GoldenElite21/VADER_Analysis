import os
import hashlib
import matplotlib.pyplot as plt
import json
import io
import urllib, base64
import numpy as np
from django.conf import settings
from django.shortcuts import render
from django.db.models import Count
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from django.http import HttpResponse
from wordcloud import WordCloud
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from decimal import Decimal
from io import BytesIO

from .models import AmazonReview
from .utils import figure_to_bytes

# Create your views here.
def index(request):
    settings_vars = {
        'TITLE_WEIGHT': settings.TITLE_WEIGHT,
        'TEXT_WEIGHT': settings.TEXT_WEIGHT,
        'VADER_WEIGHT': settings.VADER_WEIGHT,
        'TEST_ACCURACY': settings.TEST_ACCURACY,
    }
    return render(request, 'index.html', {'settings': settings_vars})

def generate_wordcloud(data, path):
    wordcloud = WordCloud(
        background_color='white',
        max_words=50,
        max_font_size=30,
        scale=4,
        random_state=42
    ).generate(str(data))

    plt.figure(figsize=(16, 9))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(path, format='png', dpi=300)
    plt.close()

def show_wordcloud(request):
    reviews = AmazonReview.objects.all()

    subsets = {
        'All': reviews,
        'Expected Rating - Positive': reviews.filter(expected_rating='positive'),
        'Expected Rating - Negative': reviews.filter(expected_rating='negative'),
        'Sentiment - Positive': reviews.filter(sentiment='positive'),
        'Sentiment - Negative': reviews.filter(sentiment='negative'),
        'Analysis - True': reviews.filter(analysis=True),
        'Analysis - False': reviews.filter(analysis=False)
    }

    top_10_words = []

    for subset_name, subset_reviews in subsets.items():
        # Get the current data for the subset
        data = ""
        for review in subset_reviews:
            data += f"{review.title} {review.text} "

        # Hash for the data to see if we need to recalculate anythig
        hash_object = hashlib.sha256(data.encode('utf-8'))
        data_hash = hash_object.hexdigest()

        # Hash from the last session
        prev_data_hash = request.session.get(f'{subset_name}_data_hash')

        # Check if the data hash is different or the top 10 words for this subset are not yet set
        if data_hash != prev_data_hash or not top_10_words or not any(d['subset_name'] == subset_name for d in top_10_words):
            # Generate word cloud image
            wordcloud = WordCloud(
                background_color='white',
                max_words=50,
                max_font_size=30,
                scale=4,
                random_state=42
            ).generate(str(data))

            word_freq = {}
            for word in wordcloud.words_:
                word_freq[word] = wordcloud.words_[word]
            top_10 = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]

            # Save the new hash in the session
            request.session[f'{subset_name}_data_hash'] = data_hash
        else:
            # Use the stored top 10 words for this subset. Image is already saved
            top_10 = next(d['top_10'] for d in top_10_words if d['subset_name'] == subset_name)

        # Add the subset's top 10 words to the context
        top_10_words.append({
            'subset_name': subset_name,
            'top_10': top_10
        })

    # Render the page with below contexts
    return render(request, 'wordclouds.html', {
        'subsets': subsets,
        'top_10_words': top_10_words,
        'MEDIA_URL': settings.MEDIA_URL
    })

def review_list(request):
    return render(request, 'review_list.html')

@require_GET
def reviews_data(request):
    draw = int(request.GET.get('draw', '0'))
    start = int(request.GET.get('start', '0'))
    #length = int(request.GET.get('length', '10')) # Filters only work well during client side processing. Therefore, we will just pull all the data for now.
    search_value = request.GET.get('search[value]', '')
    search_regex = request.GET.get('search[regex]', False)
    order_column = int(request.GET.get('order[0][column]', '0'))
    order_dir = request.GET.get('order[0][dir]', 'asc')

    columns = ['title', 'text', 'num_words', 'pos', 'neg', 'neu', 'compound', 'sentiment', 'expected_rating', 'analysis']
    order_field = columns[order_column]
    if order_dir == 'desc':
        order_field = '-' + order_field

    reviews = AmazonReview.objects.all()
    total_count = reviews.count()

    if search_value:
        search_fields = [column for column in columns if column != 'text']
        search_filter = '|'.join([f'(?i)\\b{search_value}\\b' for search_value in search_value.split()])
        if search_regex:
            reviews = reviews.filter(**{f'{field}__regex': search_filter for field in search_fields})
        else:
            reviews = reviews.filter(**{f'{field}__iregex': search_filter for field in search_fields})
        filtered_count = reviews.count()
    else:
        filtered_count = total_count

    reviews = reviews.order_by(order_field)
    #reviews = reviews.order_by(order_field)[start:start+length]
    data = [
        {
            'title': review.title,
            'text': review.text,
            'num_words': review.num_words,
            'pos': review.pos,
            'neg': review.neg,
            'neu': review.neu,
            'compound': review.compound,
            'sentiment': review.sentiment,
            'expected_rating': review.expected_rating,
            'analysis': review.analysis
        }
        for review in reviews
    ]

    return JsonResponse({
        'draw': draw,
        'recordsTotal': total_count,
        'recordsFiltered': filtered_count,
        'data': data,
    })

def heatmaps(request):
    reviews = AmazonReview.objects.all()
    subsets = {
        'All': reviews,
        'Sentiment - Positive': reviews.filter(sentiment='positive'),
        'Sentiment - Negative': reviews.filter(sentiment='negative'),
        'Analysis - True': reviews.filter(analysis=True),
        'Analysis - False': reviews.filter(analysis=False),
    }

    plots = {}
    for subset_name, subset in subsets.items():
        # calculate the density of the data using a 2D histogram
        x = [1 if sentiment == 'positive' else 2 for sentiment in subset.values_list('expected_rating', flat=True)]
        y = subset.values_list('compound', flat=True)
        heatmap, xedges, yedges = np.histogram2d(x, y, bins=[2, 20], range=[[0.5, 2.5], [-1, 1]])
        extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

        fig, ax = plt.subplots()
        im = ax.imshow(heatmap.T, extent=extent, aspect='auto', origin='lower', cmap='YlGnBu')
        ax.set_xticks([1, 2])
        ax.set_xticklabels(['Positive', 'Negative'])
        ax.set_xlabel('Given Rating')
        ax.set_ylabel('Compound score')
        ax.set_title(subset_name)

        # Add colorbar
        cbar = fig.colorbar(im, ax=ax)
        cbar.ax.set_ylabel('Density')

        plot_bytes = figure_to_bytes(fig)
        plots[subset_name] = plot_bytes
        plt.close(fig)

    return render(request, 'heatmaps.html', {'plots': plots})

def pie_charts(request):
    reviews = AmazonReview.objects.all()

    charts_data = []
    for field in ['sentiment', 'expected_rating', 'analysis']:
        field_data = reviews.values(field).annotate(total=Count(field)).order_by('-total')
        total_count = sum(item['total'] for item in field_data)
        data = [
            {'label': item[field], 'value': item['total'], 'percentage': round(item['total']/total_count * 100, 2)} for item in field_data
        ]
        charts_data.append({'chart_id': field, 'title': field.title(), 'total_count': int(total_count), 'data': data})

    #TODO: Fix percentage display on tooltip

    return render(request, 'pie_charts.html', {'charts_data': charts_data})
