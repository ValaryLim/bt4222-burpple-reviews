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
    "border-bottom-style": "solid",
    "border-bottom-color": "black",
    "background-color": "white",
    "font-size": "12px",
    "zIndex": 100,
    "position": "fixed"
}

# styles for the main content 
CONTENT_STYLE = {
    "padding-top": "75px",
    "padding-left": "1rem",
    "padding-right": "1rem",
    "font-size": "12px",
    "margin": "2rem",
    "zIndex": 0
}

RESTAURANT_URL = 'data/dummy_restaurants.csv'
REVIEW_URL = 'data/dummy_reviews.csv'
CATEGORIES = ['Italian', 'Malay', 'Japanese', 'Chinese', 'Western', 'Korean',\
    'Thai', 'Vietnamese', 'Mexican', 'Indian', 'Local Delights', 'Desserts', \
    'Healthy', 'Cafes & Coffee', 'Halal', 'Beverages', 'Others']
ASPECTS = ['Overall', 'Taste', 'Value', 'Service', 'Ambience']

# load restaurant and review data
restaurant_df = pd.read_csv(RESTAURANT_URL)
restaurant_df = utils.process_csv_lists(restaurant_df, columns=["restaurant_photo"])
review_df = pd.read_csv(REVIEW_URL)

# header
header = html.Div(
    [
        dbc.Row(dcc.Link(
                html.H5("burpple+", className="display-4", style={"color":"#BF0A30", 'font-weight': '700', 'margin-left': 20}),
                href='/', style={"color":"#BF0A30"}))
    ],
    style=HEADER_STYLE
)

layout = html.Div([
    header,
    html.Div(id='restaurant-page', style=CONTENT_STYLE)
])

aspect_input = html.Div([
    dcc.Dropdown(
        id = "aspect-input",
        value="Overall",
        options = [
            {'label': aspect, 'value': aspect} for aspect in ASPECTS
        ],
        className = 'm-3',
        searchable=False,
        clearable=False
    )
], style = {'width': '170px', 'display': 'inline-block', 'font-size': '14px'})

# aspect order sort input
order_input = html.Div([
    dcc.Dropdown(
        id = "order-input",
        value = "Descending",
        options = [
            {'label': 'Descending', 'value': 'Descending'},
            {'label': 'Ascending', 'value': 'Ascending'}
        ],
        className = 'm-3',
        searchable=False,
        clearable=False
    )
], style = {'width': '170px', 'display': 'inline-block', 'font-size': '14px'})


@app.callback(
    Output("restaurant-page", "children"),
    Input('url', 'pathname')
)
def render_restaurant_page(pathname):
    # retrieve restaurant code from path name
    restaurant_code = pathname.split("/")[1][11:]

    # filter for restaurant and review details
    restaurant_info = restaurant_df.loc[restaurant_df["restaurant_code"] == restaurant_code]
    restaurant_page = []
    
    # if no restaurant info, don't generate any output
    if len(restaurant_info) == 0:
        return restaurant_page

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
    restaurant_page.append(html.P(restaurant_description, style={"font-size": "14px"}))

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

    # overall restaurant rating
    restaurant_page.append(html.Hr())
    table_header = [
        html.Thead(html.Tr([html.Th(x) for x in ASPECTS]))
    ]
    table_row = []
    for aspect in ASPECTS:
        aspect_score = round(restaurant_info["review_rating_" + aspect.lower()].values[0], 2)
        table_row.append(html.Td(str(aspect_score) + " / 5.00"))
    table_body = [html.Tbody([html.Tr(table_row)])]
    restaurant_page.append(dbc.Table(table_header + table_body, borderless=True, \
        style={"font-size": "20px", "text-align": "center"}))

    # reviews and inputs to sort by aspect (ascending/descending)
    restaurant_page.append(html.Hr())
    restaurant_page.append(dbc.Row([aspect_input, order_input], justify='end'))
    restaurant_page.append(html.Div([], id="restaurant-reviews"))

    return (restaurant_page)

@app.callback(
    Output('restaurant-reviews', 'children'),
    [Input('aspect-input', 'value'), Input('order-input', 'value')],
    State('url', 'pathname'))
def update_output(aspect, order, pathname):
    # retrieve restaurant code from path name
    restaurant_code = pathname.split("/")[1][11:]

    # REVIEWS SECTION #
    filtered_reviews = review_df.loc[review_df["restaurant_code"] == restaurant_code]
    ascending = (order == "Ascending")
    selected_aspect = "review_rating_" + aspect.lower()
    filtered_reviews = filtered_reviews.sort_values(by=selected_aspect, ascending=ascending)

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

        review_overall_score = None
        if selected_aspect == "review_rating_overall":
            review_overall_score = html.H6(f'Overall   : {round(row["review_rating_overall"], 2)}/5.0', \
                style={"margin-top":"5px", "margin-left":"12px", "color": "#BF0A30"})
        else:
            review_overall_score = html.H6(f'Overall   : {round(row["review_rating_overall"], 2)}/5.0', \
                style={"margin-top":"5px", "margin-left":"12px"})
        
        review_table_body = []
        for review_metric in ASPECTS[1:]: # exclude overall
            column = "review_rating_" + review_metric.lower()
            if column == selected_aspect:
                if math.isnan(row[column]):
                    review_table_body.append(html.Tr([html.Td(review_metric, style={"font-weight": "bold", "color":"#BF0A30"}), \
                        html.Td("-", style={"color":"#BF0A30", "font-weight": "bold"})], 
                        style={"padding": "0px"}))
                else:
                    review_table_body.append(html.Tr([html.Td(review_metric, style={"font-weight": "bold", "color":"#BF0A30"}), \
                        html.Td(round(row[column], 2), style={"color":"#BF0A30", "font-weight": "bold"})],
                        style={"padding": "0px"}))
            else:
                if math.isnan(row[column]):
                    review_table_body.append(html.Tr([html.Td(review_metric, style={"font-weight": "bold"}), \
                        html.Td("-")], style={"padding": "0px"}))
                else:
                    review_table_body.append(html.Tr([html.Td(review_metric, style={"font-weight": "bold"}), \
                        html.Td(round(row[column], 2))], style={"padding": "0px"}))
    
        review_jumbotron = dbc.Jumbotron([
            dbc.Container([
                dbc.Row([
                    dbc.Col(html.Img(src=review_photo, style={"width": "100%"}), width=2, style={"margin": "0px"}),
                    dbc.Col(html.Div([
                        html.H5(review_title, className="review-title"),
                        html.P(review_body, className="review-body"),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col(html.Img(src=review_reviewer_photo, style={"width": "100%", "border-radius": "50%"}), width=1),
                            dbc.Col([
                                html.H6(review_reviewer, className="review-reviewer"), 
                                html.P(review_reviewer_level + ", " + review_date, style={"margin-bottom": "5px", "padding": "0px"})
                            ])
                        ])
                    ])),
                    dbc.Col([review_overall_score, dbc.Table([html.Tbody(review_table_body)], borderless=True)], width=2),
                ], style={"margin":"0px", "padding": "0px"})
            ], fluid=True, style={"margin":"0px", "padding": "0px"})
        ], fluid=True, style={"padding": "15px 0px 15px 0px", "position": "relative"})

        restaurant_reviews.append(review_jumbotron)

    return restaurant_reviews
