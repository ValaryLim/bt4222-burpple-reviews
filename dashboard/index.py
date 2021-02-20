# import packages
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# import apps
from app import app
from apps import search_restaurants
# from apps import search_restaurants, search_reviews


#### APP LAYOUT ##########################################################
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


#### APP CALLBACKS ##########################################################
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))

def display_page(pathname):
    if pathname == '/search-reviews':
        return # something
    else: # default start page
        return search_restaurants.layout
    # else:
        # return '404'

if __name__ == '__main__':
    app.run_server(debug=True)