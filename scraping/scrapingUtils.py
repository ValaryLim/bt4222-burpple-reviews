import os
import ast
import datetime
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

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

def process_restaurant_details(df, columns_to_process, final_path):
    df = process_csv_lists(df, columns_to_process)
    df = process_categories(df, category_column='categories')
    df.to_csv(final_path, index=False)

def get_all_reviews(current_reviews_path, new_reviews_path):
    current_reviews=pd.read_csv(current_reviews_path)
    new_reviews=pd.read_csv(new_reviews_path)
    all_reviews=pd.concat([current_reviews, new_reviews])

    # Refresh existing csv 
    all_reviews.to_csv(current_reviews_path, index=False)

def load_url(url, browser):
    ''' 
    Loads html of any url in burpple and returns BeautifulSoup object
    '''
    browser.get(url)
    html = browser.page_source
    soup = BeautifulSoup(html, "html.parser")
    return soup

def format_search_terms(terms):
    return ["+".join(term.split("-")) for term in terms]

def format_review_date(date):
    date = date.strip()
    if "h ago" in date:
        hours_ago = int(date.split("h ago")[0])
        review_datetime = datetime.datetime.now() - datetime.timedelta(hours = hours_ago)
        return review_datetime.date()
    elif "d ago" in date:
        days_ago = int(date.split("d ago")[0])
        review_date = datetime.date.today() - datetime.timedelta(days = days_ago)
        return review_date
    elif "at" in date: # "Feb 3 at 8:36pm"
        review_date_str = date.split("at")[0] + '2021'
        review_date = datetime.datetime.strptime(review_date_str, "%b %d %Y")
        return review_date.date()
    else: # "Dec 3, 2020"
        review_datetime = datetime.datetime.strptime(date, "%b %d, %Y")
        return review_datetime.date()

def compile_csv(dir):
    # retrieve all files
    files = os.listdir(dir)
    
    # instantiate dataframe
    combined_df = pd.DataFrame()
    
    # append dataframes
    for file in files:
        combined_df = combined_df.append(pd.read_csv(dir + file))
    
    # drop duplicates
    combined_df = combined_df.drop_duplicates()
    
    return combined_df

def compile(raw_dir, compiled_dir):
    combined_df = compile_csv(raw_dir)
    combined_df.to_csv(compiled_dir, index=False)
