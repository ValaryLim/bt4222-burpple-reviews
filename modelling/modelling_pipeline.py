import pickle
import pandas as pd
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# instantiate models
LOGREG_VECT = "saved_models/model_logreg_vectorizer.pkl"
LOGREG_MODEL = "saved_models/model_logreg.pkl"
SVM_VECT = "saved_models/model_SVM_vectorizer.pkl"
SVM_MODEL = "saved_models/model_SVM.pkl"
NB_VECT = "saved_models/model_NB_vectorizer.pkl"
NB_MODEL = "saved_models/model_NB.pkl"
RF_VECT = "saved_models/model_RF_vectorizer.pkl"
RF_MODEL = "saved_models/model_RF.pkl"
META_MODEL = "saved_models/model_meta.pkl"

def base_modelling_pipeline(processed_csv, prediction_csv):
    '''
    Reads processed data and outputs csv of predictions for each model
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
    svm_vectorizer = pickle.load(open(SVM_VECT, "rb"))
    svm_model = pickle.load(open(SVM_MODEL, "rb"))
    svm_transformed_text = svm_vectorizer.transform(processed_df.phrase_emoticon_generic)
    svm_predictions = svm_model.predict_proba(svm_transformed_text)
    processed_df["SVM_prob_pos"] = svm_predictions[:, 2]
    processed_df["SVM_prob_neg"] = svm_predictions[:, 0]

    # NAIVE BAYES PREDICTION
    nb_vectorizer = pickle.load(open(NB_VECT, "rb"))
    nb_model = pickle.load(open(NB_MODEL, "rb"))
    nb_transformed_text = nb_vectorizer.transform(processed_df.phrase_stem_emoticon_generic)
    nb_predictions = nb_model.predict_proba(nb_transformed_text)
    processed_df["NB_prob_pos"] = nb_predictions[:, 2]
    processed_df["NB_prob_neg"] = nb_predictions[:, 0]

    # RANDOM FOREST PREDICTION
    rf_vectorizer = pickle.load(open(RF_VECT, "rb"))
    rf_model = pickle.load(open(RF_MODEL, "rb"))
    rf_transformed_text = rf_vectorizer.transform(processed_df.phrase_stem_emoticon_generic)
    rf_predictions = rf_model.predict_proba(rf_transformed_text)
    processed_df["RF_prob_pos"] = rf_predictions[:, 2]
    processed_df["RF_prob_neg"] = rf_predictions[:, 0]

    # FASTTEXT PREDICTION


    # BERT PREDICTION
    
    # VADER PREDICTION
    processed_df[["VADER_prob_pos","VADER_prob_neg"]] = load_VADER_model(processed_df)
    
    
    processed_df.to_csv(prediction_csv, index=False)
    print("BASELINE PREDICTIONS COMPLETE")

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

    #fit model
    predictions_df[["prob_neg","prob_neu","prob_pos"]] = meta_model.predict_proba(predictions_df[['bert_prob_pos', 'bert_prob_neg', 'fasttext_prob_pos',
       'fasttext_prob_neg', 'logreg_prob_pos', 'logreg_prob_neg',
       'NB_prob_pos', 'NB_prob_neg', 'RF_prob_pos', 'RF_prob_neg',
       'SVM_prob_pos', 'SVM_prob_neg', 'VADER_prob_pos', 'VADER_prob_neg',
       'label']])[:, 0:2]
    


    # i want the predictions in this format!
    ensemble_predictions = pd.DataFrame(data=predictions_df,columns=["restaurant-code", "review_title", "review_body", "account_name", 
        "account_id",  "account_level", "account_photo", "review_photo", "location", "aspect", 
        "prob_pos", "prob_neu", "prob_neg"]) 
    
    
    # save ensemble predictions
    ensemble_predictions.to_csv(ensemble_file, index=False)
    print("ENSEMBLE PREDICTIONS COMPLETE")
    
    
def load_VADER_model(df):
    """
    This function loads the VADER model whose dictionary has been updated.
    
    Parameters:
        df(pd.DataFrame) : data to be predicted
    
    Return : dataframe with 2 columns containing prediction probability
       
    """

    sid = SentimentIntensityAnalyzer()
    
    new_food = {
        "tender" : 2,
        "fresh" : 2,
        "soggy" : -2,
        "jelat" : -2,
        "oily" : -2,
        "overcooked" :-2,
        "dry" : -2,
        "disappointed" : -2,
        "cravings satisfied" : 2,
        "crispy" : 2,
        "sinful" : 2,
        "tough" : -2,
        "cold" : -2
    }

    new_time = {
        "long queue" : -2,
        "queue" : -2,
        "wait" : -2,
        "slow" : -2,
        "crowd" : -2,
        "crowded" : -2,
        "no waiting time" : 2,
        "fast" : 2,
    }

    new_price = {
        "pricey" : -2,
        "expensive" : -2,
        "cheap" : 2,
        "worth" : 2,
        "overpriced" : -2,
        "not worth" : -2,
        "value for money" : 2,
        "reasonable" : 2,
        "reasonably" : 2,
        "affordable" : 2,
        "steal" : 2   
    }

    new_portion = {
        "small" : -2,
        "large" : 2,
        "generous" : 2,
        "sufficient" : 1,
        "enough" : 1
    }

    sid.lexicon.update(new_food)
    sid.lexicon.update(new_time)
    sid.lexicon.update(new_price)
    sid.lexicon.update(new_portion)

    dataframe = df.copy()
    dataframe["polarity_scores"] = dataframe.phrase_emoticon_generic.map(lambda phrase : sid.polarity_scores(phrase))
    dataframe["pos"] = dataframe["polarity_scores"].map(lambda score_dict : score_dict["pos"])
    dataframe["neg"] = dataframe["polarity_scores"].map(lambda score_dict : score_dict["neg"])

    # Create Dataframe and output
    df = pd.DataFrame(data=dataframe[["neg","pos","label"]].values, columns = [model_name+'_prob_neg', model_name+'_prob_pos',"label"])
    # df.drop(columns= [model_name+'_prob_neu'])
    ordered_cols = [model_name+'_prob_pos',model_name+'_prob_neg',"label"]
    df = df[ordered_cols]
    
    return df

