# import packages
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# connect to main app.py file
from app import app
from app import server

# connect to pages
from apps import main_page, restaurant_page

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
        return main_page.layout
    elif '/restaurant-' in pathname:
        return restaurant_page.layout
    else:
        return '404 Page Not Found Error'

if __name__ == '__main__':
    app.run_server(debug=True)