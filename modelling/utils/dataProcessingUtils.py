import ast

CATEGORY_CUISINE_MAPPING = {
    'Burgers': ['Western'], 
    'Waffles': ['Cafes & Coffee'] , 
    'Healthier Choice': ['Healthy'], 
    'Mookata': ['Thai'], 
    'Nasi Lemak': ['Malay'],  
    'Char Kway Teow': ['Local Delights'], 
    'Vegan': ['Healthy'], 
    'Craft Beer': ['Beverages'], 
    'Kopitiam': ['Local Delights'],  
    'Chirashi': ['Japanese'], 
    'Sandwiches': ['Cafes & Coffee'], 
    'Ice Cream & Yoghurt': ['Desserts'], 
    'Chicken Rice': ['Local Delights'], 
    'Sushi': ['Japanese'], 
    'Zi Char': ['Chinese', 'Local Delights'], 
    'Fruit Tea': ['Beverages'],  
    'Cakes': ['Desserts', 'Cafes & Coffee'],
    'Bubble Tea': ['Beverages'], 
    'Teppanyaki': ['Japanese'], 
    'Korean Desserts': ['Korean', 'Desserts'], 
    'Korean BBQ': ['Korean', 'Desserts'],
    'Bak Kut Teh': ['Local Delights', 'Chinese'], 
    'Hot Pot': ['Chinese'], 
    'Vegetarian': ['Healthy'],  
    'Pasta': ['Italian'], 
    'Ramen': ['Japanese'], 
    'Pizza': ['Italian'], 
    'Steak': ['Western'], 
    'Korean Fried Chicken': ['Korean'], 
    'Dim Sum': ['Chinese'], 
    'Salads': ['Healthy'], 
    'Argentinian': ['Others'], 
    'Turkish': ['Others', 'Halal'],
    'Greek': ['Others'], 
    'Russian': ['Others'],
    'European': ['Western', 'Others'],
    'Brazilian': ['Others'],
    'Fast Food': ['Western'],
    'Bread & Pastries': ['Cafes & Coffee'],
    'Breakfast & Brunch': ['Cafes & Coffee'],
    'Peranakan': ['Local Delights'],
    'Spanish': ['Others'],
    'Bars': ['Beverages', 'Others'],
    'Taiwanese': ['Chinese'],
    'Mediterranean': ['Others'],
    'Middle Eastern': ['Others'],
    'French': ['Others'],
    'Indonesian': ['Others'],
    'Hawker Food': ['Local Delights']
}

FILTERED_CATEGORIES = ['Italian', 'Malay', 'Japanese', 'Chinese', 'Western', 'Korean', 'Thai', 'Vietnamese', \
            'Mexican', 'Indian', 'Local Delights', 'Desserts', 'Healthy', 'Cafes & Coffee', 'Halal']

ADDITIONAL_CATEGORIES = ['Beverages', 'Others']


def process_csv_lists(df, columns):
    for col in columns:
        df[col] = df[col].apply(lambda x: ast.literal_eval(x))
    return df

def process_categories(df, category_column="categories"):
    for category in FILTERED_CATEGORIES:
        df[category] = [1 if category in x else 0 for x in df[category_column]]
    for category in ADDITIONAL_CATEGORIES:
        df[category] = 0
    
    for burpple_category in CATEGORY_CUISINE_MAPPING.keys():
        for actual_category in CATEGORY_CUISINE_MAPPING[burpple_category]:
            # get values to update new row
            updated_row = df[actual_category] # get current values in category
            for i, row in df.iterrows():
                if burpple_category in row[category_column]:
                    updated_row[i] = 1 # label as part of that category

            # update new row
            df[actual_category] = updated_row
    return df