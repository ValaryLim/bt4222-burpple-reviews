# import packages
import utils
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px

# import app
from app import app
import pandas as pd

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
    "padding": "1rem 1rem",
    "font-size": "12px",
    "margin": "2rem"
}

RESTAURANT_URL = 'data/dummy_restaurants.csv'
REVIEW_URL = 'data/dummy_reviews.csv'
CATEGORIES = ['Italian', 'Malay', 'Japanese', 'Chinese', 'Western', 'Korean',\
    'Thai', 'Vietnamese', 'Mexican', 'Indian', 'Local Delights', 'Desserts', \
    'Healthy', 'Cafes & Coffee', 'Halal', 'Beverages', 'Others']

# load restaurant and review data
restaurant_df = pd.read_csv(RESTAURANT_URL)
restaurant_df = utils.process_csv_lists(restaurant_df, columns=["restaurant_photo"])
review_df = pd.read_csv(REVIEW_URL)

# header
header = html.Div(
    [
        dbc.Row([html.H5("burpple+", className="display-4", \
            style={'font-weight': '500', 'margin-left': 20})]),
    ],
    style=HEADER_STYLE
)

layout = html.Div([
    header,
    html.Div(id='restaurant-page', style=CONTENT_STYLE)
])


@app.callback(
    Output("restaurant-page", "children"),
    Input('url', 'pathname'),
)
def render_restaurant_page(pathname):
    restaurant_code = pathname.split("/")[1][11:]
    restaurant_info = restaurant_df.loc[restaurant_df["restaurant_code"] == restaurant_code]
    restaurant_page = []

    photo_collage = []
    restaurant_photos = restaurant_info["restaurant_photo"].values[0]
    for photo_src in restaurant_photos:
        photo_collage.append(html.Img(src=photo_src, \
            style={"height": "20%", "width": "20%", "padding": "0.5rem"}))
    restaurant_page.append(html.Div(photo_collage))

    restaurant_name = restaurant_info["restaurant_name"]
    restaurant_page.append(html.H3(restaurant_name))

    # add categories
    for cat in CATEGORIES:
        if restaurant_info[cat].values[0] == 1:
            restaurant_page.append(
                html.Button(cat, id=cat, n_clicks=0, \
                    style={"margin-right": "0.5rem", "margin-bottom": "1rem"}))

    restaurant_description = restaurant_info["restaurant_description"]
    restaurant_page.append(html.P(restaurant_description, \
        style={"font-size": "14px"}))

    restaurant_number = str(restaurant_info["restaurant_number"].values[0])
    restaurant_page.append(
        html.Div([
            html.I(className="fa fa-phone", \
                style={"font-size": "18px", "margin-left":"0.25rem", "margin-top": "0.25rem", "margin-right":"1rem"}), 
            html.P(restaurant_number)
        ], style={"display": "flex", "font-size": "14px"})   
    )

    restaurant_address = restaurant_info["restaurant_address"]
    restaurant_page.append(
        html.Div([
            html.I(className="fa fa-map-marker", \
                style={"font-size": "18px", "margin-left":"0.5rem",  "margin-top": "0.25rem", "margin-right":"1.25rem"}), 
            html.P(restaurant_address)
        ], style={"display": "flex", "font-size": "14px"})   
    )

    restaurant_price = restaurant_info["price_per_pax"].values[0]
    restaurant_page.append(
        html.Div([
            html.I(className="fa fa-money", \
                style={"font-size": "18px", "margin-top": "0.25rem", "margin-right":"1rem"}), 
            html.P(restaurant_price)
        ], style={"display": "flex", "font-size": "14px"})   
    )

    restaurant_page.append(html.Hr())
    return (restaurant_page)
