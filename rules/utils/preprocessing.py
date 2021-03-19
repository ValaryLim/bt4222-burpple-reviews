import string
from string import digits

'''
description: remove numbers, empty strings, new lines from phrases
input: string
output: string
'''
def clean_review(review) : 
    # remove numbers
    remove_digits = str.maketrans('', '', digits)
    review = review.translate(remove_digits)
    # remove new lines
    review = review.replace('\n', ' ')
    return review
