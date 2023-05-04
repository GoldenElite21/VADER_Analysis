#!/usr/bin/env python3
from nltk.sentiment.vader import SentimentIntensityAnalyzer
 
def sentiment_scores(sentence, weight=0.05, do_print=False):

    sid_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sid_obj.polarity_scores(sentence)
    
    if do_print:
        print("Statement is: " + sentence)
        print("Overall sentiment dictionary is : ", sentiment_dict)
        for sentiment in ['Negative', 'Neutral', 'Positive']:
            print("Sentence was rated as ", sentiment_dict[sentiment[0:3].lower()]*100, "% ", sentiment)
    
        print("Sentence Overall Rated As", end=" ")
 
        # Compound sentiment decision
        print("Positive" if sentiment_dict['compound'] >= weight else "Negative" if sentiment_dict['compound'] <= -weight else "Neutral")
    
    return sentiment_dict

print("\n1st statement:")
sentiment_scores("Angelo State University is the BEST university for Computer Science majors.",0.05,True)

print("\n2nd Statement:")
sentiment_scores("The flight went by rather quickly.",0.05,True)
 
print("\n3rd Statement:")
sentiment_scores("I am very sad today.",0.05,True)

print("\n4th Statement:")
sentiment_scores("I am VERY SAD today!",0.05,True)
