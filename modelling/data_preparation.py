# prepares train and test datasets
import pandas as pd
import numpy as np

TRAIN_SET = 300
VALIDATION_SET = 100
TEST_SET = 100
MIN_REVIEWS = 5

# set seed
np.random.seed(12345)

# load all reviews and restaurants
reviews_df = pd.read_csv("../data/processed/reviews_all.csv")
restaurant_df = pd.read_csv("../data/processed/restaurant_all_detailed.csv")

# left join on reviews
reviews_df = reviews_df.merge(restaurant_df[["restaurant_code", "location"]], on="restaurant_code", how="left")

# filter only restaurants with at least 5 unique reviews
reviews_grouped_df = reviews_df.groupby('restaurant_code')
reviews_filtered_df = reviews_grouped_df.filter(lambda x: x["review_body"].count() > MIN_REVIEWS)

# randomly generate restaurant lists
all_restaurants = list(reviews_filtered_df.restaurant_code.unique())
test_restaurants = list(np.random.choice(all_restaurants, TEST_SET, replace=False))
nontest_restaurants = list(np.setdiff1d(all_restaurants, test_restaurants))
train_validation_restaurants = list(np.random.choice(nontest_restaurants, TRAIN_SET + VALIDATION_SET, replace=False))
train_restaurants = list(np.random.choice(train_validation_restaurants, TRAIN_SET, replace=False))
validation_restaurants = list(np.setdiff1d(train_validation_restaurants, train_restaurants))

# filter the restaurants into datasets
test_reviews_mask = [x in test_restaurants for x in reviews_filtered_df["restaurant_code"]]
test_reviews_df = reviews_filtered_df[test_reviews_mask]

nontest_reviews_mask = [x not in test_restaurants for x in reviews_df["restaurant_code"]]
nontest_reviews_df = reviews_df[nontest_reviews_mask]

nontest_reviews_filtered_mask = [x not in test_restaurants for x in reviews_filtered_df["restaurant_code"]]
nontest_reviews_filtered_df = reviews_filtered_df[nontest_reviews_filtered_mask]

train_validation_reviews_mask = [x in train_validation_restaurants for x in reviews_filtered_df["restaurant_code"]]
train_validation_reviews_df = reviews_filtered_df[train_validation_reviews_mask]

train_reviews_mask = [x in train_restaurants for x in reviews_filtered_df["restaurant_code"]]
train_reviews_df = reviews_filtered_df[train_reviews_mask]

validation_reviews_mask = [x in validation_restaurants for x in reviews_filtered_df["restaurant_code"]]
validation_reviews_df = reviews_filtered_df[validation_reviews_mask]

# selecting 5 restaurants from each dataset
test_reviews_subset_df = test_reviews_df.groupby('restaurant_code').apply(lambda x: x.sample(5))
test_reviews_subset_df = test_reviews_subset_df.reset_index(drop=True)

train_reviews_subset_df = train_reviews_df.groupby('restaurant_code').apply(lambda x: x.sample(5))
train_reviews_subset_df = train_reviews_subset_df.reset_index(drop=True)

validation_reviews_subset_df = validation_reviews_df.groupby('restaurant_code').apply(lambda x: x.sample(5))
validation_reviews_subset_df = validation_reviews_subset_df.reset_index(drop=True)

train_validation_reviews_subset_df = train_reviews_subset_df.copy()
train_validation_reviews_subset_df.append(validation_reviews_subset_df, ignore_index=True)

# save all reviews datasets to dataframe
test_reviews_df.to_csv("../data/train_test/reviews_test.csv", index=False)
nontest_reviews_df.to_csv("../data/train_test/reviews_nontest.csv", index=False)
validation_reviews_df.to_csv("../data/train_test/reviews_validation.csv", index=False)
train_reviews_df.to_csv("../data/train_test/reviews_train.csv", index=False)
train_validation_reviews_df.to_csv("../data/train_test/reviews_trainvalidation.csv", index=False)

# save filtered reviews to dataframe
test_reviews_subset_df.to_csv("../data/train_test/reviews_test_subset.csv", index=False)
train_reviews_subset_df.to_csv("../data/train_test/reviews_train_subset.csv", index=False)
validation_reviews_subset_df.to_csv("../data/train_test/reviews_validation_subset.csv", index=False)
train_validation_reviews_subset_df.to_csv("../data/train_test/reviews_trainvalidation_subset.csv", index=False)