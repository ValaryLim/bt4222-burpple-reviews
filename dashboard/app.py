# import packages
import dash
import dash_bootstrap_components as dbc

# set up application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "https://codepen.io/chriddyp/pen/bWLwgP.css", 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'])
# server = app.server