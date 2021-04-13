import re
import string
import utils
import numpy as np 
import pandas as pd 
from emot.emo_unicode import UNICODE_EMO, EMOTICONS
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
from nltk.corpus import stopwords
nltk.download('wordnet')
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, PorterStemmer 
nltk.download('wordnet')

STOPWORD_SET = list(STOPWORDS.union(set(stopwords.words("english"))))
NEGATION_TERMS = ["not", "never", "no", "nothing", "neither", "nowhere", "doesn't", "doesn", "isn't", "isn", \
                  "wasn", "wasn't", "cant", "can't", "cannot", "shouldn't", "shouldn", "won", "won't", "couldn't", \
                  "couldn", "couldnt", "don", "don't"]
STOPWORD_SET = set([word for word in STOPWORD_SET if word not in NEGATION_TERMS])

WORD_TOKENIZER = nltk.WordPunctTokenizer()
LEMMATIZER = WordNetLemmatizer()
STEMMER = PorterStemmer()
PUNCTUATION_TABLE = str.maketrans(dict.fromkeys(string.punctuation))

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

EMOJI_GENERIC_MAPPING = get_emoji_sentiment_mapping(UNICODE_EMO, 'good', 'bad')
EMOJI_UNIQUE_MAPPING = get_emoji_sentiment_mapping(UNICODE_EMO, 'emoji_good', 'emoji_bad')

def clean_phrase(phrase, remove_whitespace=True, remove_stopwords=True, remove_punctuation=True, remove_nonascii=True, \
                 remove_single_characters=True, remove_numbers=True, lemmatize=False, stem=False, convert_emoji_generic=False, \
                 convert_emoji_unique=False):
    if convert_emoji_generic:
        phrase = replace_emojis(phrase, EMOJI_GENERIC_MAPPING)
    if convert_emoji_unique:
        phrase = replace_emojis(phrase, EMOJI_UNIQUE_MAPPING)
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

def replace_emojis(text, mapping):
    for emot in mapping:
        text = text.replace(emot, ' ' + mapping[emot] + ' ').strip()
    return " ".join(text.split())


def postprocessing_pipeline(rule_mined_csv, postprocessed_csv):
    '''
    Runs postprocessing on rule mined file
    '''
    rule_mined_df = pd.read_csv(rule_mined_csv)

    # clean phrases
    rule_mined_df["phrase_lemma"] = rule_mined_df.phrase.apply(lambda x: clean_phrase(x, lemmatize=True, stem=False))
    rule_mined_df["phrase_stem"] = rule_mined_df.phrase.apply(lambda x: clean_phrase(x, lemmatize=False, stem=True))
    rule_mined_df["phrase_emoticon_generic"] = rule_mined_df.phrase.apply(lambda x: clean_phrase(x, lemmatize=False, stem=False, convert_emoji_generic = True))
    rule_mined_df["phrase_lemma_emoticon_generic"] = rule_mined_df.phrase.apply(lambda x: clean_phrase(x, lemmatize=True, stem=False, convert_emoji_generic = True))
    rule_mined_df["phrase_stem_emoticon_generic"] = rule_mined_df.phrase.apply(lambda x: clean_phrase(x, lemmatize=False, stem=True, convert_emoji_generic = True))
    rule_mined_df["phrase_emoticon_unique"] = rule_mined_df.phrase.apply(lambda x: clean_phrase(x, lemmatize=False, stem=False, convert_emoji_unique = True))
    rule_mined_df["phrase_lemma_emoticon_unique"] = rule_mined_df.phrase.apply(lambda x: clean_phrase(x, lemmatize=True, stem=False, convert_emoji_unique = True))
    rule_mined_df["phrase_stem_emoticon_unique"] = rule_mined_df.phrase.apply(lambda x: clean_phrase(x, lemmatize=False, stem=True, convert_emoji_unique = True))
    rule_mined_df.phrase = rule_mined_df.phrase.apply(lambda x: clean_phrase(x, lemmatize=False, stem=False))

    # filter out rows where there are no characters
    rule_mined_df = rule_mined_df.loc[(rule_mined_df.phrase.str.len() > 0)]

    # aggregate phrases
    postprocessed_df = rule_mined_df.groupby(["restaurant_code", "review_title", "review_body", "review_date",\
        "review_title_raw", "review_body_raw", "account_name", "account_id", "account_level", "account_photo", \
        "review_photo", "scraped_date", "aspect"
        ], as_index=False).agg({
            "phrase": " ".join,
            "phrase_lemma":" ".join,
            "phrase_stem":" ".join,
            "phrase_emoticon_generic" : " ".join,
            "phrase_emoticon_unique" : " ".join,
            "phrase_stem_emoticon_generic" : " ".join,
            "phrase_lemma_emoticon_generic": " ".join,
            "phrase_stem_emoticon_unique": " ".join,
            "phrase_lemma_emoticon_unique" : " ".join
        })
    postprocessed_df = postprocessed_df.reset_index(drop=True)

    postprocessed_df.to_csv(postprocessed_csv, index=False)
    print("POST-PROCESSING COMPLETE")