import dash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import pandas as pd

import scraper_dash.utilities as utilities 


path = utilities.get_project_path().resolve().parent.joinpath('scraper')
path_celestrak = path.joinpath('data','celestrak.csv')
path_satbeam = path.joinpath('data','satbeam.csv')

df_celestrak = pd.read_csv(f'{path_celestrak}', header=0)
df_satbeam = pd.read_csv(f'{path_satbeam}', header=0)

celestrak_satellites = df_celestrak['Satellite'].tolist()
satbeam_satellites = df_satbeam['Satellite'].tolist()
acceptable_satellites = list(set(celestrak_satellites + satbeam_satellites))


acceptable_satellites.sort()
options = [{'label': sat, 'value': sat} for sat in acceptable_satellites]


app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # expose server variable for Procfile
app.layout = utilities.create_layout()


@app.callback(Output(component_id="sat-dropdown", component_property="options"),
    [Input(component_id="sat-dropdown", component_property="search_value")])
def update_options(search_value):
    if not search_value:
        raise PreventUpdate
    search_value = search_value.lower()
    return [o["label"] for o in options if o["value"].lower().startswith(search_value)]


@app.callback(Output(component_id="tabs-content", component_property="children"),
    [Input(component_id="sat-dropdown", component_property="value"),
     Input(component_id='tabs', component_property='value')])
def render_content(sat: str, tab):
    if sat is None:
        raise PreventUpdate
    else:
        if sat.upper() in acceptable_satellites:
            if tab == 'tab-general':
                return utilities.populate_general_info(sat, satbeam_satellites, df_satbeam) 
            elif tab == 'tab-telemetry':
                return utilities.populate_telemetry(sat, celestrak_satellites, df_celestrak)
            elif tab == 'tab-footprints':
                return utilities.populate_footprints(sat, satbeam_satellites)
        return ""


if  __name__ == '__main__':
    app.run_server(debug=True)