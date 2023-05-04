#!/usr/bin/env python3

import os
import sys
import django

# Add the project's root directory to the system's PYTHONPATH
sys.path.insert(0, os.path.join(os.environ.get('PROJECT_ROOT'), 'amazonreviews'))

# Set up Django
django.setup()
from main.models import AmazonReview

# Save the review
review = AmazonReview(
    rating=2,
    title='Testing123',
    text='I really enjoyed using this product. It exceeded my expectations.',
    num_words=12,
    pos=0.8,
    neg=0.1,
    neu=0.1,
    compound=0.9,
    sentiment='positive',
    expected_rating='positive',
    analysis=True
)

review.save()

input("Press enter to continue...")
# Retreive the review
print('Review saved successfully. Proving query...')

review = AmazonReview.objects.filter(title='Testing123').last()

# Print the review details
print('ID:', review.id)
print('Rating:', review.rating)
print('Title:', review.title)
print('Text:', review.text)
print('Number of words:', review.num_words)
print('Positive score:', review.pos)
print('Negative score:', review.neg)
print('Neutral score:', review.neu)
print('Compound score:', review.compound)
print('Sentiment:', review.sentiment)
print('Expected rating:', review.expected_rating)
print('Analysis:', review.analysis)

input("Press enter to continue...")
# Delete our test records
# Retrieve the review object from the database
reviews = AmazonReview.objects.filter(title='Testing123')

# Delete the review object
reviews.delete()
