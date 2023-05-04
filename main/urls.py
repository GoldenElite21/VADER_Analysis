from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
import os
from . import views

urlpatterns = [
        path('', views.index, name='index'),
        path('wordclouds/', views.show_wordcloud, name='wordclouds'),
        path('review_list/', views.review_list, name='review_list'),
        path('reviews_data/', views.reviews_data, name='reviews_data'),
        path('heatmaps/', views.heatmaps, name='heatmaps'),
        path('pie_charts/', views.pie_charts, name='pie_charts'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
