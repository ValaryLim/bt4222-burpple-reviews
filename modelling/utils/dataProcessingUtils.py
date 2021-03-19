import ast
import re
import string
import numpy as np 
import pandas as pd 
import nltk
from emot.emo_unicode import UNICODE_EMO
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, PorterStemmer  

STOPWORD_SET = list(STOPWORDS.union(set(stopwords.words("english"))))
NEGATION_TERMS = ["not", "never", "no", "nothing", "neither", "nowhere", "doesn't", "doesn", "isn't", "isn", \
                  "wasn", "wasn't", "cant", "can't", "cannot", "shouldn't", "shouldn", "won", "won't", "couldn't", \
                  "couldn", "couldnt", "don", "don't"]
STOPWORD_SET = set([word for word in STOPWORD_SET if word not in NEGATION_TERMS])

WORD_TOKENIZER = nltk.WordPunctTokenizer()
LEMMATIZER = WordNetLemmatizer()
STEMMER = PorterStemmer()
PUNCTUATION_TABLE = str.maketrans(dict.fromkeys(string.punctuation))

CATEGORY_CUISINE_MAPPING = {
    'Burgers': ['Western'], 
    'Waffles': ['Cafes & Coffee'] , 
    'Healthier Choice': ['Healthy'], 
    'Mookata': ['Thai'], 
    'Nasi Lemak': ['Malay'],  
    'Char Kway Teow': ['Local Delights'], 
    'Vegan': ['Healthy'], 
    'Craft Beer': ['Beverages'], 
    'Kopitiam': ['Local Delights'],  
    'Chirashi': ['Japanese'], 
    'Sandwiches': ['Cafes & Coffee'], 
    'Ice Cream & Yoghurt': ['Desserts'], 
    'Chicken Rice': ['Local Delights'], 
    'Sushi': ['Japanese'], 
    'Zi Char': ['Chinese', 'Local Delights'], 
    'Fruit Tea': ['Beverages'],  
    'Cakes': ['Desserts', 'Cafes & Coffee'],
    'Bubble Tea': ['Beverages'], 
    'Teppanyaki': ['Japanese'], 
    'Korean Desserts': ['Korean', 'Desserts'], 
    'Korean BBQ': ['Korean', 'Desserts'],
    'Bak Kut Teh': ['Local Delights', 'Chinese'], 
    'Hot Pot': ['Chinese'], 
    'Vegetarian': ['Healthy'],  
    'Pasta': ['Italian'], 
    'Ramen': ['Japanese'], 
    'Pizza': ['Italian'], 
    'Steak': ['Western'], 
    'Korean Fried Chicken': ['Korean'], 
    'Dim Sum': ['Chinese'], 
    'Salads': ['Healthy'], 
    'Argentinian': ['Others'], 
    'Turkish': ['Others', 'Halal'],
    'Greek': ['Others'], 
    'Russian': ['Others'],
    'European': ['Western', 'Others'],
    'Brazilian': ['Others'],
    'Fast Food': ['Western'],
    'Bread & Pastries': ['Cafes & Coffee'],
    'Breakfast & Brunch': ['Cafes & Coffee'],
    'Peranakan': ['Local Delights'],
    'Spanish': ['Others'],
    'Bars': ['Beverages', 'Others'],
    'Taiwanese': ['Chinese'],
    'Mediterranean': ['Others'],
    'Middle Eastern': ['Others'],
    'French': ['Others'],
    'Indonesian': ['Others'],
    'Hawker Food': ['Local Delights']
}

FILTERED_CATEGORIES = ['Italian', 'Malay', 'Japanese', 'Chinese', 'Western', 'Korean', 'Thai', 'Vietnamese', \
            'Mexican', 'Indian', 'Local Delights', 'Desserts', 'Healthy', 'Cafes & Coffee', 'Halal']

ADDITIONAL_CATEGORIES = ['Beverages', 'Others']

def process_csv_lists(df, columns):
    for col in columns:
        df[col] = df[col].apply(lambda x: ast.literal_eval(x))
    return df

def process_categories(df, category_column="categories"):
    for category in FILTERED_CATEGORIES:
        df[category] = [1 if category in x else 0 for x in df[category_column]]
    for category in ADDITIONAL_CATEGORIES:
        df[category] = 0
    
    for burpple_category in CATEGORY_CUISINE_MAPPING.keys():
        for actual_category in CATEGORY_CUISINE_MAPPING[burpple_category]:
            # get values to update new row
            updated_row = df[actual_category] # get current values in category
            for i, row in df.iterrows():
                if burpple_category in row[category_column]:
                    updated_row[i] = 1 # label as part of that category

            # update new row
            df[actual_category] = updated_row
    return df

def clean_phrase(phrase, remove_whitespace=True, remove_stopwords=True, remove_punctuation=True, remove_nonascii=True,\
                 remove_single_characters=True, remove_numbers=True, lemmatize=False, stem=False):
    if remove_whitespace:
        phrase = phrase.strip()
    if remove_stopwords:
        phrase = " ".join([word for word in WORD_TOKENIZER.tokenize(phrase) if not word in STOPWORD_SET])
    if remove_punctuation:
        phrase = phrase.translate(PUNCTUATION_TABLE)
    if remove_nonascii:
        phrase = phrase.encode("ascii", "ignore").decode()
    if remove_single_characters:
        phrase = " ".join([word for word in phrase.split() if len(word) > 1])
    if remove_numbers:
        phrase = "".join([i for i in phrase if not i.isdigit()])
    if lemmatize:
        phrase = " ".join([LEMMATIZER.lemmatize(word) for word in WORD_TOKENIZER.tokenize(phrase)])
    if stem:
        phrase = " ".join([STEMMER.stem(word) for word in WORD_TOKENIZER.tokenize(phrase)])

    phrase = " ".join(phrase.split())
    return phrase.lower()

def process_emojis(df, text_col, text_pos, text_neg):
    """
    :df: Dataframe to convert
    :text_col: Column containing text that we want to replace emojis
    :text_pos: Text we want to replace positive sentiment emojis with, e.g. emoji_good, good
    :text_neg: Text we want to replace negative sentiment emojis with, e.g. emoji_bad, bad
    :returns: Original Dataframe with text_col overwritten
    """
    # Get Mapping
    mapping = get_emoji_sentiment_mapping(UNICODE_EMO, text_pos, text_neg)

    # Get Column
    phrases = df[text_col]
    processed_text = []

    for p in phrases:
        processed_text.append(replace_emojis(p, mapping))

    df[text_col] = processed_text
    
    return df

def replace_emojis(text, mapping):
    for emot in mapping:
        text = text.replace(emot, ' ' + mapping[emot] + ' ').strip()
    return " ".join(text.split())

def get_emoji_sentiment_mapping(UNICODE_EMO, text_pos, text_neg):
    analyser = SentimentIntensityAnalyzer()
    d = {}
    for k in UNICODE_EMO:
        pol = analyser.polarity_scores(k)
        if pol['neu'] == 1.0:
            continue
        elif pol['compound'] > 0.4: 
            d[k] = text_pos
        elif pol['compound'] < -0.3:
            d[k] = text_neg
    return d