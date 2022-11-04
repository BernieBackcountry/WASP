import dash
from dash.dependencies import Input, Output

import scraper_dash.utilities as utilities 

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # expose server variable for Procfile
app.layout = utilities.create_layout()

acceptable_satellites = ["test", "yee"]

# Call back for search bar
@app.callback(
    Output(component_id='tabs-content', component_property='value'),
    [Input(component_id='sat-id', component_property='value')])
def get_general_info(sat: str):
    if sat in acceptable_satellites:
        return "Click a tab to view information for " + sat
    else:
        return []


# # Callback for tab navigation - fill textbox dependent on tab id
# @app.callback(Output('tabs-content', 'children'),
#               Input('tabs', 'value'))
# def render_content(tab):
#     if tab == 'tab-general':
#         return html.Div([
#             html.H3('Tab content 1')
#         ])
#     elif tab == 'tab-telemetry':
#         return html.Div([
#             html.H3('Tab content 2')
#         ])
#     elif tab == 'tab-footprints':


if  __name__ == '__main__':
    app.run_server(debug=True)
