import ast
import re
import string
import utils
import numpy as np 
import pandas as pd 
from emot.emo_unicode import UNICODE_EMO, EMOTICONS
import nltk
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

def clean_phrase(phrase, remove_whitespace=True, remove_stopwords=True, remove_punctuation=True, remove_nouns=True, remove_nonascii=True,\
                 remove_single_characters=True, remove_numbers=True, lemmatize=False, stem=False):
    if remove_whitespace:
        phrase = phrase.strip()
    if remove_stopwords:
        phrase = " ".join([word for word in WORD_TOKENIZER.tokenize(phrase) if not word in STOPWORD_SET])
    if remove_punctuation:
        phrase = phrase.translate(PUNCTUATION_TABLE)
    if remove_nouns:
        pos_df = utils.get_pos(phrase)
        nouns = list(pos_df.loc[pos_df['pos']=='NOUN']['text'])
        word_tokens = word_tokenize(phrase)
        new_phrase_list = [w for w in word_tokens if not w in nouns]
        phrase = " ".join(new_phrase_list)
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
    
    # replace negated terms
    phrase = re.sub(r"\bnt\b", "not", phrase)
    phrase = re.sub(r"\bn't\b", "not", phrase)
    
    phrase = " ".join(phrase.split())
    return phrase.lower()

def one_hot_encode_emojis(df, column):
    phrases = df[column]
  
    # Find all the emojis in the text
    emojis = []
    for p in phrases:
        emojis_in_phrase = []
        for char in p:
            if char in UNICODE_EMO: 
                string_rep = UNICODE_EMO[char].replace(":","")
                # do not store duplicate emojis
                if string_rep not in emojis_in_phrase:
                    emojis_in_phrase.append(string_rep)
        emojis.append(emojis_in_phrase)

    # Prepare for one hot encoding 
    df['emojis'] = emojis
    values = df.emojis.values 
    lengths = [len(x) for x in values.tolist()]
    f, u = pd.factorize(np.concatenate(values))
    n,m = len(values), u.size
    i = np.arange(n).repeat(lengths)

    # Create dataframe with dummies
    dummies = pd.DataFrame(np.bincount(i*m+f, minlength = n*m).reshape(n,m), df.index, u)

    # Append dataframe to original df
    df = df.drop('emojis', 1).join(dummies)

    return df
