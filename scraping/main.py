import os
import utils
import requests
import numpy as np
import pandas as pd

RESTAURANT_OFFSET_INCREMENT = 12
REVIEW_OFFSET_INCREMENT = 20

def scrape_neighbourhoods():
    # retrieve html
    neighbourhood_soup = utils.load_url("https://www.burpple.com/neighbourhoods/sg")

    # retrieve list of neighbourhoods
    neighbourhood_refs = []
    for neighbourhood in neighbourhood_soup.findAll("a", {"class": "a--grey"}):
        neighbourhood_refs.append(neighbourhood["href"].split("/")[-1])
    
    return neighbourhood_refs

def scrape_restaurants_by_neighbourhood(neighbourhood):
    '''
    takes in a neighbourhood term and returns dataframe of all restaurants in the neighbourhood
    '''
    # create query
    offset = 0
    
    ids, names, terms, location, latitude, longitude, price, categories = [], [], [], [], [], [], [], []

    while True:
        # construct restaurant url
        params = {"offset":offset, "open_now":"false", "price_from":0, "price_to":1000, "q":neighbourhood}
        url = requests.get("https://www.burpple.com/search/sg", params=params).url
        
        # retrieve html
        soup = utils.load_url(url)
        
        # retrieve venues
        venues = soup.findAll("div", {"class": "searchVenue card feed-item"})
        
        if len(venues) == 0: # stop scraping once there are no more venues
            break
            
        for venue in venues:
            try: 
                # basic requirements to scrape
                rid = int(venue.find("button", {"class": "btn--wishBtn"})["data-venue-id"])
                name = venue.find("button", {"class": "btn--wishBtn"})["data-venue-name"]
                term = venue.find("a")["href"].split("/")[1].split("?")[0]
                
                # all scrappable, add to list
                ids.append(rid)
                names.append(name)
                terms.append(term)
            except: 
                # does not meet basic requirements, do not scrape restaurant
                continue
            
            # optional items
            try: 
                location.append(venue.find("span", {"class": "searchVenue-header-locationDistancePrice-location"}).text)
            except:
                location.append("") # filler
            
            try:
                lat = float(venue.find("span", {"class": "searchVenue-header-locationDistancePrice-distance"})["data-latitude"])
                long = float(venue.find("span", {"class": "searchVenue-header-locationDistancePrice-distance"})["data-longitude"])
                latitude.append(lat)
                longitude.append(long)
            except:
                latitute.append(None)
                longitude.append(None)
            
            try:
                price.append(int(venue.find("span", {"class": "searchVenue-header-locationDistancePrice-price"}).text.split("$")[1].split("/")[0]))
            except:
                price.append(None)
                
            try:
                categories.append(venue.find("span", {"class": "searchVenue-header-categories"}).text.split(", "))
            except:
                categories.append([])
        
        offset += RESTAURANT_OFFSET_INCREMENT
    
    # combine to dataframe
    restaurant_df = pd.DataFrame({
        'id': ids,
        'name': names,
        'term': terms,
        'location': location,
        'lat': latitude,
        'long': longitude,
        'price_per_pax': price,
        'categories': categories
    })
    
    return restaurant_df

def scrape_reviews_by_restaurant(restaurant_term):
    '''
    given restaurant term, scrapes all reviews from the restaurant
    '''
    offset = 0
    
    titles, bodys, dates, names, ids, levels, acc_photos, photos = [], [], [], [], [], [], [], []
    
    while True: 
        # retrieve url
        params = {"id": "masonry-container", "offset":offset}
        review_url = requests.get("https://www.burpple.com/" + restaurant_term + "/reviews", params=params).url
        
        # retrieve html
        review_soup = utils.load_url(review_url)
        
        # retrieve reviews
        reviews = review_soup.findAll("div", {"class": "food card feed-item"})
        
        if len(reviews) == 0: # no more reviews
            break
        
        for review in reviews:
            try: # essential information
                title = review.find("div", "food-description-title").text
                date = format_review_date(review.find("div", "card-item-set--link-subtitle").text.split("\n")[1])
                
                # review details
                account_name = review.find("div", "card-item-set--link-title").text.split("\n")[1]
                account_id = review.find("div", "card-item-set--link-title").a["href"].split("/")[1]
            except:
                continue
            
            try:
                body = review.find("div", "food-description-body").text
            except: 
                body = ""
                
            try: 
                account_level = review.find("div", "card-item-set--link-main").a.text
            except:
                account_level = ""
            
            try:
                account_photo = review.find("img", {"class": "card-item-set--link-image-profile"})["src"]
            except: 
                account_photo = None
                
            try:
                photo = review.find("div", {"class": "food-image"}).img["src"]
            except:
                photo = None
            
            # add to lists
            titles.append(title)
            bodys.append(body)
            dates.append(date)
            names.append(account_name)
            ids.append(account_id)
            levels.append(account_level)
            acc_photos.append(account_photo)
            photos.append(photo)
                
        offset += REVIEW_OFFSET_INCREMENT # update offset
    
    # combine to dataframe
    review_df = pd.DataFrame({
        'title': titles,
        'body': bodys,
        'date': dates,
        'account_name': names,
        'account_id': ids,
        'account_level': levels,
        'account_photo': acc_photos,
        'review_photo': photos
    })
    
    review_df["term"] = restaurant_term
    
    return review_df

def generate_restaurants(restaurant_list_dir):
    # retrieve neighbourhoods
    neighbourhoods = scrape_neighbourhoods()

    # format neighbourhoods 
    neighbourhoods_formatted = utils.format_search_terms(neighbourhoods)

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
    utils.compile(raw_dir=RESTAURANT_LIST_DIR, compiled_dir=RESTAURANT_CSV)

    # generate reviews
    generate_reviews(restaurant_csv=RESTAURANT_CSV, restaurant_reviews_dir=RESTAURANT_REVIEWS_DIR)
    # compile restaurants 
    utils.compile(raw_dir=RESTAURANT_REVIEWS_DIR, compiled_dir=REVIEWS_CSV)
