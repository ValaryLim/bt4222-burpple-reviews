# import packages
import utils
import math
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
SCORE_METRICS = ['Taste', 'Value', 'Service', 'Ambience', 'Overall']

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
    # retrieve restaurant code from path name
    restaurant_code = pathname.split("/")[1][11:]

    # filter for restaurant and review details
    restaurant_info = restaurant_df.loc[restaurant_df["restaurant_code"] == restaurant_code]
    filtered_reviews = review_df.loc[review_df["restaurant_code"] == restaurant_code]
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
                dbc.Button(cat, id=cat, n_clicks=0, \
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
            html.P("$" + str(restaurant_price) + " /pax")
        ], style={"display": "flex", "font-size": "14px"})   
    )

    restaurant_page.append(html.Hr())

    restaurant_reviews = []
    # print reviews 
    for i, row in filtered_reviews.iterrows():
        review_title = row["review_title"]
        review_body = row["review_body"]
        review_date = row["review_date"]
        review_photo = row["review_photo"]
        review_reviewer = row["account_name"]
        review_reviewer_level = row["account_level"]
        review_reviewer_photo = row["account_photo"]

        review_table_body = []
        for review_metric in SCORE_METRICS:
            if math.isnan(row["review_rating_" + review_metric.lower()]):
                continue
            else:
                review_table_body.append(
                    html.Tr([html.Td(review_metric, style={"font-weight": "bold"}), 
                    html.Td(round(row["review_rating_" + review_metric.lower()], 2))],
                    style={"font-size": "14px"}
                ))
        
        review_jumbotron = dbc.Jumbotron([
            dbc.Container([
                dbc.Row([
                    dbc.Col(html.Img(src=review_photo, style={"width": "100%"}), width=3, style={"margin": "0px"}),
                    dbc.Col(html.Div([
                        html.H5(review_title, className="review-title"),
                        html.P(review_body, className="review-body", style={"font-size": "14px"}),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col(html.Img(src=review_reviewer_photo, style={"width": "80%", "border-radius": "50%"}), width=2),
                            dbc.Col([
                                html.H6(review_reviewer, className="review-reviewer"), 
                                html.P(review_reviewer_level, className="review-date", style={"margin-bottom": "5px", "padding": "0px", "font-size": "14px"}),
                                html.P(review_date, className="review-date", style={"margin": "0px", "padding": "0px", "font-size": "14px"})
                            ])
                        ])
                    ])),
                    dbc.Col(dbc.Table([html.Tbody(review_table_body)], borderless=True), width=2),
                ], style={"margin":"0px", "padding": "0px"})
            ], fluid=True, style={"margin":"0px", "padding": "0px"})
        ], fluid=True, style={"padding": "15px 0px 15px 0px"})

        restaurant_reviews.append(review_jumbotron)

    #     review_card = dbc.Card([
    #         dbc.CardImg(src=review_photo, top=True),
    #         dbc.CardBody([
    #             html.H6(review_title, className="review-title"),
    #             html.P(review_body, className="review-body"),
    #             html.P(review_date, className="review-date"),
    #             html.Hr(),
    #             html.P(review_rating_taste, className="review-rating"),
    #             html.P(review_rating_value, className="review-rating"),
    #             html.P(review_rating_service, className="review-rating"),
    #             html.P(review_rating_ambience, className="review-rating"),
    #             html.P(review_rating_overall, className="review-rating"),
    #         ])
    #     ], style={"width": "330px", "margin":"0.5rem"})
        
    #     restaurant_reviews.append(review_card)
    
    # card_columns = dbc.CardColumns(restaurant_reviews, style={"columns": "4"})
    # restaurant_page.append(card_columns)

    restaurant_page.append(html.Div(restaurant_reviews))

    restaurant_page.append(html.Div(restaurant_reviews, style={"display": "inline"}))
    return (restaurant_page)
