# import packages
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# import apps
from app import app
from apps import search_restaurants, restaurant_page

#### APP LAYOUT ##########################################################
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


#### APP CALLBACKS ##########################################################
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))

def display_page(pathname):
    if pathname == '/':
        return search_restaurants.layout
    elif '/restaurant-' in pathname:
        return restaurant_page.layout
    #     return # something
    # else: # default start page
    #     return search_restaurants.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)