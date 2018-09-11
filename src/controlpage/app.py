import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import os
import flask
import glob
import json
import logging

import model_scoring


logging.basicConfig(level=logging.INFO)

IMAGES_DIR = './data/images/faces'

current_image_object = None

feature_data = [
    {
        'label': 'Haarkleur',
        'value': 'hair_colour',
        'options': [
            {'label': 'licht', 'value': 'light'},
            {'label': 'donker', 'value': 'dark'},
            {'label': 'geen haar', 'value': 'no_hair'}
        ]
    }, {
        'label': 'Haartype',
        'value': 'hair_type',
        'options': [
            {'label': 'krullend', 'value': 'curly'},
            {'label': 'stijl', 'value': 'straight'},
            {'label': 'kort', 'value': 'too_short'}
        ]
    }, {
        'label': 'Haarlengte',
        'value': 'hair_length',
        'options': [
            {'label': 'kaal', 'value': 'bold'},
            {'label': 'kort', 'value': 'short_hair'},
            {'label': 'lang', 'value': 'long_hair'}
        ]
    }, {
        'label': 'Geslacht',
        'value': 'gender',
        'options': [
            {'label': 'man', 'value': 'man'},
            {'label': 'vrouw', 'value': 'woman'}
        ]
    }, {
        'label': 'Hoofddeksel',
        'value': 'hat',
        'options': [
            {'label': 'hoed', 'value': 'hat'},
            {'label': 'pet', 'value': 'cap'},
            {'label': 'geen', 'value': 'none'}
        ]
    }, {
        'label': 'Bril',
        'value': 'glasses',
        'options': [
            {'label': 'bril', 'value': 'glasses'},
            {'label': 'geen bril', 'value': 'no_glasses'}
        ]
    }, {
        'label': 'Stropdas',
        'value': 'tie',
        'options': [
            {'label': 'met das', 'value': 'tie'},
            {'label': 'zonder das', 'value': 'no_tie'}
        ]
    }, {
        'label': 'Gezichtsbeharing',
        'value': 'facial_hair',
        'options': [
            {'label': 'baard', 'value': 'beard'},
            {'label': 'snor', 'value': 'moustache'},
            {'label': 'geen', 'value': 'no_facial_hair'}
        ]
    }
]

feature_keys = [x['value'] for x in feature_data]

list_of_images = [os.path.basename(x) for x in glob.glob('./data/images/faces/*.jpg') if 'dummy' not in x]


def bulma_modal(id, content=None, btn_text='OK', btn_class='is-info', active=False):
    """
    Create a modal (overlay) in bulma format
    """
    return html.Div(className='modal {}'.format('is-active' if active else ''), id='{}-modal'.format(id), children=[
        html.Div(className='modal-background'),
        html.Div(className='modal-content', children=[
            html.Div(className='box', children=[
                html.Div(className='content', children=[
                    html.Div(id='{}-modal-content'.format(id), children=content),
                    html.Button(id='{}-modal-button'.format(id),
                                className='button is-medium {}'.format(btn_class),
                                n_clicks=0,
                                children=btn_text
                                )
                ])
            ])
        ])
    ])


def bulma_dropdown(id, options, value=''):
    """
    Wrapper to create a bulma select/dropdown
    :param id: name for id of html element
    :param options: list of dicts with label and value
    :return: Dash html component
    """
    return html.Div(id=id, className='select', children=[
        html.Select([
            html.Option(value=o['value'], children=o['label']) for o in options
        ])
    ])


def show_field_row(data):
    return html.Tr([
        html.Td([
            html.Label(className='label field-label', children=data['label']),
        ]),
        html.Td([
            bulma_dropdown(id='input-'+data['value'], options=data['options'])
        ]),
        html.Td('hier komt nog een bar chart met de scores')
    ])


app = dash.Dash()

app.layout = html.Div(className='container is-fluid', children=[

    # Choose image
    html.H1(children='Kies een foto'),
    dcc.Dropdown(
        id='image-dropdown',
        options=[{'label': i, 'value': i} for i in list_of_images],
        value=''
    ),
    #html.Div(id='hidden-input-image', accessKey=''),
    html.Figure([
        html.Img(id='image', src='/assets/dummy.png')
    ]),

    # hidden json data containers
    html.Div(id='data-container', accessKey='{}'),
    html.Div(id='data-container2', accessKey='{}'),

    # dropdown field for features
    html.Table(className='table is-striped', children=[
        html.Tbody([
            show_field_row(field) for field in feature_data
        ])
    ]),

    html.Button('Opslaan', id='save-button', className='button is-medium is-info', n_clicks=0),
    html.Div(id='output-save', children=''),

    dcc.Input(id='testdiv', type='text', value=''),

    # modal for when model in scoring
    bulma_modal(id='waiting',
                content=[
                    html.Img(className='header-logo', src='/assets/web-development.gif'),
                    html.Br(), html.Br(),
                    html.H3('Analyzing image. Please wait...'),
                ],
                btn_class='is-hidden',
                active=False
                )
])


@app.server.route('/<path:path>')
def serve_images(path):
    """
    Pass local images to the web server
    """
    print(path)
    root_dir = os.getcwd()
<<<<<<< HEAD
    return flask.send_from_directory(os.path.join(root_dir, 'data/images/faces'), path)


@app.callback(
    Output('waiting-modal', 'className'),
    [Input('image-dropdown', 'value')]
)
def show_waiting_modal(value):
    """
    Show the selected image
    """
    if value is None or value == '':
        return 'modal'
    return 'modal is-active'
=======
    # return flask.send_from_directory(os.path.join(root_dir, 'data/images/faces'), path)
    return flask.send_from_directory(image_directory, path)
>>>>>>> 7f81a690992808269b67a0935fccfbecb7f8bfef


@app.callback(
    Output('image', 'src'),
    [Input('image-dropdown', 'value')]
)
def update_image_src(value):
    """
    Show the selected image
    """
    if value is None or value == '':
        return '/assets/dummy.png'
<<<<<<< HEAD
    logging.info('Selected image: {}'.format(value))
    return os.path.join('/images', value)
=======
    return os.path.join(image_directory, value)
>>>>>>> 7f81a690992808269b67a0935fccfbecb7f8bfef


@app.callback(
    Output('data-container', 'accessKey'),
    [Input('image-dropdown', 'value')]
)
def choose_image(dropdown_value):
    """
    Use selected image to score model on and return estimated features
    """

    if dropdown_value is None or dropdown_value == '':
        return ''
<<<<<<< HEAD
    logging.info('You\'ve selected "{}"'.format(dropdown_value))
    image_file = os.path.join(IMAGES_DIR, dropdown_value)

=======
    print('You\'ve selected "{}"'.format(dropdown_value))
    image_file = os.path.join(image_directory, dropdown_value)
>>>>>>> 7f81a690992808269b67a0935fccfbecb7f8bfef
    global current_image_object
    logging.info('Start model scoring..')
    data_raw = model_scoring.predict(image_file)
    data = data_raw
    data['features'] = { 
        x['key']: {
            'value': x['value'],
            'score': x['score']
        } for x in data_raw['features']
    }
    print(data)
    current_image_object = data
    logging.info('End model scoring')

    return json.dumps(current_image_object)


@app.callback(
    Output('output-save', 'children'),
    [Input('save-button', 'n_clicks')],
    [dash.dependencies.State('data-container2', 'accessKey'),
     dash.dependencies.State('testdiv', 'value')]
)
def save_correct_data(_, json_string, x2):
    print('save button geklikt')
    print(json_string)
    print(x2)
    if json_string is None or json_string == '{}':
        return ''
    features = json.loads(json_string)
    data_output = current_image_object
    print(data_output)
    data_output['features'] = features
    try:
        filepath = './data/checked/{}.json'.format(data_output)
        print("Saving data to {}".format(filepath))
        with open(filepath, 'w') as f:
            json.dump(data_output, f)
        return 'Data saved'
    except Exception as e:
        print(e)
        return 'Saving failed'


if __name__ == '__main__':
    app.run_server(debug=True)