from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go

import tmt_analyzer_dash.utilities as utilities


def create_layout(selections: dict) -> html.Div:
    return html.Div(children=[html.Div(className='row', children=[
        create_information_layout(selections=selections), create_data_layout()])])


def create_information_layout(selections: dict) -> html.Div:
        return html.Div(className='three columns div-user-controls', children=[
            create_title(), create_description(), create_selection(selections=selections), create_logo(),
            create_placeholder_output()])


def create_data_layout() -> html.Div:
    return html.Div(className='nine columns div-for-charts bg-grey', children=[
                html.Div(id='page_content', className='loader', style={'height': '100%', 'width': '100%'}),
                create_contact_information()], style={'textAlign': 'center', 'align-items': 'center'})


def create_title() -> html.H1:
    return html.H1("SpOC 16th EWS Webscraper")


def create_description() -> html.P:
    return html.P("Predict a TMT tasker's intended audience using AI/ML. Input the text of a tasker into the text box to obtain the predicted audience.")


def create_selection(selections: dict) -> html.Div:
    return html.Div(className='div-for-dropdown', children=[html.Label(children=[
        "Selections:", dcc.Dropdown(id='selections_dropdown', clearable=False, value='Predict', options=selections)])])


def create_logo() -> html.Div:
    return html.Div(className='logo', children=[
        utilities.encode_image(path=utilities.get_project_path().joinpath('assets', 'spoc_logo.png'))])


def create_predict() -> html.Div:
    style = {'width': '75%', 'height': 300, 'border-style': 'solid', 'border-color': '#862633', 'border-width': '5px'}
    return html.Div(className='nine columns div-for-charts bg-grey', children=[
        dbc.Textarea(id='text_tasker', className='bg-grey', placeholder='Input TMT tasker here', style=style),
        html.Button('Predict', id='button_predict', n_clicks=0, style={'margin': '50px', 'background-color': '#00263A', 'color': '#DBE2E9'}),
        dbc.Textarea(id='text_oprs', className='bg-grey', placeholder='Result', style=style)
    ], style={'width': '100%', 'display': 'flex', 'justify-content': 'center', 'align-items': 'center'})


def create_explore() -> html.Div:
    return html.Div(children=[create_pie_chart(), create_line_chart()])


def create_train(intents):
    style = {'width': '75%', 'height': 300, 'border-style': 'solid', 'border-color': '#862633', 'border-width': '5px'}
    return html.Div(className='nine columns div-for-charts bg-grey', children=[
        dbc.Textarea(id='text_tasker_train', className='bg-grey', placeholder='Input TMT tasker here', style=style),
        create_training_buttons(),
        create_training_text(intents=intents)
    ], style={'width': '100%', 'display': 'flex', 'justify-content': 'center', 'align-items': 'center'})


def create_training_buttons() -> html.Div:
    return html.Div(className='two columns', children=[
        html.Button('Predict', id='button_predict_train', n_clicks=0, style={'margin': '50px', 'background-color': '#00263A', 'color': '#DBE2E9'}),
        html.Button('Persist', id='button_persist_train', n_clicks=0, style={'margin': '50px', 'background-color': '#00263A', 'color': '#DBE2E9'}),
    ], style={'width': '100%', 'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'margin': '0px'})


def create_training_text(intents: dict) -> html.Div:
    style = {'width': '35%', 'height': 300, 'border-style': 'solid', 'border-color': '#862633', 'border-width': '5px'}
    return html.Div(className='three columns', children=[
        dbc.Textarea(id='text_oprs_train', className='bg-grey', placeholder='Result', style=style),
        dcc.Checklist(id='checklist_oprs_train', className='one columns', options=list(intents.keys()), style={'text-align': 'left', 'width': '10%'}),
        dbc.Textarea(id='text_reason_train', className='bg-grey', placeholder='Reason', style=style)
    ], style={'width': '100%', 'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'margin': '0px'})


def create_pie_chart() -> dcc.Graph:
    df = get_data()
    figure = go.Figure()
    figure.add_trace(go.Pie(labels=df.columns.values, values=df.sum(), sort=False))
    figure.update_layout(title='Ratio of TMT Taskers', plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)')
    return dcc.Graph(figure=figure, config={'displayModeBar': False}, style={'margin-bottom': '-75px'})


def create_line_chart() -> dcc.Graph:
    df = get_data()
    figure = go.Figure()
    for column in df.columns.values:
        figure.add_trace(go.Scatter(x=df.index, y=df[column], mode='lines', name=column))
    figure.update_layout(
        title='Timeline of TMT Taskers', xaxis_title='Date', yaxis_title='TMT Taskers', 
        plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)')
    return dcc.Graph(figure=figure, config={'displayModeBar': False})


def get_data() -> pd.DataFrame:
    data = {
        'S9A': {'2022-01-01': 2, '2022-02-01': 3, '2022-03-01': 4, '2022-04-01': 2, '2022-05-01': 3, '2022-06-01': 3},
        'S9I': {'2022-01-01': 1, '2022-02-01': 2, '2022-03-01': 2, '2022-04-01': 4, '2022-05-01': 1, '2022-06-01': 3},
        'CDO': {'2022-01-01': 3, '2022-02-01': 2, '2022-03-01': 5, '2022-04-01': 6, '2022-05-01': 4, '2022-06-01': 3},
        'IN': {'2022-01-01': 2, '2022-02-01': 1, '2022-03-01': 1, '2022-04-01': 2, '2022-05-01': 3, '2022-06-01': 1},
        'IA': {'2022-01-01': 1, '2022-02-01': 1, '2022-03-01': 2, '2022-04-01': 1, '2022-05-01': 3, '2022-06-01': 1}
    }
    df = pd.DataFrame(data=data)
    return df[sorted(df.columns)]


def create_contact_information() -> html.Footer:
    return html.Footer(className='footer', children="michelle.mcgee.2@spaceforce.mil, alexis.denhard.ctr@spaceforce.mil")


# DO WE NEED THIS FUNCTION?????
def create_placeholder_output() -> html.Div:
    return html.Div(id='hidden-div', style={'display':'none'})

