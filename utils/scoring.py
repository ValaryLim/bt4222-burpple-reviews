import pandas as pd
def scoring_pipeline(ensemble_csv, restaurant_csv, review_final_csv, restaurant_final_csv):
    # score each aspect

    # aggregate scoring
    review_aggregated = pd.DataFrame(columns=["restaurant_code", "review_title", "review_body", "account_name", 
        "account_id",  "account_level", "account_photo", "review_photo", "location", "review_rating_food", 
        "review_rating_service", "review_rating_price", "review_rating_portion", "review_rating_ambience", 
        "review_rating_time", "review_rating_overall"])
    review_aggregated.to_csv(review_final_csv, index=False)

    # aggregate scoring for restaurants
    restaurant_orig_df = pd.read_csv(restaurant_csv)
    #### insert code here to aggregate review_aggregated into restaurants
    restaurant_aggregated = pd.DataFrame(columns=["restaurant_code", "restaurant_id", "restaurant_name", "location", 
        "lat",  "long", "price_per_pax", "categories", "restaurant_description", "restaurant_operating_hours", 
        "restaurant_address", "restaurant_number", "restaurant_website", "restaurant_photo", 
        "review_rating_food", "review_rating_service", "review_rating_price", "review_rating_portion", 
        "review_rating_ambience", "review_rating_time", "review_rating_overall", "Italian", "Malay", "Japanese", 
        "Chinese", "Western", "Korean", "Thai", "Vietnamese", "Mexican", "Indian", "Local Delights", "Desserts",
        "Healthy", "Cafes & Coffee", "Halal", "Beverages", "Others"])
    restaurant_aggregated.to_csv(restaurant_final_csv, index=False)