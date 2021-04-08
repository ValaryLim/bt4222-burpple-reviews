import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import numpy as np
import ast
import os
import en_core_web_sm
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize  
import string
from string import digits

nlp = en_core_web_sm.load()
nltk.download('punkt')

FOOD_LIST = list(pd.read_csv("utils/aspects/food.csv")['food'].astype(str))
TIME_LIST = list(pd.read_csv("utils/aspects/time.csv")['time'].astype(str))
PRICE_LIST = list(pd.read_csv("utils/aspects/price.csv")['price'].astype(str))
PORTION_LIST = list(pd.read_csv("utils/aspects/portion.csv")['portion'].astype(str))
SERVICE_LIST = list(pd.read_csv("utils/aspects/service.csv")['service'].astype(str))
AMBIENCE_LIST = list(pd.read_csv("utils/aspects/ambience.csv")['ambience'].astype(str))


def get_all_aspects(df):
    '''
    description: get the unique synonyms for each aspect 
    input: dataframe
    output: dataframe (saved as csv)
    '''
    food = []
    time = []
    price = []
    portion = []
    service = []
    ambience = []
    for row in range(0, len(df)) :
        # turn each aspects string into dictionary
        row_aspects_dict = ast.literal_eval(df['aspects'][row])
        # get the aspect keys
        row_aspects_keys = list(row_aspects_dict.keys())
        for key in row_aspects_keys :
            if key == 'food' :
                for value in row_aspects_dict['food'] :
                    if value not in food :
                        food.append(str(value))
            elif key == 'time' :
                for value in row_aspects_dict['time'] :
                    if value not in time :
                        time.append(str(value))
            elif key == 'price' :
                for value in row_aspects_dict['price'] :
                    if value not in price :
                        price.append(str(value))
            elif key == 'portion' :
                for value in row_aspects_dict['portion'] :
                    if value not in portion :
                        portion.append(str(value))
            elif key == 'service' :
                for value in row_aspects_dict['service'] :
                    if value not in service :
                        service.append(str(value))
            elif key == 'ambience' :
                for value in row_aspects_dict['ambience'] :
                    if value not in ambience :
                        ambience.append(str(value))
        print(row, "out of", len(df), "done")
    # create dataframe
    food_df = pd.DataFrame({'food': food})
    time_df = pd.DataFrame({'time': time})
    price_df = pd.DataFrame({'price': price})
    portion_df = pd.DataFrame({'portion': portion})
    service_df = pd.DataFrame({'service': service})
    ambience_df = pd.DataFrame({'ambience': ambience})
    print("dataframes created")
    # create new folder
    if not os.path.exists('./aspects') :
        os.makedirs('./aspects')
    # save as csv
    food_df.to_csv("./aspects/food.csv", index=False)
    time_df.to_csv("./aspects/time.csv", index=False)
    price_df.to_csv("./aspects/price.csv", index=False)
    portion_df.to_csv("./aspects/portion.csv", index=False)
    service_df.to_csv("./aspects/service.csv", index=False)
    ambience_df.to_csv("./aspects/ambience.csv", index=False)
    print("dataframes saved")

def get_pos(review) :
    '''
    description: get the text, pos and tag of each word
    input: text
    output: dataframe
    '''
    text = []
    pos = []
    tag = []
    doc = nlp(review)
    for token in doc:
        text.append(token.text)
        pos.append(token.pos_)
        tag.append(token.tag_)
    pos_df = pd.DataFrame({'text': text, 'pos': pos, 'tag': tag})
    return pos_df

def get_aspects(review, pos_df, aspect_list):
    '''
    description: get aspects
    input: string, list
    output: list, list
    '''
    # get aspects present in review
    aspects = list(pos_df.loc[pos_df['text'].isin(aspect_list)]['text'])
    # get sentences with aspects
    aspect_sentences = []
    # split into sentences
    sentences = review.split('.')
    for i in range(0, len(sentences)) :
        if any(aspect in sentences[i] for aspect in aspect_list) :
            aspect_sentences.append(sentences[i])
    return aspects, aspect_sentences

def ranges(nums):
    '''
    description: get the ranges
    input: list
    output: list
    '''
    nums = sorted(set(nums))
    gaps = [[s, e] for s, e in zip(nums, nums[1:]) if s+1 < e]
    edges = iter(nums[:1] + sum(gaps, []) + nums[-1:])
    return list(zip(edges, edges))

def pos_before_after_aspect(pos_df, aspect_list, target_pos) :
    '''
    description: get the text where first word is target_pos and last word is aspect and vice versa
    input: dataframe, list, str
    output: list
    '''
    start, end = 0, 0
    sentences = []
    positions_start = []
    positions_end = []
    filtered = []
    aspect_index = list(pos_df.loc[pos_df['text'].isin(aspect_list)].index)
    
    # adjectives before
    for i in range(0, len(aspect_index)) :
        index = aspect_index[i]
        for j in reversed(range(0, index)) :
            if pos_df['pos'][j] == target_pos or pos_df['pos'][j] == 'VERB':
                # check if there is an adv or det before then add that
                if j>1 :
                    if pos_df['pos'][j-1] == 'ADV' or pos_df['pos'][j-1] == 'DET' :
                        positions_start.append(j-1)
                        positions_end.append(index+1)
                    else :
                        positions_start.append(j)
                        positions_end.append(index+1)
                else :
                    positions_start.append(j)
                    positions_end.append(index+1)  

    # adjectives after
    for i in range(0, len(aspect_index)) :
        index = aspect_index[i]
        for j in range(index, len(pos_df)) :
            if pos_df['pos'][j] == target_pos :
                positions_start.append(index+1)
                positions_end.append(j)
            
    positions_df = pd.DataFrame({'start': positions_start, 'end': positions_end})
    positions_df = positions_df.drop_duplicates().reset_index(drop=True)
    positions_df = positions_df.sort_values(by=['start', 'end'])
    filtered_df_1 = positions_df.drop_duplicates(subset=['end'], keep='last').reset_index(drop=True)
    filtered_df = filtered_df_1.drop_duplicates(subset=['start'], keep='last').reset_index(drop=True)
    
    for i in range(0, len(filtered_df)) :
        start = filtered_df['start'][i]
        end = filtered_df['end'][i]
        if start < end and start!=0 and end!=0:
            review = pos_df['text'][start:end+1].apply(lambda x:x + ' ').sum()
            if '.' in review :
                review = review.split(".")[0]
            elif '!' in review :
                review = review.split("!")[0]
            elif '?' in review :
                review = review.split("?")[0]
            if len(review) > 0 :
                filtered.append(review)
    return filtered

def get_sentence_indexes(sentence, pos_df) :
    '''
    description: get the start and end indexes of the sentence
    input: string, dataframe
    output: dataframe
    '''
    sentence_split = sentence.split(" ")
    target_pos = pos_df.loc[pos_df['text'].isin(sentence_split)]
    target_index = list(target_pos.index)
    ranges_list = ranges(target_index)
    for i in ranges_list :
        if i[0] != i[1] :
            start = i[0]
            end = i[1] + 1
            return pos_df[start:end]

def get_sentences_indexes(sentence, pos_df) :
    all_indexes = pd.DataFrame({'text':[], 'pos':[],'tag':[]})
    for i in range(0, len(sentence)) :
        pos_df_target = get_sentence_indexes(sentence[i], pos_df)
        all_indexes = pd.concat([all_indexes, pos_df_target])
    return all_indexes
        
def get_sentences(pos_df, pos_df_original) :
    '''
    description: get the sentences from indexes
    input: dataframe, dataframe
    output: list
    '''
    pos_df_phrases = []
    pos_df_index = list(pos_df.index)
    ranges_list = ranges(pos_df_index)
    for i in ranges_list :
        if i[0] != i[1] :
            start = i[0]
            end = i[1] + 1
            pos_df_phrases.append(pos_df_original['text'][start:end].apply(lambda x:x + ' ').sum())
    return pos_df_phrases

def process_review_aspect(review, pos_df, aspect_list) :
    '''
    description: apply functions to aspect
    input: str, dataframe, list
    output: list
    '''
    aspects, sentence = get_aspects(review, pos_df, aspect_list)
    sentence_new = pos_before_after_aspect(pos_df, aspects, 'ADJ')
    aspect_pos = get_sentences_indexes(sentence_new, pos_df)
    aspect_pos = aspect_pos.sort_index().drop_duplicates()
    phrase_list = get_sentences(aspect_pos, pos_df)
    return phrase_list

def add_phrases(df, all_aspects) :
    '''
    description: add phrase_no_noun and phrase_no_aspect
    input: dataframe, list
    output: dataframe
    '''
    new_phrase_no_aspect = []
    new_phrase_no_noun = []
    for i in range(0, len(df)) :
        no_aspect = []
        no_noun = []
        phrase_list = df['phrase'][i].split(', ')
        for phrase in phrase_list:
            if phrase not in all_aspects :
                no_aspect.append(phrase)
            if get_pos(phrase)['pos'][0] != 'NOUN' :
                no_noun.append(phrase)
        new_phrase_no_aspect.append(no_aspect)
        new_phrase_no_noun.append(no_noun)
    df['phrase_no_aspect'] = new_phrase_no_aspect
    df['phrase_no_noun'] = new_phrase_no_noun
    return df


def generate_phrase_list(row, phrase, aspect):
    return {
        "restaurant_code": row["restaurant_code"],
        "review_title": row["review_title"],
        "review_body": row["review_body"],
        "review_title_raw": row["review_title_raw"],
        "review_body_raw": row["review_body_raw"], 
        "review_date": row["review_date"],
        "account_name": row["account_name"],
        "account_id": row["account_id"],
        "account_level": row["account_level"],
        "account_photo": row["account_photo"],
        "review_photo": row["review_photo"],
        "scraped_date": row["scraped_date"],
        "aspect": aspect,
        "phrase": phrase
    }

def rule_mining_pipeline(preprocessed_csv, rule_mined_csv) :
    '''
    Reads preprocessed csv and outputs new csv with reviews split into aspects
    '''
    df = pd.read_csv(preprocessed_csv)
    df = df.fillna("")
    
    food_phrases, time_phrases, price_phrases, portion_phrases, service_phrases, ambience_phrases = [], [], [], [], [], []
    aspect_list, phrase_list, restaurant_code, review_title, review_body, account_name, account_id = [], [], [], [], [], [], []
    
    phrases_data_list = []
    for i, row in df.iterrows():
        review = (row["review_title"] + " " + row["review_body"]).lower()
        
        # for pre-processing
        pos_df = get_pos(review)
        
        # get phrases for each aspect
        food_phrases = process_review_aspect(review, pos_df, FOOD_LIST) 
        time_phrases = process_review_aspect(review, pos_df, TIME_LIST)
        price_phrases = process_review_aspect(review, pos_df, PRICE_LIST)
        portion_phrases = process_review_aspect(review, pos_df, PORTION_LIST)
        service_phrases = process_review_aspect(review, pos_df, SERVICE_LIST)
        ambience_phrases = process_review_aspect(review, pos_df, AMBIENCE_LIST)

        for phrase in food_phrases:
            phrases_data_list.append(generate_phrase_list(row, phrase, "food"))
        for phrase in time_phrases:
            phrases_data_list.append(generate_phrase_list(row, phrase, "time"))
        for phrase in price_phrases:
            phrases_data_list.append(generate_phrase_list(row, phrase, "price"))
        for phrase in portion_phrases:
            phrases_data_list.append(generate_phrase_list(row, phrase, "portion"))
        for phrase in service_phrases:
            phrases_data_list.append(generate_phrase_list(row, phrase, "service"))
        for phrase in ambience_phrases:
            phrases_data_list.append(generate_phrase_list(row, phrase, "ambience"))
    
    # create df
    output = pd.DataFrame(phrases_data_list)

    # remove empty phrases
    output = output.loc[output['phrase'].apply(lambda x: len(x)>0)]

    # set phrases to str
    output['phrase'] = output['phrase'].apply(lambda x: "".join(x))

    # remove duplicated rows
    output = output.drop_duplicates().reset_index(drop=True)
    
    # save as csv
    output.to_csv(rule_mined_csv, index=False)
    print("RULE MINING COMPLETE")