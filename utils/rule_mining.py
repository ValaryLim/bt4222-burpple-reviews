import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import numpy as np
import ast
import os
import en_core_web_sm
nlp = en_core_web_sm.load()
import re
import nltk
from nltk.corpus import stopwords
nltk.download('punkt')
from nltk.tokenize import word_tokenize  
import string
from string import digits

'''
description: get the unique synonyms for each aspect 
input: dataframe
output: dataframe (saved as csv)
'''
def get_all_aspects(df) :
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

'''
description: get the text, pos and tag of each word
input: text
output: dataframe
'''
def get_pos(review) :
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

'''
description: get aspects
input: string, list
output: list, list
'''
def get_aspects(review, pos_df, aspect_list) :
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

'''
description: get the ranges
input: list
output: list
'''
def ranges(nums):
    nums = sorted(set(nums))
    gaps = [[s, e] for s, e in zip(nums, nums[1:]) if s+1 < e]
    edges = iter(nums[:1] + sum(gaps, []) + nums[-1:])
    return list(zip(edges, edges))

'''
description: get the text where first word is target_pos and last word is aspect and vice versa
input: dataframe, list, str
output: list
'''
def pos_before_after_aspect(pos_df, aspect_list, target_pos) :
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

'''
description: get the start and end indexes of the sentence
input: string, dataframe
output: dataframe
'''
def get_sentence_indexes(sentence, pos_df) :
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
        
'''
description: get the sentences from indexes
input: dataframe, dataframe
output: list
'''
def get_sentences(pos_df, pos_df_original) :
    pos_df_phrases = []
    pos_df_index = list(pos_df.index)
    ranges_list = ranges(pos_df_index)
    for i in ranges_list :
        if i[0] != i[1] :
            start = i[0]
            end = i[1] + 1
            pos_df_phrases.append(pos_df_original['text'][start:end].apply(lambda x:x + ' ').sum())
    return pos_df_phrases

'''
description: apply functions to aspect
input: str, dataframe, list
output: list
'''
def process_review_aspect(review, pos_df, aspect_list, to_remove) :
    aspects, sentence = get_aspects(review, pos_df, aspect_list)
    sentence_new = pos_before_after_aspect(pos_df, aspects, 'ADJ')
    aspect_pos = get_sentences_indexes(sentence_new, pos_df)
    aspect_pos = aspect_pos.sort_index().drop_duplicates()
    phrase_list = get_sentences(aspect_pos, pos_df)
    phrase_list_cleaned = post_processing(phrase_list, to_remove)
    return phrase_list_cleaned

'''
description: add phrase_no_noun and phrase_no_aspect
input: dataframe, list
output: dataframe
'''
def add_phrases(df, all_aspects) :
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

'''
description: apply functions to review
input: path to dataframe
output: dataframe
'''
def process_reviews(df, df_path, to_save) :
    
    # for post-processing
    stop_words_to_remove = set(stopwords.words('english'))
    # negated terms to not remove
    stop_words_dont_remove = set(['no', 'not', 'nor']) 
    # stop_words_dont_remove = set(['no', 'not', 'nor', 'don', "don't", 'should', "should've", 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]) 
    stop_words = list(stop_words_to_remove-stop_words_dont_remove)
    punctuations = list(string.punctuation)
    to_remove = stop_words + punctuations + ["'s"]
    
    # df = pd.read_csv(df_path)
    
    food_phrases = []
    time_phrases = []
    price_phrases = []
    portion_phrases = []
    service_phrases = []
    ambience_phrases = []
    
    aspect_list = []
    phrase_list = []
    restaurant_code = []
    review_title = []
    review_body = []
    account_name = []
    account_id = []
    
    for i in range(0, len(df)) :
        
        review = (str(df['review_title'][i])+str(df['review_body'][i])).lower()
        # for pre-processing
        review = pre_processing(review)
        pos_df = get_pos(review)
        
        # get phrases for each aspect
        food_phrases = process_review_aspect(review, pos_df, food_list, to_remove)
        time_phrases = process_review_aspect(review, pos_df, time_list, to_remove)
        price_phrases = process_review_aspect(review, pos_df, price_list, to_remove)
        portion_phrases = process_review_aspect(review, pos_df, portion_list, to_remove)
        service_phrases = process_review_aspect(review, pos_df, service_list, to_remove)
        ambience_phrases = process_review_aspect(review, pos_df, ambience_list, to_remove)

        # add aspects together
        if len(food_phrases) > 0 :
            for j in range(0, len(food_phrases)) :
                aspect_list.append('food')
                phrase_list.append(food_phrases[j])
                restaurant_code.append(df['restaurant_code'][i])
                review_title.append(df['review_title'][i])
                review_body.append(df['review_body'][i])
                account_name.append(df['account_name'][i])
                account_id.append(df['account_id'][i])
        if len(time_phrases) > 0 :
            for j in range(0, len(time_phrases)) :
                aspect_list.append('time')
                phrase_list.append(time_phrases[j])
                restaurant_code.append(df['restaurant_code'][i])
                review_title.append(df['review_title'][i])
                review_body.append(df['review_body'][i])
                account_name.append(df['account_name'][i])
                account_id.append(df['account_id'][i])
        if len(price_phrases) > 0 :
            for j in range(0, len(price_phrases)) :
                aspect_list.append('price')
                phrase_list.append(price_phrases[j])
                restaurant_code.append(df['restaurant_code'][i])
                review_title.append(df['review_title'][i])
                review_body.append(df['review_body'][i])
                account_name.append(df['account_name'][i])
                account_id.append(df['account_id'][i])
        if len(portion_phrases) > 0 :
            for j in range(0, len(portion_phrases)) :
                aspect_list.append('portion')
                phrase_list.append(portion_phrases[j])
                restaurant_code.append(df['restaurant_code'][i])
                review_title.append(df['review_title'][i])
                review_body.append(df['review_body'][i])
                account_name.append(df['account_name'][i])
                account_id.append(df['account_id'][i])
        if len(service_phrases) > 0 :
            for j in range(0, len(service_phrases)) :
                aspect_list.append('service')
                phrase_list.append(service_phrases[j])
                restaurant_code.append(df['restaurant_code'][i])
                review_title.append(df['review_title'][i])
                review_body.append(df['review_body'][i])
                account_name.append(df['account_name'][i])
                account_id.append(df['account_id'][i])
        if len(ambience_phrases) > 0 :
            for j in range(0, len(ambience_phrases)) :
                aspect_list.append('ambience')
                phrase_list.append(ambience_phrases[j])
                restaurant_code.append(df['restaurant_code'][i])
                review_title.append(df['review_title'][i])
                review_body.append(df['review_body'][i])
                account_name.append(df['account_name'][i])
                account_id.append(df['account_id'][i])

        #print(i, "out of", len(df), "done")
    
    # create df
    output = pd.DataFrame({'restaurant_code': restaurant_code, 'review_title': review_title, 'review_body': review_body, 'account_name': account_name, 'account_id': account_id, 'aspect': aspect_list, 'phrase': phrase_list})
    # remove empty phrases
    output = output.loc[output['phrase'].apply(lambda x: len(x)>0)]
    # set phrases to str
    output['phrase'] = output['phrase'].apply(lambda x: ", ".join(x))
    # remove duplicated rows
    output = output.drop_duplicates().reset_index(drop=True)

    # add phrase_no_noun and phrase_no_aspect
    # output = add_phrases(output, all_aspects)
    
    if to_save:
        # save as csv
        path_split = df_path.split("/")
        new_path = "/".join(path_split[:-1]) + "/unlabelled/unlabelled_" + path_split[-1]
        output.to_csv(new_path)
        print("saved to", new_path)
    
    return output
