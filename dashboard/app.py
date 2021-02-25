# import packages
import dash
import dash_bootstrap_components as dbc

# set up application
app = dash.Dash(__name__, suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP, \
                                      'assets/priceslider.css', \
                                      'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'])
# server = app.server
