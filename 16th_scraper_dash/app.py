import dash
from dash.dependencies import Input, Output

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # expose server variable for Procfile
app.layout = utilities.create_layout(selections=selections)

# put in call backs below 
