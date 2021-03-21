import numpy as np 

def score_review(probabilities):
    '''
    Returns the aggregated score on a scale of 1 to 5 stars based on the probabilities given

    Parameters:
        probabilities (List) : Contains 3 elements - [probability_pos, probability_zero, probability_neg]
    
    Returns:
        score (float) : Aggregated score to 1 decimal place
    '''
    if probabilities[1] == np.max(probabilities):
        return 3.0
    else:
        return round(3.0 + probabilities[0] * 2 - probabilities[2] * 0.2, 1)
