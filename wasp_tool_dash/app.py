import os

import boto3
import dash
import pandas as pd
from dash.dependencies import Input, Output

import wasp_tool_dash.utilities as utilities

AWS_CLIENT = boto3.client(
    's3',
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY'))

AWS_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME') 

path = utilities.get_project_path().joinpath('wasp_tool')

# condition for checking if app data is populated 
cond = utilities.prefix_exists(AWS_CLIENT, AWS_BUCKET_NAME, 'data/celestrak.csv')

key = 'data/'

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # expose server variable for Procfile
app.layout = utilities.create_layout()


@app.callback(Output(component_id='sat-dropdown', component_property='options'),
    [Input(component_id='sat-dropdown', component_property='search_value')])
def update_search_options(search: str):
    if cond:
        inputs = utilities.populate_inputs(AWS_CLIENT, AWS_BUCKET_NAME, 'data/') 
        if search:
            return [i['label'] for i in inputs if i['value'].startswith(search.upper())]
        else:
            return inputs       
    else:
        return []
        
        
@app.callback(Output(component_id='celestrak-output', component_property='children'),
    [Input(component_id='button-update-celestrak', component_property='n_clicks')])
def update_celestrak_tles(click: int):
    changed_ids = [property['prop_id'] for property in dash.callback_context.triggered][0]
    if click and 'button-update-celestrak' in changed_ids:
        script_fn = path.joinpath('prepare_celestrak.py')
        exec(open(script_fn).read())
        return 'TLEs successfully pulled'
    return ''
    

@app.callback(Output(component_id='tabs-content', component_property='children'),
    [Input(component_id='sat-dropdown', component_property='value'),
     Input(component_id='tabs', component_property='value')])
def render_content(search: str, tab: str):
    if tab == 'tab-general':
        return utilities.populate_general_info(AWS_CLIENT, AWS_BUCKET_NAME, search, key)
    elif tab == 'tab-telemetry':
        return utilities.populate_telemetry(AWS_CLIENT, AWS_BUCKET_NAME, search, key)
    elif tab == 'tab-footprints':
        return utilities.populate_footprints(AWS_CLIENT, AWS_BUCKET_NAME, search, key)
    elif tab == 'tab-freq_plans':
        return utilities.populate_freq_plans(AWS_CLIENT, AWS_BUCKET_NAME, search, key)
    elif tab == 'tab-channels':
        return utilities.populate_channels(AWS_CLIENT, AWS_BUCKET_NAME, search, key)


@app.callback(Output(component_id='value-filter', component_property='options'),
              [Input(component_id='column-filter', component_property='value')])
def render_filter_values(column: str):
    if column == 'Channel Status':
        return ['ON', 'OFF']
    elif column == 'Ku/C-band':
        return ['Ku-band', 'C-band']    
    else:
        return []   
    
    
@app.callback(Output(component_id='data-table', component_property='data'),
              [Input(component_id='column-filter', component_property='value'),
               Input(component_id='value-filter', component_property='value'),
               Input(component_id='sat-dropdown', component_property='value')])
def update_rows(column: str, value: str, sat: str):
    path = f"channels/{sat}.csv"
    df = pd.read_csv(path, header=0)
    if column and value and sat:
        df_subset = df[df[column] == value]
        return df_subset.to_dict('records') 
    else:
        return df.to_dict('records') 
    

if  __name__ == '__main__':
    app.run_server(debug=True)
