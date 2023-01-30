import dash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import pandas as pd

import wasp_tool_dash.utilities as utilities 


path = utilities.get_project_path().resolve().parent.joinpath('wasp_tool')
path_celestrak = path.joinpath('data','celestrak.csv')
path_satbeams = path.joinpath('data','satbeams.csv')
path_lyngsat = path.joinpath('data','lyngsat.csv')
path_altervista = path.joinpath('data','altervista.csv')

df_celestrak = pd.read_csv(f'{path_celestrak}', header=0)
df_satbeams = pd.read_csv(f'{path_satbeams}', header=0)
df_lyngsat = pd.read_csv(f'{path_lyngsat}', header=0)
df_altervista = pd.read_csv(f'{path_altervista}', header=0)

celestrak_satellites = df_celestrak['priSatName'].tolist()
satbeams_satellites = df_satbeams['priSatName'].tolist()
lyngsat_satellites = df_lyngsat['priSatName'].tolist()
altervista_satellites = df_altervista['priSatName'].tolist()

acceptable_satellites = list(set(celestrak_satellites + satbeams_satellites + lyngsat_satellites + altervista_satellites))
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
                return utilities.populate_general_info(sat, satbeams_satellites, df_satbeams) 
            elif tab == 'tab-telemetry':
                return utilities.populate_telemetry(sat, celestrak_satellites, df_celestrak)
            elif tab == 'tab-footprints':
                return utilities.populate_footprints(sat, satbeams_satellites)
            elif tab == 'tab-freq_plans':
                return utilities.populate_freq_plans(sat, altervista_satellites)
            elif tab == 'tab-channels':
                return utilities.populate_channels(sat, lyngsat_satellites)
        return ""


if  __name__ == '__main__':
    app.run_server(debug=True)
