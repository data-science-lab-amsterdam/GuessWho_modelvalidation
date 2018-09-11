import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import os
import flask
import glob
import json
from pathlib import Path
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


def get_image_list():
    all_faces = [os.path.basename(x) for x in glob.glob('./data/images/faces/*.jpg') if 'dummy' not in x]
    checked_faces = [x.stem for x in Path().glob('./data/checked/*json')]
    remaining_faces = [x for x in all_faces if x not in checked_faces]
    return remaining_faces


list_of_images = get_image_list()


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


def bulma_columns(components, extra_classes=None):
    if extra_classes is None:
        extra_classes = ['' for _ in components]
    return html.Div(className='columns is-vcentered', children=[
        html.Div(className='column {}'.format(cls), children=[comp]) for comp, cls in zip(components, extra_classes)
    ])


def bulma_center(component):
    return html.Div(className='columns', children=[
        html.Div(className='column', children=[]),
        html.Div(className='column has-text-centered', children=[component]),
        html.Div(className='column', children=[])
    ])


def bulma_figure(url):
    return html.Figure(className="figure", children=[
        html.Img(src=url),
    ])


def show_field_row(data):
    # return html.Tr([
    #     html.Td([
    #         html.Label(className='label field-label is-vertical-center', children=data['label']),
    #     ]),
    #     html.Td([
    #         dcc.Dropdown(id='input-'+data['value'], className='feature-dropdown is-vertical-center', options=data['options'])
    #     ]),
    #     html.Td([
    #         html.Div('hier komt nog een bar chart met de scores', id='graph-container-'+data['value'], className='graph-container is-vertical-center')
    #     ])
    # ])

    return bulma_columns([
        html.Label(className='label field-label has-text-right', children=data['label']),
        dcc.Dropdown(id='input-' + data['value'],
                     className='feature-dropdown is-vertical-center',
                     options=data['options']
                     ),
        html.Div('hier komt nog een bar chart met de scores',
                 id='graph-container-' + data['value'],
                 className='graph-container is-vertical-center'
                 )
    ], ['has-text-right', '', ''])


app = dash.Dash()

app.layout = html.Div([

    html.Div(className='container is-fluid', children=[

        html.Div('', id='spacer-top'),

        # Choose image
        bulma_columns(
            components=[
                html.H1(children='Kies een foto'),
                dcc.Dropdown(
                    id='image-dropdown',
                    options=[{'label': i, 'value': i} for i in list_of_images],
                    value=''
                ),
                html.Button('Start analyse', id='start-model-button', className='button is-info', n_clicks=0)
            ],
            extra_classes=['', 'is-half', '']
        ),
        bulma_center(
            html.Figure([
                html.Img(id='image', src='/assets/dummy.png')
            ])
        ),

        # hidden json data containers
        html.Div(id='data-container', accessKey='{}'),

        # dropdown field for features
        #html.Table(className='table is-striped', children=[
        ##   html.Tbody([
            html.Div([
                show_field_row(field) for field in feature_data
            ]),
        #]),

        html.Button('Opslaan', id='save-button', className='button is-medium is-success', n_clicks=0),
        html.Div(id='output-save', children=''),

        # modal for when model in scoring
        bulma_modal(id='waiting',
                    content=[
                        html.Img(className='header-logo', src='/assets/web-development.gif'),
                        html.Br(), html.Br(),
                        html.H3('Analyzing image. Please wait...'),
                    ],
                    btn_class='is-hidden',
                    active=False
                    ),
    ]),
    #html.Div(className="container", children=[
        # footer
        html.Footer(className="footer", children=[
            bulma_columns([
                bulma_figure("/assets/tensorflow-logo.png"),
                bulma_figure("/assets/dash-logo-stripe.svg"),
                bulma_figure("/assets/python-logo-generic.svg")
            ])
        ])
    #])
])


@app.server.route('/images/<path:path>')
def serve_images(path):
    """
    Pass local images to the web server
    """
    root_dir = os.getcwd()
    return flask.send_from_directory(os.path.join(root_dir, 'data/images/faces'), path)


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
    logging.info('Selected image: {}'.format(value))
    return os.path.join('/images', value)


@app.callback(
    Output('data-container', 'accessKey'),
    [Input('start-model-button', 'n_clicks')],
    [State('image-dropdown', 'value')]
)
def choose_image(n_clicks, dropdown_value):
    """
    Use selected image to score model on and return estimated features
    """
    if n_clicks is None or n_clicks == 0:
        return ''

    logging.info('You\'ve selected "{}"'.format(dropdown_value))
    image_file = os.path.join(IMAGES_DIR, dropdown_value)

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
    current_image_object = data
    logging.info('End model scoring')

    return json.dumps(current_image_object)


@app.callback(
    Output('input-hair_colour', 'value'),
    [Input('data-container', 'accessKey')]
)
def update_hair_colour(json_string):
    if json_string is None or json_string == '' or json_string == '{}':
        return ''
    data = json.loads(json_string)
    return data['features']['hair_colour']['value']


@app.callback(
    Output('input-hair_type', 'value'),
    [Input('data-container', 'accessKey')]
)
def update_hair_type(json_string):
    if json_string is None or json_string == '' or json_string == '{}':
        return ''
    data = json.loads(json_string)
    return data['features']['hair_type']['value']


@app.callback(
    Output('input-hair_length', 'value'),
    [Input('data-container', 'accessKey')]
)
def update_hair_length(json_string):
    if json_string is None or json_string == '' or json_string == '{}':
        return ''
    data = json.loads(json_string)
    return data['features']['hair_length']['value']


@app.callback(
    Output('input-gender', 'value'),
    [Input('data-container', 'accessKey')]
)
def update_gender(json_string):
    if json_string is None or json_string == '' or json_string == '{}':
        return ''
    data = json.loads(json_string)
    return data['features']['gender']['value']


@app.callback(
    Output('input-glasses', 'value'),
    [Input('data-container', 'accessKey')]
)
def update_glasses(json_string):
    if json_string is None or json_string == '' or json_string == '{}':
        return ''
    data = json.loads(json_string)
    return data['features']['glasses']['value']


@app.callback(
    Output('input-facial_hair', 'value'),
    [Input('data-container', 'accessKey')]
)
def update_facial_hair(json_string):
    if json_string is None or json_string == '' or json_string == '{}':
        return ''
    data = json.loads(json_string)
    return data['features']['facial_hair']['value']


@app.callback(
    Output('input-hat', 'value'),
    [Input('data-container', 'accessKey')]
)
def update_hat(json_string):
    if json_string is None or json_string == '' or json_string == '{}':
        return ''
    data = json.loads(json_string)
    return data['features']['hat']['value']


@app.callback(
    Output('input-tie', 'value'),
    [Input('data-container', 'accessKey')]
)
def update_tie(json_string):
    if json_string is None or json_string == '' or json_string == '{}':
        return ''
    data = json.loads(json_string)
    return data['features']['tie']['value']


@app.callback(
    dash.dependencies.Output('output-save', 'children'),
    [dash.dependencies.Input('save-button', 'n_clicks')],
    [dash.dependencies.State('input-hair_colour', 'value'),
     dash.dependencies.State('input-hair_type', 'value'),
     dash.dependencies.State('input-gender', 'value'),
     dash.dependencies.State('input-glasses', 'value'),
     dash.dependencies.State('input-hair_length', 'value'),
     dash.dependencies.State('input-facial_hair', 'value'),
     dash.dependencies.State('input-hat', 'value'),
     dash.dependencies.State('input-tie', 'value')]
)
def save_data(n_clicks, f_hc, f_ht, f_ge, f_gl, f_hl, f_fh, f_h, f_t):
    if n_clicks is None or n_clicks == 0:
        return ''

    data_output = current_image_object
    data_output['features'] = {
        'hair_colour': f_hc,
        'hair_type': f_ht,
        'hair_length': f_hl,
        'gender': f_ge,
        'glasses': f_gl,
        'facial_hair': f_fh,
        'hat': f_h,
        'tie': f_t
    }
    try:
        filepath = './data/checked/{}.json'.format(data_output['name'])
        print("Saving data to {}".format(filepath))
        with open(filepath, 'w') as f:
            json.dump(data_output, f)
        return 'Data saved'
    except Exception as e:
        print(e)
        return 'Saving failed'


if __name__ == '__main__':
    app.run_server(debug=True)