import os
import datetime
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

RESTAURANT_OFFSET_INCREMENT = 12
REVIEW_OFFSET_INCREMENT = 20

def load_url(url):
    ''' 
    Loads html of any url in burpple and returns BeautifulSoup object
    ''' 
    chrome_options = Options()  
    chrome_options.add_argument("--headless") # Opens the browser up in background

    with Chrome("./utils/chromedriver", options=chrome_options) as browser:
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

def scrape_neighbourhoods():
    # retrieve html
    neighbourhood_soup = load_url("https://www.burpple.com/neighbourhoods/sg")

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
        soup = load_url(url)
        
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
        review_soup = load_url(review_url)
        
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