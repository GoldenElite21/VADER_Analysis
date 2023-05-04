from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class AmazonReview(models.Model):
    rating = models.IntegerField(choices=((1, "1"), (2, "2")))
    title = models.CharField(max_length=250)
    text = models.CharField(max_length=1500)
    num_words = models.IntegerField()
    pos = models.DecimalField(max_digits=5, decimal_places=4, validators=[MinValueValidator(0), MaxValueValidator(1)])
    neg = models.DecimalField(max_digits=5, decimal_places=4, validators=[MinValueValidator(0), MaxValueValidator(1)])
    neu = models.DecimalField(max_digits=5, decimal_places=4, validators=[MinValueValidator(0), MaxValueValidator(1)])
    compound = models.DecimalField(max_digits=6, decimal_places=5, validators=[MinValueValidator(-1), MaxValueValidator(1)])
    sentiment = models.CharField(max_length=8, choices=(("positive", "positive"), ("negative", "negative")))
    expected_rating = models.CharField(max_length=8, choices=(("positive", "positive"), ("negative", "negative")))
    analysis = models.BooleanField()

    def __str__(self):
        return self.title
