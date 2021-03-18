################
### packages ###
################
import sys

#################
### functions ###
#################
sys.path.insert(1, './scraping/utils')
from scrapingUtils import load_url, format_search_terms, format_review_date, compile_csv, compile
sys.path.insert(1, './rules/utils')
from preprocessing import clean_review
from rules import get_all_aspects, get_pos, get_aspects, ranges, pos_before_after_aspect, get_sentence_indexes, get_sentences_indexes, get_sentences, process_review_aspect, add_phrases, process_reviews
from postprocessing import process_csv_lists, process_categories, one_hot_encode_emojis, clean_phrase

################
### scraping ###
################


#####################
### preprocessing ###
#####################
'''
Function Name: clean_review
Description: remove numbers, empty strings, new lines from phrases
Input: string
Output: string
'''
df['review_title'] = df['review_title'].apply(lambda x: clean_review(x))
df['review_body'] = df['review_body'].apply(lambda x: clean_review(x))
print("preprocessing done")

###################
### rule mining ###
###################
'''
Function Name: process_reviews
Description: generate aspects through rule mining
Input: dataframe, string
Output: dataframe
'''
df = process_reviews(df, df_path)
print("rule mining done")

######################
### postprocessing ###
######################
'''
Function Name: 
Description: 
Input: 
Output:
'''
print("postprocessing done")

################
### modeling ###
################
'''
Function Name: 
Description: 
Input: 
Output:
'''


print("postprocessing done")