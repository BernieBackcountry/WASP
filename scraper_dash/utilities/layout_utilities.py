from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go

import scraper_dash.utilities as utilities


def create_layout() -> html.Div:
    return html.Div(children=[html.Div(className='row', children=[
        create_information_layout(), create_data_layout()])])


def create_information_layout() -> html.Div:
        return html.Div(className='three columns div-user-controls', children=[
            create_title(), create_description(), create_search_bar(), create_logo()])


def create_data_layout() -> html.Div:
    return html.Div(className='nine columns div-for-charts bg-grey', children=[
                html.Div(id='page_content', className='loader', style={'height': 'auto', 'width': 'auto'}),
                create_tabs(), create_contact_information()], style={'textAlign': 'center', 'align-items': 'center'})


def create_title() -> html.H1:
    return html.H1("16th EWS Webscraping Tool")


def create_description() -> html.P:
    return html.P("This tool consolidates pertinent information to the satellite pair-building process. Enter a satellite below to obtain its related data.")


def create_search_bar() -> html.Div:
    return html.Div(className='search_bar', children=[
        dcc.Input(id="sat-id", type="text", placeholder="Input a satellite", style={'height': 'auto', 'width': 'auto', 'marginLeft': '10px'}),
    ])


def create_logo() -> html.Div:
    return html.Div(className='logo', children=[
        utilities.encode_image(path=utilities.get_project_path().joinpath('assets', 'spoc_logo.png'))])



def create_tabs() -> html.Div:
    style = {'width': 700, 'height': 500, 'resize': 'none', 'border-style': 'solid', 'border-color': '#862633', 'border-width': '5px', 'margin': '32px'}
    return html.Div([
        dcc.Tabs(id="tabs", value='tab-1', style={'width': '100%','font-size': '150%','height': '50%', 'margin-top': '30px', 'margin-left': '0px'}, children=[
            dcc.Tab(label='General Info', value='tab-general'),
            dcc.Tab(label='Telemetry Data', value='tab-telemetry'),
            dcc.Tab(label='Footprints', value='tab-footprints')
        ]),
        dbc.Textarea(id='tabs-content', style=style)])


def create_contact_information() -> html.Footer:
    return html.Footer(className='footer', children="michelle.mcgee.2@spaceforce.mil, alexis.denhard.ctr@spaceforce.mil")