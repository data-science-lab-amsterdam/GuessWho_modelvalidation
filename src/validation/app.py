import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import os
import flask
import re
import json
from pathlib import Path
import logging
import face_recognition
from skimage import io

import model_scoring
from crop_faces import crop_image


logging.basicConfig(level=logging.INFO)

RAW_IMAGES_DIR = './data/images/faces'
CHECKED_IMAGES_DIR = './data/images/faces_checked'
CHECKED_DATA_DIR = './data/labels_checked'

current_image_data = None

feature_data = [
    {
        'label': 'Hair colour',
        'value': 'hair_colour',
        'options': [
            {'label': 'licht', 'value': 'light'},
            {'label': 'Dark', 'value': 'dark'},
            {'label': 'te kort', 'value': 'too_short'}
        ]
    }, {
        'label': 'Hair type',
        'value': 'hair_type',
        'options': [
            {'label': 'krullend', 'value': 'curly'},
            {'label': 'Straight', 'value': 'straight'},
            {'label': 'te kort', 'value': 'too_short'}
        ]
    }, {
        'label': 'Hair length',
        'value': 'hair_length',
        'options': [
            {'label': 'kort', 'value': 'short'},
            {'label': 'Long', 'value': 'long'}
        ]
    }, {
        'label': 'Gender',
        'value': 'gender',
        'options': [
            {'label': 'man', 'value': 'male'},
            {'label': 'Female', 'value': 'female'}
        ]
    }, {
        'label': 'Hat',
        'value': 'hat',
        'options': [
            {'label': 'Yes', 'value': 'yes'},
            {'label': 'No', 'value': 'no'}
        ]
    }, {
        'label': 'Glasses',
        'value': 'glasses',
        'options': [
            {'label': 'Yes', 'value': 'yes'},
            {'label': 'No', 'value': 'no'}
        ]
    }, {
        'label': 'Tie',
        'value': 'tie',
        'options': [
            {'label': 'Yes', 'value': 'yes'},
            {'label': 'No', 'value': 'no'}
        ]
    }, {
        'label': 'Facial hair',
        'value': 'facial_hair',
        'options': [
            {'label': 'Yes', 'value': 'yes'},
            {'label': 'nee', 'value': 'no'}
        ]
    }
]

feature_keys = [x['value'] for x in feature_data]


def get_image_list(last_n=10):
    """
    Get a list of raw image files that have not been checked yet
    """
    all_faces = [x for x in Path(RAW_IMAGES_DIR).glob('*.jpg') if 'dummy' not in x.stem]
    recent_faces = sorted(all_faces, key=os.path.getmtime, reverse=True)[:last_n]
    checked_faces = [x.stem for x in Path(CHECKED_DATA_DIR).glob('*.json')]
    remaining_faces = [x for x in recent_faces if x.name not in checked_faces]
    if len(remaining_faces) == 0:
        remaining_faces = recent_faces

    return [x.name for x in remaining_faces]


def get_image_dropdown_options():
    return [{'label': i, 'value': i} for i in get_image_list()]


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
    return html.Figure(className="figure has-text-centered", children=[
        html.Img(src=url),
    ])


def show_field_row(data):
    return bulma_columns([
        html.Label(className='label field-label has-text-right', children=data['label']),
        dcc.Dropdown(id='input-' + data['value'],
                     className='feature-dropdown is-vertical-center',
                     options=data['options']
                     ),
        html.Div(id='graph-container-' + data['value'],
                 className='graph-container is-vertical-center'
                 )
    ], ['has-text-right', '', ''])


def crop_image_to_face(img_file):
    image_rgb = face_recognition.load_image_file(img_file)

    # run the face detection model to find face locations
    try:
        face_location = face_recognition.face_locations(image_rgb)[0]
        (top, right, bottom, left) = face_location
        area = (left, top, bottom - top, right - left)
        cropped_image = crop_image(image_rgb, area, padding=0.25)
    except Exception as e:
        print("Error during cropping to face. Using original image.")
        print(e)
        cropped_image = image_rgb

    img_file_out = str(Path(CHECKED_IMAGES_DIR) / Path(img_file).name)
    io.imsave(img_file_out, cropped_image)
    return img_file_out


app = dash.Dash()
#app.config['suppress_callback_exceptions'] = True
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

app.layout = html.Div([

    html.Div(className='container is-fluid', children=[

        html.Div('', id='spacer-top'),

        # Choose image
        bulma_columns(
            components=[
                html.Button('Update', id='update-button', className='button is-info', n_clicks=0),
                html.H1(children='Choose image'),
                dcc.Dropdown(
                    id='image-dropdown',
                    options=get_image_dropdown_options(),
                    value=''
                ),
                html.Button('Start analysing', id='start-model-button', className='button is-info', n_clicks=0)
            ],
            extra_classes=['', 'has-text-right', 'is-half', '']
        ),

        html.Div(className='box', children=[
            # image placeholders
            bulma_columns([
                '',
                html.Figure(className="image", children=[
                    html.Caption(className="caption", children="Original image"),
                    html.Img(id='image', src='/images/controlpage/dummy.png'),
                ]),
                html.Figure(className="image", children=[
                    html.Caption(className="caption", children="Detected face"),
                    html.Img(id='cropped-image', src='/images/controlpage/dummy.png'),
                ]),
                ''
            ]),

            # hidden json data containers
            html.Div(id='data-container', accessKey='{}'),

            # field for character name
            bulma_columns([
                html.Label(className='label field-label has-text-right', children='Name'),
                dcc.Input(id='input-character-name', className='input', type='text', value='', placeholder='Enter a name for the avatar...', maxlength=10),
                html.Div('')
            ]),

            # dropdown field for features
            html.Div([
                show_field_row(field) for field in feature_data
            ]),
        ]),

        # save button
        bulma_center(
            html.Div([
                html.Button('Save', id='save-button', className='button is-medium is-success', n_clicks=0)
            ])
        ),

        bulma_modal(id='end',
                    content='Data opgeslagen!',
                    btn_class='is-success',
                    active=False
                    ),

        # modal for when model in scoring
        bulma_modal(id='waiting',
                    content=[
                        html.Img(className='header-logo', src='/images/controlpage/web-development.gif'),
                        html.Br(), html.Br(),
                        html.H3(id='waiting-text', children='Analyzing image | Running face detection | Scoring Tensorflow models | Please wait...'),
                    ],
                    btn_class='is-hidden',
                    active=False
                    ),
    ]),

    # footer
    html.Footer(className="footer", children=[
        bulma_columns([
            bulma_figure("/images/controlpage/python-logo-generic.svg"),
            bulma_figure("/images/controlpage/tensorflow-logo.png"),
            bulma_figure("/images/controlpage/dash-logo-stripe.svg"),
            bulma_figure("/images/controlpage/bulma_logo.png"),
            bulma_figure("/images/game/Logo_datasciencelab.png")
        ])
    ])
])


@app.server.route('/images/<path:path>')
def serve_images(path):
    """
    Pass local images to the web server
    """
    root_dir = os.getcwd()
    return flask.send_from_directory(os.path.join(root_dir, 'data/images'), path)


@app.callback(
    Output('image-dropdown', 'options'),
    [Input('update-button', 'n_clicks')]
)
def update_source_images(_):
    return get_image_dropdown_options()


@app.callback(
    Output('image', 'src'),
    [Input('image-dropdown', 'value')]
)
def update_image_src(value):
    """
    Show the selected image
    """
    if value is None or value == '':
        return '/images/controlpage/dummy.png'
    logging.info('Selected image: {}'.format(value))
    return os.path.join('/images/faces', value)


@app.callback(
    Output('cropped-image', 'src'),
    [Input('image-dropdown', 'value')]
)
def update_cropped_image_src(_):
    """
    Show the selected image
    """
    return '/images/controlpage/dummy.png'


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
    image_file = Path(RAW_IMAGES_DIR) / dropdown_value

    cropped_img_file = crop_image_to_face(image_file)

    global current_image_data
    logging.info('Start model scoring..')
    data_raw = model_scoring.predict(cropped_img_file)
    data = data_raw
    data['url'] = cropped_img_file
    data['filename'] = Path(cropped_img_file).name
    data['features'] = {
        x['key']: {
            'value': x['value'],
            'score': x['score']
        } for x in data_raw['features']
    }
    current_image_data = data
    logging.info('End model scoring')

    return json.dumps(current_image_data)


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
    Output('end-modal', 'className'),
    [Input('save-button', 'n_clicks')],
    [State('input-character-name', 'value'),
     State('input-hair_colour', 'value'),
     State('input-hair_type', 'value'),
     State('input-gender', 'value'),
     State('input-glasses', 'value'),
     State('input-hair_length', 'value'),
     State('input-facial_hair', 'value'),
     State('input-hat', 'value'),
     State('input-tie', 'value')]
)
def save_data(n_clicks, name, f_hc, f_ht, f_ge, f_gl, f_hl, f_fh, f_h, f_t):
    if n_clicks is None or n_clicks == 0:
        return 'modal'

    data_output = current_image_data
    data_output['name'] = re.sub('[^\w_.)( -]', '', name)
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
        data_filepath = '{}/{}.json'.format(CHECKED_DATA_DIR, data_output['filename'])
        logging.info("Saving data to {}".format(data_filepath))
        with open(data_filepath, 'w') as f:
            json.dump(data_output, f)
    except Exception as e:
        print(e)

    return 'modal is-active'


if __name__ == '__main__':
    app.run_server(debug=True)
