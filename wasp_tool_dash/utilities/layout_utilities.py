from dash import dcc, html

import wasp_tool_dash.utilities as utilities


def create_layout() -> html.Div:
    return html.Div(children=[html.Div(className='row', children=[
        create_information_layout(), create_data_layout()])])


def create_information_layout() -> html.Div:
        return html.Div(className='three columns div-user-controls', children=[
            create_title(), create_description(), create_search_dropdown(), create_search_message(),
            create_button_celestrak(), create_celestrak_output(), create_sources_output(), create_logo()])


def create_data_layout() -> html.Div:
    return html.Div(className='nine columns div-for-charts bg-grey', children=[
                html.Div(id='page_content', className='loader', style={'height': 'auto', 'width': 'auto'}),
                create_tabs(), create_contact_information()], style={'textAlign': 'center', 'align-items': 'center'})


def create_title() -> html.H1:
    return html.H1("16th EWS W.A.S.P.")


def create_description() -> html.P:
    return html.P("The Webscraping Application for Satellite Pairing (WASP) consolidates pertinent information to the satellite pair-building process. Enter a satellite below to obtain its related data.")


def create_search_dropdown() -> html.Div:
    return html.Div(className='search_dropdown', children=[
        dcc.Dropdown(id="sat-dropdown", placeholder="Input a satellite", style={'marginLeft': '5px'}),
    ])


def create_search_message() -> html.Div:
    return html.Div(id='search-message', style={'height': '25px'})
 
 
def create_button_celestrak() -> html.Div:
    return html.Div(className='button_celestrak', children=[
        html.Div("Click the button below to obtain up-to-date TLEs.", style={'marginLeft': '5px'}),
        html.Button('Update Celestrak TLEs', id='button-update-celestrak', n_clicks=0, style={'marginLeft': '5px', 'background-color': '#00263A', 'color': '#DBE2E9'})
    ])


def create_logo() -> html.Div:
    return html.Div(className='logo', children=[
        utilities.encode_image(path=utilities.get_project_path().joinpath('wasp_tool_dash', 'assets', 'spoc_logo.png'))])
        
        
def create_celestrak_output() -> html.Div:
    return html.Div(id='celestrak-output', style={'marginLeft': '5px'})
    
    
def create_sources_output() -> html.Div:
    return html.Div(id='sources-output', style={'marginLeft': '5px'})


def create_tabs() -> html.Div:
    style = {'width': 1100, 'height': 500, 'resize': 'none', 'margin': '32px'}
    return html.Div([
        dcc.Tabs(id="tabs", value='tab-1', children=[
            dcc.Tab(label='General Info', value='tab-general'),
            dcc.Tab(label='TLE', value='tab-telemetry'),
            dcc.Tab(label='Footprints', value='tab-footprints'),
            dcc.Tab(label='Frequency Plans', value='tab-freq_plans'),
            dcc.Tab(label='Channels', value='tab-channels'),
            ]),
        html.Div(id='tabs-content')], style=style)


def create_contact_information() -> html.Footer:
    return html.Footer(className='footer', children="All information presented on this dashboard is aggregated and compiled from open-source, unclassified websites. \
        The information is copyrighted and not approved for commercial or public use. The original sources for this information are \
        https://www.satbeams.com/, https://www.lyngsat.com/, https://celestrak.org/, and http://frequencyplansatellites.altervista.org/. \
        For more information or questions, please contact michelle.mcgee.2@spaceforce.mil and/or alexis.denhard.ctr@spaceforce.mil", 
        style={'font-style': 'italic'})
