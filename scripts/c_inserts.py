#!/usr/bin/env python3

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os
from joblib import Parallel, delayed
import argparse
import sys

# Define the command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--test", help="Run the script in test mode. This is used to acquire weights to set for use in larger batches.", action="store_true")
args = parser.parse_args()

# Check if the --test switch was provided
if args.test:
    print("Running in test mode...")


def sentiment_scores(sentence, weight=0.05, do_print=False):
    sid_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sid_obj.polarity_scores(sentence)
    
    if do_print:
        print('Overall sentiment dictionary utilizing weight', weight, 'is : ', sentiment_dict)
        for sentiment in ['Negative', 'Neutral', 'Positive']:
            print("Sentence was rated as ", sentiment_dict[sentiment[0:3].lower()]*100, "% ", sentiment)
    
        print("Sentence Overall Rated As", end=" ")
 
        # Compound sentiment decision
        print("Positive" if sentiment_dict['compound'] >= weight else "Negative" if sentiment_dict['compound'] <= -weight else "Neutral")
    
    return sentiment_dict

# Weight title and text differently. We will calculate the weights appropriately
def _calc_weighted_sentiment(title_sentiment_scores, text_sentiment_scores, title_w, text_w):
    weighted_sentiment_scores = ((title_sentiment_scores * title_w) + (text_sentiment_scores * text_w)) / (title_w + text_w)
    return weighted_sentiment_scores

def _sentiment_scores_helper(sentence, sentiment):
    return sentiment_scores(sentence, do_print=False)[sentiment]

def weighted_sentiment(sentiment, title_w=3, text_w=2):
    print('Running weight title', '/', 'text:', title_w, '/', text_w, ' for sentiment ', sentiment, '...')
    
    title_sentiment_scores = np.array(Parallel(n_jobs=-1)(delayed(_sentiment_scores_helper)(x, sentiment) for x in reviews['title']))
    text_sentiment_scores = np.array(Parallel(n_jobs=-1)(delayed(_sentiment_scores_helper)(x, sentiment) for x in reviews['text']))
    
    weighted_sentiment_scores = _calc_weighted_sentiment(title_sentiment_scores, text_sentiment_scores, title_w, text_w)
    
    return weighted_sentiment_scores

# Post calculations
def calc_vader(compound, weight):
    # Since we only have a positive and negative for our dataset, we are removing the possibility of neutral results
    return "positive" if compound >= weight else "negative"

def weighted_reviews(rev, w):
    wr = rev.copy()
    wr['sentiment'] = wr['compound'].apply(lambda x: calc_vader(x, w))
    wr['expected_rating'] = wr['rating'].apply(lambda x: calc_vader(x, 2)) #pos=2, else neg 
    wr['analysis'] = np.where((wr['sentiment'] == wr['expected_rating']), True, False)
    return wr

def calc_confidence(mr):
    match_count = len(mr[mr.analysis == True])
    confidence = (match_count/len(mr))*100
    #print(weight, match_count, confidence)
    return confidence


print('Reading the CSV...')
reviews = pd.read_csv('csv/test.csv')

print('Remove rows without data...')
for i in ['rating','title','text']: 
    reviews = reviews[reviews[i].notna()]

print('Adding num_words and keep only those with enough data to make conclusions...')
reviews['num_words'] = (reviews['title'] + reviews['text']).apply(lambda x: len(x.split(" ")))

print('Removing submissions with < 5 words...')
reviews = reviews[reviews['num_words'] >= 5]

print('Sample size to remove subjective bias. Running with no replace...')
sample_frac = (0.001 if args.test else 0.1) # Test training data takes a while, so sample size should be smaller
reviews = reviews.sample(frac = sample_frac, replace = False, random_state=42)
print('Remaining reviews sample size:', len(reviews))

if args.test:
    print('Calculating confidence in batch...')
    best_weight = 0
    best_confidence = 0
    best_title_weight = 0
    best_text_weight = 0

    for title_weight in range(1,10):
        for text_weight in range(1,10):
            reviews['compound'] = weighted_sentiment('compound', title_weight, text_weight)
            for x in range(1,100):
                weight = x/100
                temp = weighted_reviews(reviews, weight)
                weight_confidence = calc_confidence(temp)
                if weight_confidence >= best_confidence:
                    best_weight = weight
                    best_confidence = weight_confidence
                    best_title_weight = title_weight
                    best_text_weight = text_weight
                    reviews = temp

    for i in ['pos','neg','neu']:
        reviews[i] = weighted_sentiment(i, best_title_weight, best_text_weight)

    for i in ['sentiment','expected_rating']:
        print('\n', reviews[i].value_counts())

    print('\nFirst record example: \n', reviews.iloc[0])

    print('\nSample size:', len(reviews)) 
    print('\nReview to Rating General Correlations:')
    print('Best title', '/', 'text ratio: ', best_title_weight, '/', best_text_weight)
    print('Best Weight: ', best_weight)
    print('Best Confidence: ', best_confidence)
else: # If confidences are found, set them in settings.py and run in default for inserts into DB
    print('Setting up Django connections...')
    import django
    from django.conf import settings

    # Add the project's root directory to the system's PYTHONPATH
    sys.path.insert(0, os.path.join(os.environ.get('PROJECT_ROOT'), 'amazonreviews'))

    # Set up Django
    django.setup()
    from main.models import AmazonReview

    for i in ['compound','pos','neg','neu']:
        reviews[i] = weighted_sentiment(i, settings.TITLE_WEIGHT, settings.TEXT_WEIGHT)
    reviews = weighted_reviews(reviews, settings.VADER_WEIGHT)

    print('Beginning inserts...')
    # Verify we have all the data
    required_cols = ['rating', 'title', 'text', 'num_words', 'pos', 'neg', 'neu', 'compound', 'sentiment', 'expected_rating', 'analysis']
    if all(col in reviews.columns for col in required_cols):
        print("All required columns are in the DataFrame. Proceeding to insert data into the database...")
    else:
        print("Some required columns are missing from the DataFrame. Exiting now.")
        quit()

    reviews_list = reviews.to_dict('records')
    amazon_reviews = [AmazonReview(**review) for review in reviews_list]
    AmazonReview.objects.bulk_create(amazon_reviews)
