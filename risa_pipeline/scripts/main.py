################
### packages ###
################
import utils

################
### scraping ###
################


#####################
### preprocessing ###
#####################
'''
Function Name: clean_review
Description: remove numbers, empty strings, new lines from phrases
Input: string
Output: string
'''
df['review_title'] = df['review_title'].apply(lambda x: clean_review(x))
df['review_body'] = df['review_body'].apply(lambda x: clean_review(x))
print("preprocessing done")

###################
### rule mining ###
###################
'''
Function Name: process_reviews
Description: generate aspects through rule mining
Input: dataframe, string
Output: dataframe
'''
df = process_reviews(df, df_path)
print("rule mining done")

######################
### postprocessing ###
######################
'''
Function Name: 
Description: 
Input: 
Output:
'''
print("postprocessing done")

########################
### emoji processing ###
########################
'''
Function Name: 
Description: 
Input: 
Output:
'''

print("emoji processing done")

################
### modeling ###
################
'''
Function Name: 
Description: 
Input: 
Output:
'''


print("modeling done")
