# import packages
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px

# import app
from app import app

import pandas as pd



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
    "background-color": "#FFD1DC",
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
restaurants_data = pd.read_csv('data/dummy_restaurants.csv')
restaurants_list = list(restaurants_data.restaurant_name.unique())
restaurants_list.sort() # sort in alphabetical order

# retrieve unique prices
prices_list = list(restaurants_data.price_per_pax.unique())
prices_list.sort() # sort in increasing value

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

# restaurant input
restaurant_input = html.Div([
    dcc.Dropdown(
        id = "restaurant-input",
        placeholder = "Search for a restaurant",
        options = [
            {'label': restaurant, 'value': restaurant} for restaurant in restaurants_list
        ],
        className = 'm-3',
    ),
], style = {'width': '30%', 'display': 'inline-block', 'font-size': '15px'}
)

# price range input
price_input = html.Div([
    dcc.Dropdown(
        id = "price-input",
        placeholder = "Select a price range",
        options = [
            {'label': price, 'value': price} for price in prices_list if str(price) != 'nan'
        ],
        className = 'm-3',
    )
], style = {'width': '15%', 'display': 'inline-block', 'font-size': '15px'}
)

# location input
location_input = html.Div([
    dcc.Dropdown(
        id = "location-input",
        placeholder = "Select a location",
        options = [
            {'label': location, 'value': location} for location in locations_list
        ],
        className = 'm-3',
    )
], style = {'width': '15%', 'display': 'inline-block', 'font-size': '15px'}
)

# cuisine input


# search button
search_button = html.Div([
    dbc.Button("Search", color="dark", block=False, id="search", className="mb-3")
    ], className = 'm-3', style = {'width': '10%', 'display': 'inline-block', 'font-size': '15px'}
)

#### header layout ####
header = html.Div(
    [
        dbc.Row([html.H5("burpple+", className="display-4", style={'font-weight': '500', 'margin-left': 20}),
                restaurant_input,
                price_input,
                location_input,
                search_button]),
    ],
    style=HEADER_STYLE
)



#### SEARCH RESTAURANTS LAYOUT ##########################################################
layout = html.Div([
    header,
    html.Div(id='restaurants-output', style=CONTENT_STYLE)
])



#### SEARCH RESTAURANTS CALLBACKS ##########################################################

def generate_restaurants(data):
    '''
    generates a container with details of a restaurant
    '''
    # retrieve restaurant details
    restaurant_name = str(data.restaurant_name)
    # to replace restaurant description after it has been scraped
    restaurant_description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    restaurant_location = data.location
    restaurant_overall_rating = round(data.review_rating_overall, 2)

    # retrieve aspect ratings
    restaurant_ratings = dict()
    for aspect in aspects_list:
        restaurant_ratings[aspect] = round(data[f'review_rating_{aspect}'])
    # sort in decreasing aspect ratings
    restaurant_ratings_sorted = dict(sorted(restaurant_ratings.items(), key=lambda item: item[1], reverse=True))
    sorted_keys = list(restaurant_ratings_sorted.keys())

    # return a container with the details (formatted)
    return html.Div([
        html.Br(),
        html.Div([
            dbc.Row([
                dbc.Col(html.H4(restaurant_name), width=8),
                dbc.Col(html.H6(restaurant_location, style={'color': '#671FFF'}), width=2),
                dbc.Col(html.H4(f'Overall: {restaurant_overall_rating}/5'), width=2),
                # dbc.Col(html.H5('/5'), width=1, style={'text-align': 'left'})
            ]),
            dbc.Row([dbc.Col(restaurant_description, width=10),
                     # show top 3 aspect ratings
                     dbc.Col([dbc.Row(html.H6(f'{sorted_keys[0]}: {restaurant_ratings_sorted[sorted_keys[0]]}')),
                             dbc.Row(html.H6(f'{sorted_keys[1]}: {restaurant_ratings_sorted[sorted_keys[1]]}')),
                             dbc.Row(html.H6(f'{sorted_keys[2]}: {restaurant_ratings_sorted[sorted_keys[2]]}'))], 
                             width=2)
                    ]),

        ], style = {"margin-left": '20px', "margin-right": '20px', "padding": "1rem 1rem", "background-color": "#FAFAFA"}
        ),
        html.Br(),
   ])

@app.callback(
    Output("restaurants-output", "children"),
    Input("search", "n_clicks"),
    [State("location-input", "value"),
     State("price-input", "value")]
)



#### RENDER RESTAURANTS PAGE ##########################################################

def render_restaurants_page(n_clicks, location, price):
    if n_clicks == None:
        # return None if user has not searched for anything
        return (None)
    
    # read data
    restaurants_data = pd.read_csv('data/dummy_restaurants.csv')
    restaurants_filter = restaurants_data.copy()

    subtitle = "Showing results for "

    # filter by location
    if location != None:
        restaurants_filter = restaurants_filter.loc[restaurants_data.location == location]
        subtitle += f'"{location}"'
    # filter by price
    if price != None:
        restaurants_filter = restaurants_filter.loc[restaurants_filter.price_per_pax == price]
        subtitle += f' "${price} per pax"'
    # sort by overall review score
    restaurants_filter = restaurants_filter.sort_values(by=['review_rating_overall'], axis=0, ascending=False)

    # generate data
    restaurants_output = [html.H2(subtitle, style={'margin-left': '25px'})]

    # if there are no results corresponding to all filters, return a message
    if len(restaurants_filter) == 0:
        restaurants_output.append(html.Br())
        restaurants_output.append(html.H3('There are no results corresponding to your search :(', style={'margin-left': '20px'}))

    else: 
        # filter restaurant list by aspect ratings
        aspects_list_all = [x for x in aspects_list]
        aspects_list_all.sort()
        aspects_list_all.insert(0, 'overall')

        aspect_input = html.Div([
            dcc.Dropdown(
                id = "aspect-input",
                placeholder = "sort by aspect",
                options = [
                    {'label': aspect, 'value': aspect} for aspect in aspects_list_all
                ],
                className = 'm-3',
            )
        ], style = {'width': '15%', 'display': 'inline-block', 'font-size': '15px'})

        order_input = html.Div([
            dcc.Dropdown(
                id = "order-input",
                placeholder = "best/worst",
                options = [
                    {'label': 'Best', 'value': 'Best'},
                    {'label': 'Worst', 'value': 'Worst'}
                ],
                className = 'm-3',
            )
        ], style = {'width': '10%', 'display': 'inline-block', 'font-size': '15px'})

        # filter button
        filter_button = html.Div([
            dbc.Button("Filter", color="dark", block=False, id="filter", className="mb-3")
            ], className = 'm-3', style = {'width': '10%', 'display': 'inline-block', 'font-size': '15px'}
        )

        aspect_order_inputs = dbc.Row([aspect_input, order_input, filter_button], justify='end',
                                      style={'margin-right': '15px'})

        restaurants_output.append(aspect_order_inputs)
        
        for i in range(len(restaurants_filter)):
            output = generate_restaurants(restaurants_filter.iloc[i])
            restaurants_output.append(output)
    
    return (restaurants_output)


# if __name__ == '__main__':
    # app.run_server(debug=True)