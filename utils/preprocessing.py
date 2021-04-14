import string
from string import digits
import pandas as pd 

def clean_review(review) : 
    '''
    Removes digits, empty strings, and new lines from phrases

    Parameters:
        review (string): review text

    Output:
        review (string): processed review texttext
    '''
    # remove numbers
    remove_digits = str.maketrans('', '', digits)
    review = review.translate(remove_digits)
    # remove new lines
    review = review.replace('\n', ' ')
    return review

def preprocessing_pipeline(review_file, preprocessed_csv):
    '''
    Runs preprocessing on review_file
    '''
    # read review_df
    review_df = pd.read_csv(review_file)

    # convert any np.nans to empty string
    review_df = review_df.fillna("") 

    # keep original raw
    review_df["review_title_raw"] = review_df["review_title"]
    review_df["review_body_raw"] = review_df["review_body"]

    # clean review text
    review_df["review_title"] = review_df["review_title"].apply(lambda x: clean_review(x))
    review_df["review_body"] = review_df["review_body"].apply(lambda x: clean_review(x))

    # save preprocessed file
    review_df.to_csv(preprocessed_csv, index=False)
    
    print("PRE-PROCESSING COMPLETE")