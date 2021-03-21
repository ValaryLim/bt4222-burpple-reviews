import string
from string import digits

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

def preprocessing_pipeline(review_file, save_file):
    '''
    Runs preprocessing on review_file
    '''
    review_df = pd.read_csv(review_file)
    review_df["review_title"] = review_df["review_title"].apply(lambda x: clean_review(x))
    review_df["review_body"] = review_df["review_body"].apply(lambda x: clean_review(x))
    review_df.to_csv(save_file, index=False)