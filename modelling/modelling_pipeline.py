import pickle
import pandas as pd
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import fasttext
from scipy.special import softmax
from simpletransformers.classification import ClassificationModel, ClassificationArgs

# instantiate models
LOGREG_VECT = "modelling/saved_models/model_logreg_vectorizer.pkl"
LOGREG_MODEL = "modelling/saved_models/model_logreg.pkl"
SVM_VECT = "modelling/saved_models/model_SVM_vectorizer.pkl"
SVM_MODEL = "modelling/saved_models/model_SVM.pkl"
NB_VECT = "modelling/saved_models/model_NB_vectorizer.pkl"
NB_MODEL = "modelling/saved_models/model_NB.pkl"
RF_VECT = "modelling/saved_models/model_RF_vectorizer.pkl"
RF_MODEL = "modelling/saved_models/model_RF.pkl"
FASTTEXT_MODEL = "modelling/saved_models/model_fasttext.bin"
BERT_MODEL = "modelling/saved_models/bert/model_bert_final"
META_MODEL = "modelling/saved_models/model_meta.pkl"

def fasttext_get_index(lst, tag):
    '''
    Helper function to make fasttext predictions
    '''
    for i in range(len(lst)):
        if lst[i][-3:] == tag:
            return i

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

    print("LR, SVM, NB, RF predictions complete")

    # FASTTEXT PREDICTION
    fasttext_model = fasttext.load_model(FASTTEXT_MODEL)
    fasttext_df = processed_df.copy()
    # get raw output (('__label__pos', '__label__zer', '__label__neg'), array([0.74627936, 0.19218659, 0.06156404]))
    fasttext_df['raw_output'] = fasttext_df.apply(lambda x: fasttext_model.predict(x['phrase_stem'].replace("\n", ""), k=-1), axis=1)
    # get raw prob [0.74627936, 0.19218659, 0.06156404]
    fasttext_df['raw_prob'] = fasttext_df.apply(lambda x: list(x.raw_output[1]), axis=1)
    # get pos and neg index
    fasttext_df['pos_index'] = fasttext_df.apply(lambda x: fasttext_get_index(list(x.raw_output[0]), 'pos'), axis=1)
    fasttext_df['neg_index'] = fasttext_df.apply(lambda x: fasttext_get_index(list(x.raw_output[0]), 'neg'), axis=1)
    # get prob_pos and prob_neg
    fasttext_df['fasttext_prob_pos'] = fasttext_df.apply(lambda x: x.raw_prob[x.pos_index], axis=1)
    fasttext_df['fasttext_prob_neg'] = fasttext_df.apply(lambda x: x.raw_prob[x.neg_index], axis=1)
    # add to processed_df
    processed_df["fasttext_prob_pos"] = fasttext_df['fasttext_prob_pos']
    processed_df["fasttext_prob_neg"] = fasttext_df['fasttext_prob_neg']

    print("Fasttext predictions complete")

    # BERT PREDICTION
    bert_model_args = ClassificationArgs(num_train_epochs=2, learning_rate=5e-5)
    bert_model = ClassificationModel(model_type = 'bert', \
                                     model_name = BERT_MODEL, \
                                     args = bert_model_args, use_cuda = False)
    bert_pred, bert_raw_outputs = bert_model.predict(processed_df.phrase)
    # convert raw output to probabilities
    bert_probabilities = softmax(bert_raw_outputs, axis=1)
    processed_df['bert_prob_pos'] = bert_probabilities[:, 1]
    processed_df['bert_prob_neg'] = bert_probabilities[:, 2]

    print("BERT predictions complete")
    
    # @ XM comment everything above this line to run vader predictions by calling main.py 
    # processed_df.to_csv("data/pipeline/baseline_prediction_checkpoint.csv", index=False)

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

    # fit model
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

