import os
import datetime
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup


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
        review_datetime = datetime.datetime.now() - timedelta(hours = hours_ago)
        return review_datetime.date()
    elif "d ago" in date:
        days_ago = int(date.split("d ago")[0])
        review_date = datetime.date.today() - timedelta(days = days_ago)
        return review_date
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
