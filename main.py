################
### packages ###
################
import utils
import scraping

# PATH DEFINITIONS
SCRAPED_DATA = "data/pipeline/scraped/"
PREPROCESSED_DATA = "data/pipeline/preprocesed/"
RULE_MINING_DATA = "data/pipeline/rule_mining/"
POSTPROCESSED_DATA = "data/pipeline/postprocessed/"
MODEL_PREDICTIONS_DATA = "data/pipeline/model_predictions/"
SCORING_DATA = "data/pipeline/scored/"

if __name__ == "__main__":
    # scrape
    scraping.scraping_pipeline("hello")
    
    # preprocessing
    utils.preprocessing_pipeline(review_file, save_file)

    # RULE MINING

    # postprocessing
    utils.postprocessing_pipeline()

    # MODELLING
    modelling.modelling_pipeline()

    # SCORING
    utils.scoring_pipeline()

    # DASHBOARD DATA UPDATE
