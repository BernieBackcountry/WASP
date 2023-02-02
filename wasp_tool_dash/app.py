import dash
from dash import html
from dash.dependencies import Input, Output

import wasp_tool_dash.utilities as utilities 

path = utilities.get_project_path().resolve().parent.joinpath('wasp_tool')
# condition for checking if app data is populated 
cond = path.joinpath('data').exists()

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # expose server variable for Procfile
app.layout = utilities.create_layout()


@app.callback(Output(component_id="sat-dropdown", component_property="options"),
    [Input(component_id="sat-dropdown", component_property="search_value")])
def update_search_options(search: str):
    if cond:
        inputs = utilities.populate_inputs(path)
        if not search:
            return inputs
        else:
            return [i["label"] for i in inputs if i["value"].startswith(search.upper())]
    else:
        return []


@app.callback(Output(component_id='sources-output', component_property='children'),
    [Input(component_id="button-data-pull", component_property="n_clicks")])
def populate_data_sources(click: int):
    changed_ids = [property['prop_id'] for property in dash.callback_context.triggered][0]
    if click and 'button-data-pull' in changed_ids:
        script_fn = "wasp_tool/prepare.py"
        exec(open(script_fn).read())
        return "Data successfully pulled"
    return ''
        
        
@app.callback(Output(component_id='celestrak-output', component_property='children'),
    [Input(component_id="button-update-celestrak", component_property="n_clicks")])
def update_celestrak_tles(click: int):
    changed_ids = [property['prop_id'] for property in dash.callback_context.triggered][0]
    if click and 'button-update-celestrak' in changed_ids:
        script_fn = "wasp_tool/prepare_celestrak.py"
        exec(open(script_fn).read())
        return "TLEs successfully pulled"
    return ''
    

@app.callback(Output(component_id="tabs-content", component_property="children"),
    [Input(component_id="sat-dropdown", component_property="value"),
     Input(component_id='tabs', component_property='value')])
def render_content(search: str, tab: str):
    if tab == 'tab-general':
        return utilities.populate_general_info(search, path) 
    elif tab == 'tab-telemetry':
        return utilities.populate_telemetry(search, path)
    elif tab == 'tab-footprints':
        return utilities.populate_footprints(search, path)
    elif tab == 'tab-freq_plans':
        return utilities.populate_freq_plans(search, path)
    elif tab == 'tab-channels':
        return utilities.populate_channels(search, path)


if  __name__ == '__main__':
    app.run_server(debug=True)
