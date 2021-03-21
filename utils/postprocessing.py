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

def postprocessing_pipeline(rule_mined_csv, postprocessed_csv):
    '''
    Runs postprocessing on rule mined file
    '''
    rule_mined_df = pd.read_csv(rule_mined_csv)

    # one hot encode emojis

    # generate phrase combinations

    postprocessed_df = pd.DataFrame(columns=["restaurant-code", "review_title", "review_body", "account_name", 
        "account_id",  "account_level", "account_photo", "review_photo", "location", "aspect", 
        "phrase", "phrase_lemma", "phrase_stem", "phrase_emoticon_generic", "phrase_emoticon_unique",
        "phrase_stem_emoticon_generic", "phrase_lemma_emoticon_generic", "phrase_stem_emoticon_unique", 
        "phrase_lemma_emoticon_unique"])  # THESE ARE THE COLUMNS I WANT
    postprocessed_df.to_csv(postprocessed_csv, index=False)
    return