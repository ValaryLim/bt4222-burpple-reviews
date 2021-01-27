import os
import numpy as np
import pandas as pd
from utils.scrapingUtils import *

def compile(raw_dir, compiled_dir):
    combined_df = compile_csv(raw_dir)
    combined_df.to_csv(compiled_dir)

def generate_restaurants(restaurant_list_dir):
    # retrieve neighbourhoods
    neighbourhoods = scrape_neighbourhoods()

    # format neighbourhoods 
    neighbourhoods_formatted = format_search_terms(neighbourhoods)

    # retrieve and save restaurants to csv
    for n in neighbourhoods:
        # scrape restaurant
        restaurants_df = scrape_restaurants_by_neighbourhood(n) 

        # save restaurant
        n_path = restaurant_list_dir + n + ".csv"
        restaurants_df.to_csv(n_path, index=False)

def generate_reviews(restaurant_csv, restaurant_reviews_dir):
    # retrieve restaurants
    combined_restaurant_df = pd.read_csv(restaurant_csv) #[3000:6000]

    # retrieve reviews per restaurant
    for r_term in combined_restaurant_df["term"].values:
        # scrape reviews
        reviews_df = scrape_reviews_by_restaurant(r_term) 

        # save restaurant
        n_path = restaurant_reviews_dir + r_term + ".csv"
        reviews_df.to_csv(n_path, index=False)

if __name__ == "__main__":
    # instantiate directories
    RESTAURANT_LIST_DIR = "../data/raw/restaurant_lists/"
    RESTAURANT_CSV = "../data/processed/restaurant_all.csv"
    RESTAURANT_REVIEWS_DIR = "../data/raw/restaurant_reviews/"
    REVIEWS_CSV = "../data/processed/reviews_all.csv"

    # generate restaurants
    generate_restaurants(restaurant_list_dir=RESTAURANT_LIST_DIR)
    # compile restaurants 
    compile(raw_dir=RESTAURANT_LIST_DIR, compiled_dir=RESTAURANT_CSV)

    # generate reviews
    generate_reviews(restaurant_csv=RESTAURANT_CSV, restaurant_reviews_dir=RESTAURANT_REVIEWS_DIR)
    # compile restaurants 
    compile(raw_dir=RESTAURANT_REVIEWS_DIR, compiled_dir=REVIEWS_CSV)
