# import packages
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px

import numpy as np
import pandas as pd
import math

# import app
from app import app



#### STYLES ##########################################################
# style arguments for header
HEADER_STYLE = {
    # "position": "sticky",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "100%",
    "height": "6rem",
    "padding": "1rem 1rem",
    "border-bottom-style": "solid",
    "border-bottom-color": "black",
    # "background-color": "#FFD1DC",
    "font-size": "12px"
}

# styles for the main content 
CONTENT_STYLE = {
    # "margin-top": "5rem",
    "padding": "2rem 1rem",
    "font-size": "12px"
}



#### HEADER ##########################################################
# retrieve unique restaurants list
RESTAURANTS_CSV_PATH = 'data/dummy_restaurants.csv'
restaurants_data = pd.read_csv(RESTAURANTS_CSV_PATH)
restaurants_list = list(restaurants_data.restaurant_name.unique())
restaurants_list.sort() # sort in alphabetical order

# retrieve unique prices
prices_list = list(restaurants_data.price_per_pax.unique())
prices_list = [x for x in prices_list if str(x) != 'nan'] # remove nan
prices_list.sort() # sort in increasing value
max_price = int(max(prices_list))
min_price = int(min(prices_list))

# retrieve unique locations
locations_list = list(restaurants_data.location.unique())
locations_list.sort() # sort in alphabetical order

# retrieve aspects list
aspects_list = []
for col in restaurants_data.columns:
    if len(col) > 14:
        if col[0:14] == 'review_rating_':
            aspect = col[14:]
            if aspect != 'overall':
                aspects_list.append(col[14:])

# category list (static)
CATEGORIES = ['Italian', 'Malay', 'Japanese', 'Chinese', 'Western', 'Korean',\
    'Thai', 'Vietnamese', 'Mexican', 'Indian', 'Local Delights', 'Desserts', \
    'Healthy', 'Cafes & Coffee', 'Halal', 'Beverages', 'Others']

# restaurant input
restaurant_input = html.Div([
    dcc.Input(
        id="restaurant-input", 
        value='',
        placeholder = "Search for a restaurant or food",
        type="text",
        style = {'width': '95%', 'font-size': '15px', 'padding': '0.3rem 0.5rem', 'margin-top': '3px', 'border-width': 'thin', 'border-color': '#CCCCCC', 'border-style': 'solid'}
    ),
], style = {'width': '20%', 'margin-left': '10px', 'margin-top': '15px','margin-right': '3px', 'font-size': '15px'}
)

# location input
location_input = html.Div([
    dcc.Dropdown(
        id = "location-input",
        placeholder = "Location",
        options = [
            {'label': location, 'value': location} for location in locations_list
        ],
        className = 'm-3',
    )
], style = {'width': '13%', 'display': 'inline-block', 'font-size': '15px'}
)

# category input
category_input = html.Div([
    dcc.Dropdown(
        id = "category-input",
        placeholder = "Category",
        options = [
            {'label': cat, 'value': cat} for cat in CATEGORIES
        ],
        className = 'm-3'
    )
], style = {'width': '13%', 'display': 'inline-block', 'font-size': '15px'}
)

# price range input
price_input = html.Div([
    html.Div(id='output-range-slider', style={'text-align': 'center'}),
    dcc.RangeSlider(
        id='price-input',
        min=0,
        max=max_price,
        step=5,
        marks = {
            int(x): str(x) for x in range(0, max_price+1, 50)
        },
        value=[0, max_price],
        allowCross=False,
    )
], style = {'width': '20%', 'display': 'inline-block', 'font-size': '15px', 'align-items': 'centre'}
)

# callback to display selected range from price slider
@app.callback(
    Output('output-range-slider', 'children'),
    [Input('price-input', 'value')]
)
def update_output(value):
    return f'Price Range: ${value[0]}-{value[1]}'

# search button
search_button = html.Div([
    dbc.Button("Search", color="dark", outline=False, block=False, id="search", className="mb-3")
    ], className = 'm-3', style = {'width': '10%', 'display': 'inline-block', 'font-size': '15px', 'margin-right': 0}
)

#### header layout ####
header = html.Div(
    [
        dbc.Row([html.H5("burpple+", className="display-4", style={"color":"#BF0A30", 'font-weight': '700', 'margin-left': 20, 'margin-right': 30, 'margin-bottom': 10}),
                restaurant_input,
                location_input,
                category_input,
                price_input,
                search_button]),
    ],
    style=HEADER_STYLE
)



#### ASPECT RATING FILTERS ##########################################################
# retrieve aspect ratings
aspects_list_all = [x for x in aspects_list]
# aspects_list_all.sort() # sort in alphabetical order
aspects_list_all.insert(0, 'overall')

# aspect input 
aspect_input = html.Div([
    dcc.Dropdown(
        id = "aspect-input",
        value="overall",
        options = [
            {'label': aspect.capitalize(), 'value': aspect} for aspect in aspects_list_all
        ],
        className = 'm-3',
        searchable=False,
        clearable=False
    )
], style = {'width': '15%', 'display': 'inline-block', 'font-size': '15px'})

# aspect order sort input
order_input = html.Div([
    dcc.Dropdown(
        id = "order-input",
        value="Descending",
        placeholder = "Descending",
        options = [
            {'label': 'Descending', 'value': 'Descending'},
            {'label': 'Ascending', 'value': 'Ascending'}
        ],
        className = 'm-3',
        searchable=False,
        clearable=False
    )
], style = {'width': '12%', 'display': 'inline-block', 'font-size': '15px'})



#### MAIN PAGE LAYOUT ##########################################################
layout = html.Div([
    header,
    dbc.Row([dbc.Col(html.H3(id='subtitle-output', style={'margin-left': '20px', 'margin-top': '20px'})), 
             aspect_input, order_input], justify='end', style={'margin-right': '20px', 'margin-top': '20px'}),
    html.Div(id='restaurants-output', style=CONTENT_STYLE)
])



#### MAIN PAGE CALLBACKS ##########################################################
def generate_restaurants_list(data, aspect_input):
    '''
    generates a container with details of a restaurant
    '''
    # retrieve restaurant details
    restaurant_name = str(data.restaurant_name)
    restaurant_code = str(data.restaurant_code)
    restaurant_description = str(data.restaurant_description)
    if len(restaurant_description) <= 1: # check for empty description
        restaurant_description = 'This restaurant does not have a description.'
    restaurant_location = data.location
    restaurant_price = data.price_per_pax
    if math.isnan(restaurant_price): # check for nan price
        restaurant_price = "-"
    restaurant_overall_rating = round(data.review_rating_overall, 2)
    
    # retrieve restaurant photo
    if data.restaurant_photo != None:
        restaurant_photos_list = data.restaurant_photo.split("'")
        for photo in restaurant_photos_list:
            if len(photo) > 10: # check for valid link
                restaurant_photo = photo
    else:
        restaurant_photo = '' # change to default image

    # retrieve restaurant categories
    restaurant_categories = ''
    for cat in CATEGORIES:
        if data[cat] == 1:
            if restaurant_categories == '':
                restaurant_categories += f'{cat}'
            else:
                restaurant_categories += f', {cat}'

    # retrieve overall score
    overall_score_display = html.H4(f'Overall: {restaurant_overall_rating}/5', style={"margin-top":"5px", "margin-left":"12px", "color": "#BF0A30"})

    if aspect_input != "overall":
        overall_score_display = html.H4(f'Overall: {restaurant_overall_rating}/5', style={"margin-top":"5px", "margin-left":"12px", "color": "black"})
    
    # retrieve aspect ratings
    aspect_table_body = []
    for review_metric in aspects_list: 
        column = "review_rating_" + review_metric.lower()
        if review_metric == aspect_input:
            if math.isnan(data[column]):
                aspect_table_body.append(html.Tr([html.Td(review_metric.capitalize(), style={"font-weight": "bold", "color":"#BF0A30"}), \
                    html.Td("-", style={"color":"#BF0A30", "font-weight": "bold"})], 
                    style={"padding": "0px"}))
            else:
                aspect_table_body.append(html.Tr([html.Td(review_metric.capitalize(), style={"font-weight": "bold", "color":"#BF0A30"}), \
                    html.Td(round(data[column], 2), style={"color":"#BF0A30", "font-weight": "bold"})],
                    style={"padding": "0px"}))
        else:
            if math.isnan(data[column]):
                aspect_table_body.append(html.Tr([html.Td(review_metric.capitalize(), style={"font-weight": "bold"}), \
                    html.Td("-")], style={"padding": "0px"}))
            else:
                aspect_table_body.append(html.Tr([html.Td(review_metric.capitalize(), style={"font-weight": "bold"}), \
                    html.Td(round(data[column], 2))], style={"padding": "0px"}))

    aspect_ratings_display = dbc.Col([overall_score_display, dbc.Table([html.Tbody(aspect_table_body)], borderless=True, style={'font-size': '14px'})], width=2)

    # return a container with the details (formatted)
    return html.Div([
        html.Br(),
        html.Div([
            dbc.Row([
                dbc.Col(html.Img(src=restaurant_photo, style={"height": "100%", "width": "100%", "padding": "0.5rem"}), width=2),
                dbc.Col([
                    dbc.Row(dcc.Link(html.H4(restaurant_name), href=f'/restaurant-{restaurant_code}', style={'color': 'black'})),
                    dbc.Row(html.H6(restaurant_location)), 
                    dbc.Row([html.I(className="fa fa-money", style={"font-size": "18px", "margin-top": "0rem", "margin-right":"0.5rem"}), 
                             html.P("$" + str(restaurant_price) + " /pax", style={'font-size': '14px'})
                    ]),
                    dbc.Row(restaurant_description, style={'font-size': '14px', 'margin-right': '5px'}),
                    html.Br(),
                    dbc.Row(f'Categories: {restaurant_categories}', style={'font-weight': 'bold', 'font-size': '14px'})
                ], width=8),
                aspect_ratings_display,
            ])
        ], style = {"margin-left": '20px', "margin-right": '20px', "padding": "1rem 1rem", "background-color": "#eaecef"}),
        html.Br()
    ])

@app.callback(
    [Output("subtitle-output", "children"),
     Output("restaurants-output", "children")],
    [Input("search", "n_clicks"),
     Input("aspect-input", "value"),
     Input("order-input", "value")],
    [State("restaurant-input", "value"),
     State("location-input", "value"),
     State("price-input", "value"),
     State("category-input", "value"),],
)



#### RENDER MAIN PAGE ##########################################################

def render_main_page(n_clicks, aspect, order, restaurant, location, price, category):    
    # read data
    restaurants_data = pd.read_csv(RESTAURANTS_CSV_PATH)
    restaurants_filter = restaurants_data.copy()

    subtitle = "Showing results for "

    # filter by restaurant name
    if restaurant != '':
        # check for occurence of restaurant string search in the restaurant_name or description column
        restaurant_lower = restaurant.lower()
        restaurants_filter = restaurants_filter.loc[restaurants_filter['restaurant_name'].str.lower().str.contains(restaurant_lower) | 
                                                    restaurants_filter['restaurant_description'].str.lower().str.contains(restaurant_lower)]
        subtitle += f' "{restaurant}" '
    # filter by location
    if location != None:
        restaurants_filter = restaurants_filter.loc[restaurants_data.location == location]
        subtitle += f' "{location}" '
    # filter by category
    if category != None:
        restaurants_filter = restaurants_filter.loc[restaurants_filter[category] == 1]
        subtitle += f' "{category} category" '
    # filter by price
    if (price[0] != 0) | (price[1] != 200): # default is [0, 200], check for deviations from default
        restaurants_filter = restaurants_filter.loc[restaurants_filter.price_per_pax <= price[1]]
        restaurants_filter = restaurants_filter.loc[restaurants_filter.price_per_pax >= price[0]]
        subtitle += f' "${price[0]}-{price[1]} per pax" '

    # sort by overall review score
    restaurants_filter = restaurants_filter.sort_values(by=['review_rating_overall'], axis=0, ascending=False)

    # check for order of sort, returns top scores first by default
    ascending_boolean = False
    if order == 'Ascending':
        ascending_boolean = True

    # check for aspect filters
    if aspect != None:
        restaurants_filter = restaurants_filter.sort_values(by=['review_rating_'+str(aspect).lower()], axis=0, ascending=ascending_boolean)

    # if user has not searched for anything
    if (n_clicks == None) | (len(restaurants_filter) == len(restaurants_data)):
        subtitle = "Top restaurants in Singapore"
        # display top 20 results
        restaurants_filter = restaurants_filter.iloc[:20]

    # generate data
    subtitle_output = [html.H2(subtitle, style={'margin-left': '25px'})]
    restaurants_output = []

    # if there are no results corresponding to all filters, return a message
    if len(restaurants_filter) == 0:
        restaurants_output.append(html.Br())
        restaurants_output.append(html.H3('There are no results corresponding to your search :(', style={'margin-left': '20px'}))

    # else generate a list of restaurants to output
    else: 
        for i in range(len(restaurants_filter)):
            output = generate_restaurants_list(restaurants_filter.iloc[i], aspect)
            restaurants_output.append(output)
    
    return (subtitle_output, restaurants_output)
