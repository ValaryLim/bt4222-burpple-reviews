import pandas as pd
import numpy as np
from datetime import datetime

def compute_score(prob_pos, prob_neu, prob_neg):
    '''
    Returns the aggregated score on a scale of 1 to 5 stars based on the probabilities given
    Parameters:
        prob_pos (float) : Probability of positive review
        prob_neu (float) : Probability of neutral review
        prob_neg (float) : Probability of negative review
    
    Returns:
        score (float) : Aggregated score to 2 decimal place
    '''
    probabilities = [prob_pos, prob_neu, prob_neg]
    if prob_neu == np.max(probabilities):
        return 3.0
    else:
        return round(3.0 + prob_pos * 2 - prob_neg * 0.2, 2)

def score_reviews(df):
    scores = []
    for i, row in df.iterrows():
        scores.append(compute_score(row["prob_pos"], row["prob_neu"], row["prob_neg"]))
    df["rating"] = scores
    return df

def aggregate_reviews(df):
    # split reviews by column
    food, service, price, portion, ambience, time = [], [], [], [], [], []
    for i, row in df.iterrows():
        food.append(row["rating"] if row["aspect"] == "food" else 0)
        service.append(row["rating"] if row["aspect"] == "service" else 0)
        price.append(row["rating"] if row["aspect"] == "price" else 0)
        ambience.append(row["rating"] if row["aspect"] == "ambience" else 0)
        portion.append(row["rating"] if row["aspect"] == "portion" else 0)
        time.append(row["rating"] if row["aspect"] == "time" else 0)
    df["review_rating_food"] = food
    df["review_rating_service"] = service
    df["review_rating_price"] = price
    df["review_rating_ambience"] = ambience
    df["review_rating_portion"] = portion
    df["review_rating_time"] = time

    # aggregate ratings
    aggregated_df = df.groupby(["restaurant_code", "review_title", "review_body", "review_date",\
        "account_name", "account_id", "account_level", "account_photo", "review_photo", "scraped_date"], 
        as_index=False)["review_rating_food", "review_rating_service", "review_rating_price", "review_rating_ambience",\
            "review_rating_portion", "review_rating_time"].sum()

    aggregated_df = aggregated_df.replace(0, np.nan)
    overall = aggregated_df.loc[: , "review_rating_food":"review_rating_time"].mean(axis=1, skipna=True)
    aggregated_df["review_rating_overall"] = overall

    return aggregated_df

def aggregate_restaurants(reviews_df):
    df = reviews_df.copy()
    # weight reviews by date of review
    df['date'] = df.apply(lambda x: datetime.strptime(str(x.review_date), '%d/%m/%y'), axis=1)
    df['half_years'] = df.apply(lambda x: round((datetime.today() - x.date).days/182, 1), axis=1)
    # define aspects
    aspects_list = ['overall', 'food', 'service', 'price', 'ambience', 'portion', 'time']
    # group by restaurant
    restaurant_groups = df.groupby(by=['restaurant_code'])
    aggregated_df = pd.DataFrame()
    for restaurant, restaurant_df in restaurant_groups:
        # store restaurant scores in a dictionary
        restaurant_scores = dict()
        restaurant_scores['restaurant_code'] = restaurant

        # calculate average scores weighted by review date
        for aspect in aspects_list:
            aspect_df = pd.DataFrame(restaurant_df[[f'review_rating_{aspect}', 'half_years']])
            # drop na
            aspect_df = aspect_df.dropna()
            if len(aspect_df) > 0:
                restaurant_scores[f'restaurant_rating_{aspect}'] = np.average(aspect_df[f'review_rating_{aspect}'], weights=1/aspect_df['half_years'])
            else:
                restaurant_scores[f'restaurant_rating_{aspect}'] = np.nan
        aggregated_df = aggregated_df.append(restaurant_scores, ignore_index=True)
    return aggregated_df

def scoring_pipeline(ensemble_csv, restaurant_csv, review_final_csv, restaurant_final_csv):
    ensemble_df = pd.read_csv(ensemble_csv)

    # score each aspect
    scored_reviews_df = score_reviews(ensemble_df)
    
    # aggregate scoring
    aggregated_reviews_df = aggregate_reviews(scored_reviews_df)
    aggregated_reviews_df.to_csv(review_final_csv, index=False)

    # aggregate scoring for restaurants
    restaurant_orig_df = pd.read_csv(restaurant_csv)
    aggregated_restaurants_df = aggregate_restaurants(aggregated_reviews_df)
    aggregated_restaurants_df = aggregated_restaurants_df.merge(restaurant_orig_df, on=['restaurant_code'])
    # aggregated_restaurants_df = pd.DataFrame(columns=["restaurant_code", "restaurant_id", "restaurant_name", "location", 
    #     "lat",  "long", "price_per_pax", "categories", "restaurant_description", "restaurant_operating_hours", 
    #     "restaurant_address", "restaurant_number", "restaurant_website", "restaurant_photo", 
    #     "review_rating_food", "review_rating_service", "review_rating_price", "review_rating_portion", 
    #     "review_rating_ambience", "review_rating_time", "review_rating_overall", "Italian", "Malay", "Japanese", 
    #     "Chinese", "Western", "Korean", "Thai", "Vietnamese", "Mexican", "Indian", "Local Delights", "Desserts",
    #     "Healthy", "Cafes & Coffee", "Halal", "Beverages", "Others"])
    aggregated_restaurants_df.to_csv(restaurant_final_csv, index=False)

    print("SCORING COMPLETE")