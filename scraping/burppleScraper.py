import os
import requests
import datetime
import time
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
if __name__ == "__main__":
    from scrapingUtils import *
else:
    from .scrapingUtils import *

RESTAURANT_OFFSET_INCREMENT = 12
REVIEW_OFFSET_INCREMENT = 20

def scrape_neighbourhoods(browser):
    # retrieve html
    neighbourhood_soup = load_url("https://www.burpple.com/neighbourhoods/sg", browser)

    # retrieve list of neighbourhoods
    neighbourhood_refs = []
    for neighbourhood in neighbourhood_soup.findAll("a", {"class": "a--grey"}):
        neighbourhood_refs.append(neighbourhood["href"].split("/")[-1])
    
    return neighbourhood_refs

def scrape_restaurants_by_neighbourhood(neighbourhood, browser):
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
        soup = load_url(url, browser)
        
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
        'restaurant_id': ids,
        'restaurant_name': names,
        'restaurant_code': terms,
        'location': location,
        'lat': latitude,
        'long': longitude,
        'price_per_pax': price,
        'categories': categories
    })
    
    return restaurant_df

def scrape_reviews_by_restaurant(restaurant_code, browser):
    '''
    given restaurant term, scrapes all reviews from the restaurant
    '''
    offset = 0
    
    titles, bodys, dates, names, ids, levels, acc_photos, photos = [], [], [], [], [], [], [], []
    
    last_month = datetime.date.today() - datetime.timedelta(weeks=4)

    while True: 
        # retrieve url
        params = {"id": "masonry-container", "offset":offset}
        review_url = requests.get("https://www.burpple.com/" + restaurant_code + "/reviews", params=params).url

        # retrieve html
        review_soup = load_url(review_url, browser)
        
        # retrieve reviews
        reviews = review_soup.findAll("div", {"class": "food card feed-item"})

        if len(reviews) == 0: # no more reviews
            break
        
        for review in reviews:
            try: # essential information
                title = review.find("div", "food-description-title").text
                date = format_review_date(review.find("div", "card-item-set--link-subtitle").text.split("\n")[1])
                
                if date < last_month: # check for reviews that were posted in the last_month only
                    continue

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
        'review_title': titles,
        'review_body': bodys,
        'review_date': dates,
        'account_name': names,
        'account_id': ids,
        'account_level': levels,
        'account_photo': acc_photos,
        'review_photo': photos
    })
    review_df["restaurant_code"] = restaurant_code    
    review_df["scraped_date"] = datetime.date.today()
    return review_df

def generate_restaurants(restaurant_list_dir, browser):
    # retrieve neighbourhoods
    neighbourhoods = scrape_neighbourhoods(browser)

    # format neighbourhoods 
    neighbourhoods_formatted = format_search_terms(neighbourhoods)

    # retrieve and save restaurants to csv
    for n in neighbourhoods:
        # scrape restaurant
        restaurants_df = scrape_restaurants_by_neighbourhood(n, browser) 

        # save restaurant
        n_path = restaurant_list_dir + n + ".csv"
        restaurants_df.to_csv(n_path, index=False)

    # compile restaurants 
    compile(raw_dir=restaurant_list_dir, compiled_dir=restaurant_csv)

def generate_reviews(restaurant_csv, restaurant_reviews_dir, browser):
    # retrieve restaurants
    combined_restaurant_df = pd.read_csv(restaurant_csv)

    # retrieve reviews per restaurant
    for r_term in combined_restaurant_df["restaurant_code"].values:
        reviews_df = scrape_reviews_by_restaurant(r_term, browser) 

        # save restaurant
        n_path = restaurant_reviews_dir + r_term + ".csv"
        reviews_df.to_csv(n_path, index=False)
        time.sleep(np.random.uniform(3,5)) 

def scrape_details_by_restaurant(restaurant_code, browser):
    restaurant_url = "https://www.burpple.com/" + restaurant_code
    browser.get(restaurant_url)

    try:
        # Check if more button is present in description
        find_more=browser.find_element_by_xpath("//span[@class='venue-bio--more']")
        find_more.click()
    except:
        pass
    finally:
        html = browser.page_source
        restaurant_soup = BeautifulSoup(html, "html.parser")
        try:
            restaurant_description = restaurant_soup.find("div", {"class": "venue-bio"}).text
        except:
            restaurant_description = ""
    try:
        restaurant_hours = restaurant_soup.find("div", {"id": "venueInfo-details-header-item-body-hidden-openingHours"}).findAll("p")
        restaurant_hours = [x.text for x in restaurant_hours]
    except:
        restaurant_hours = []
    try:
        restaurant_address = restaurant_soup.find("div", {"class": "venue-details__item-body"}).find("p").text.strip()
    except:
        restaurant_address = ""
    try:
        restaurant_number = restaurant_soup.find("div", {"class": "venue-details__item venue-details__item--phone"}).find("p").text.strip()
        restaurant_number = "" if "This place does not have a landline" in restaurant_number else restaurant_number
    except:
        restaurant_number = ""
    try:
        restaurant_website = restaurant_soup.find("div", {"class": "venue-details__item venue-details__item--website"}).text.strip()
        restaurant_website = "" if "Know the website?" in restaurant_website else restaurant_website
    except:
        restaurant_website = ""
    try:
        restaurant_photos = restaurant_soup.findAll("div", {"class": "col featured-image"})
        restaurant_photos = [x.find("img")["src"] for x in restaurant_photos] 
    except:
        restaurant_photos = []
    return restaurant_description, restaurant_hours, restaurant_address, restaurant_number, restaurant_website, restaurant_photos

def generate_restaurant_details(restaurant_csv, browser):
    restaurant_df = pd.read_csv(restaurant_csv)
    codes, descriptions, hours, addresses, numbers, websites, photos = [], [], [], [], [], [], []
    count = 0
    for code in restaurant_df.restaurant_code:
        description, hour, address, number, website, photo = scrape_details_by_restaurant(code, browser)
        codes.append(code)
        descriptions.append(description)
        hours.append(hour)
        addresses.append(address)
        numbers.append(number)
        websites.append(website)
        photos.append(photo)
        count += 1
        if (count % 100 == 0):
            print(str(count) + " out of " + str(len(restaurant_df)) + " done")

    restaurant_description_df = pd.DataFrame({
        "restaurant_code": codes,
        "restaurant_description": descriptions,
        "restaurant_operating_hours": hours, 
        "restaurant_address": addresses, 
        "restaurant_number": numbers,
        "restaurant_website": websites,
        "restaurant_photo": photos
    })

    restaurant_detailed_df = restaurant_df.merge(restaurant_description_df, on="restaurant_code", how="left")
    return restaurant_detailed_df 

def scraping_pipeline(restaurant_csv, restaurant_detailed_csv, review_csv):
    '''
    Runs through entire scraping pipeline and saves files according to directory input
    Parameters:
    Returns: None
    '''
    print("scraping pipeline called")

    # Set required intermediate variables 
    RESTAURANT_LIST_DIR = "../data/raw/restaurant_lists/"
    RESTAURANT_REVIEWS_DIR = "./data/raw/restaurant_reviews/"
    RESTAURANT_REVIEWS_NEW = "./data/processed/new_reviews.csv"
    TO_PROCESS = ['categories'] 

    # Configure chrome options 
    chrome_options = Options()  
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    with Chrome("./scraping/utils/chromedriver", options=chrome_options) as browser:
        print("scraping restaurants")
        generate_restaurants(restaurant_list_dir=RESTAURANT_LIST_DIR, browser=browser)

        print("scraping additional restaurant details")
        restaurant_detailed_df = generate_restaurant_details(restaurant_csv=restaurant_csv, browser=browser)

        print("processing additional restaurant details")
        process_restaurant_details(restaurant_detailed_df, TO_PROCESS, restaurant_detailed_csv)

        print("scraping new reviews")
        generate_reviews(restaurant_csv=restaurant_csv, restaurant_reviews_dir=RESTAURANT_REVIEWS_DIR, browser=browser)
        compile(raw_dir=RESTAURANT_REVIEWS_DIR, compiled_dir=RESTAURANT_REVIEWS_NEW)

        print("appending new reviews to current reviews")
        get_all_reviews(review_csv, RESTAURANT_REVIEWS_NEW)

        print("scraping done")
    return None

if __name__ == "__main__": #adhoc scraping
    # instantiate directories
    RESTAURANT_LIST_DIR = "../data/raw/restaurant_lists/" 
    RESTAURANT_CSV = "../data/processed/restaurant_all.csv"
    RESTAURANT_DETAILED_CSV = "../data/processed/restaurant_all_detailed.csv"
    RESTAURANT_REVIEWS_DIR = "../data/raw/restaurant_reviews/"
    REVIEWS_CSV = "../data/processed/reviews_all.csv" 

    # configure chrome options 
    chrome_options = Options()  
    # chrome_options.add_argument("--headless") # Opens the browser up in background
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--enable-automation")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-browser-side-navigation")
    chrome_options.add_argument("--disable-gpu") 

    with Chrome("./utils/chromedriver", options=chrome_options) as browser:
        # generate restaurants
        generate_restaurants(restaurant_list_dir=RESTAURANT_LIST_DIR, browser=browser)
        # compile restaurants 
        compile(raw_dir=RESTAURANT_LIST_DIR, compiled_dir=RESTAURANT_CSV)

        # generate restaurant details
        restaurant_detailed_df = generate_restaurant_details(restaurant_csv=RESTAURANT_CSV, browser=browser)
        process_restaurant_details(restaurant_detailed_df, ['categories'], RESTAURANT_DETAILED_CSV)

        # generate reviews
        generate_reviews(restaurant_csv=RESTAURANT_CSV, restaurant_reviews_dir=RESTAURANT_REVIEWS_DIR, browser=browser)

        # compile restaurants 
        compile(raw_dir=RESTAURANT_REVIEWS_DIR, compiled_dir=REVIEWS_CSV)
