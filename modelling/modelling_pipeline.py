import pickle
import pandas as pd

# instantiate models
LOGREG_VECT = "modelling/saved_models/model_logreg.pkl"
LOGREG_MODEL = "modelling/saved_models/model_logreg.pkl"
META_MODEL = "modelling/saved_models/model_meta.pkl"

def base_modelling_pipeline(processed_csv, prediction_csv):
    '''
    '''
    # READ PROCESSED DATA
    processed_df = pd.read_csv(processed_csv)

    # LOGISTIC REGRESSION PREDICTION
    lr_vectorizer = pickle.load(open(LOGREG_VECT, "rb"))
    lr_model = pickle.load(open(LOGREG_MODEL, "rb"))
    lr_transformed_text = lr_vectorizer.transform(processed_df.phrase_stem_emoticon_generic)
    lr_predictions = lr_model.predict_proba(lr_transformed_text)
    processed_df["logreg_prob_pos"] = lr_predictions[:, 2]
    processed_df["logreg_prob_neg"] = lr_predictions[:, 0]

    # SUPPORT VECTOR MACHINE PREDICTION


    # NAIVE BAYEs PREDICTION


    # RANDOM FOREST PREDICTION


    # FASTTEXT PREDICTION


    # BERT PREDICTION
    
    processed_df.to_csv(prediction_csv)

def ensemble_modelling_pipeline(prediction_csv, ensemble_file):
    '''
    Retrieves predictions for each baseline model and outputs final prediction using meta model

    Parameters:
        prediction_dir (str): directory containing all predictions from baseline model
        ensemble_file (str):  filename to save ensemble predictions in
    Return: none
    '''
    # read baseline model predictions 
    predictions_df = pd.read_csv(prediction_csv)
    
    # generate ensemble predictions
    meta_model = pickle.load(open(META_MODEL, "rb"))
    # i want the predictions in this format!
    ensemble_predictions = pd.DataFrame(columns=["restaurant-code", "review_title", "review_body", "account_name", 
        "account_id",  "account_level", "account_photo", "review_photo", "location", "aspect", 
        "prob_pos", "prob_neu", "prob_neg"]) 

    # save ensemble predictions
    ensemble_predictions.to_csv(ensemble_file, index=False)