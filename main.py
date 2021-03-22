################
### packages ###
################
import utils
import scraping
import modelling

# PATH DEFINITIONS
RESTAURANT_CSV = "data/pipeline/restaurants.csv"
RESTAURANT_DETAILED_CSV = "data/pipeline/restaurants_detailed.csv"
REVIEW_CSV = "data/pipeline/reviews.csv"
PREPROCESSED_CSV = "data/pipeline/reviews_preprocessed.csv"
RULE_MINED_CSV = "data/pipeline/rule_mined.csv"
POSTPROCESSED_CSV = "data/pipeline/reviews_postprocessed.csv"
BASELINE_CSV = "data/pipeline/baseline_prediction.csv"
ENSEMBLE_CSV = "data/pipeline/ensemble_prediction.csv"
REVIEW_FINAL = "data/pipeline/reviews_final.csv"
RESTAURANT_FINAL = "data/pipeline/restaurants_final.csv"

if __name__ == "__main__":
    # scrape
    # scraping.scraping_pipeline(RESTAURANT_CSV, RESTAURANT_DETAILED_CSV, REVIEW_CSV) # SEAN 
    
    # preprocessing
    utils.preprocessing_pipeline(REVIEW_CSV, PREPROCESSED_CSV)

    # rule mining
    # utils.rule_mining_pipeline(PREPROCESSED_CSV, RULE_MINED_CSV) 

    # postprocessing
    utils.postprocessing_pipeline(RULE_MINED_CSV, POSTPROCESSED_CSV) 

    # modelling
    modelling.base_modelling_pipeline(POSTPROCESSED_CSV, BASELINE_CSV) # SEAN, YJ, XM
    # modelling.meta_modelling_pipeline(PREDICTIONS_CSV, ENSEMBLE_CSV) # XM

    # scoring
    utils.scoring_pipeline(ENSEMBLE_CSV, RESTAURANT_DETAILED_CSV, REVIEW_FINAL, RESTAURANT_FINAL)

    # ##### dashboard to read data from REVIEW_FINAL, RESTAURANT_FINAL
