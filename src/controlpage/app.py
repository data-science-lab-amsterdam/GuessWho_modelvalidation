import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import os
import flask
import glob
import json

from models.Complete_Model import main_model

cwd = os.getcwd()
image_directory = os.path.join(cwd, 'data/images/faces/')
list_of_images = [os.path.basename(x) for x in glob.glob(os.path.join(image_directory, '*.jpeg')) if 'dummy.jpeg.png' not in x]
static_image_route = '/static/'
feature_keys = ['hair_colour', 'hair_type', 'hair_length', 'gender', 'hat', 'glasses', 'necklace', 'facial_hair']

current_image_object = None


def bulma_field(label, component):
    """
    Handle boiler plate stuff for putting a label on a dcc / input field
    """
    return html.Div(className='field', children=[
        html.Label(className='label', children=label),
        html.Div(className='control', children=[component])
    ])


def bulma_dropdown(id, options):
    return html.Div(id=id, className='select', children=[
        html.Select([
            html.Option(value=o['value'], children=o['label']) for o in options
        ])
    ])


app = dash.Dash()

app.layout = html.Div([
    html.H1(children='Choose player'),
    dcc.Dropdown(
        id='image-dropdown',
        options=[{'label': i, 'value': i} for i in list_of_images],
        value=''
    ),
    html.Img(id='image', src='/assets/dummy.png'),
    html.Div(id='data-container', accessKey='{}'),
    html.Div(id='data-container2', accessKey='{}'),
    html.Div(className='columns', children=[
        html.Div(className='column', children=[
            bulma_field(label='Haarkleur', component=bulma_dropdown(id='input-hair_colour', 
                options=[{'label': 'licht', 'value': 'light'},
                        {'label': 'Donker', 'value': 'dark'}])),

            bulma_field(label='Haartype', component=bulma_dropdown(id='input-hair_type', 
                options=[{'label': 'krullend', 'value': 'curly'},
                {'label': 'stijl', 'value': 'straight'}])),

            bulma_field(label='Haarlengte', component=bulma_dropdown(id='input-hair_length', 
                options=[{'label': 'kaal', 'value': 'bold'},
                {'label': 'kort', 'value': 'short'},
                {'label': 'lang', 'value': 'long'}])),

            bulma_field(label='Geslacht', component=bulma_dropdown(id='input-gender', 
                options=[{'label': 'Man', 'value': 'male'},
                        {'label': 'Vrouw', 'value': 'female'}])),

            bulma_field(label='Hoed of pet', component=bulma_dropdown(id='input-hat', 
                options=[{'label': 'Hoed', 'value': 'hat'},
                        {'label': 'Pet', 'value': 'cap'},
                        {'label': 'Geen', 'value': 'none'}]
                )),

            bulma_field(label='Bril', component=bulma_dropdown(id='input-glasses', 
                options=[{'label': 'Bril', 'value': 'yes'},
                        {'label': 'Geen Bril', 'value': 'no'}]
                )),

            bulma_field(label='Accessories', component=bulma_dropdown(id='input-necklace', 
                options=[{'label': 'kleine ketting', 'value': 'necklace'},
                        {'label': 'grote ketting', 'value': 'chain'},
                        {'label': 'geen ketting', 'value': 'none'}]
                        )),

            bulma_field(label='Gezichtsbeharing', component=bulma_dropdown(id='input-facial_hair', 
                options=[{'label': 'Baard', 'value': 'beard'},
                        {'label': 'Snor', 'value': 'snor'},
                        {'label': 'Geen gezichtsbeharing', 'value': 'none'}]
                        ))
            ])
        ]),
    # dcc.Input(id='hidden-hair_colour', type='hidden', value=''),
    # dcc.Input(id='hidden-hair_length', type='hidden', value=''),
    # dcc.Input(id='hidden-hair_length', type='hidden', value=''),
    # dcc.Input(id='hidden-gender', type='hidden', value=''),
    # dcc.Input(id='hidden-hat', type='hidden', value=''),
    # dcc.Input(id='hidden-glasses', type='hidden', value=''),
    # dcc.Input(id='hidden-necklace', type='hidden', value='')

    # html.Div([dcc.Input(id='input-{}'.format(x), type='text', value='') for x in feature_keys]),
    
    # html.Div(dcc.Input(id='input-hair_colour')),
    # html.Div(dcc.Input(id='input-hair_type')),
    # html.Div(dcc.Input(id='input-gender')),
    # html.Div(dcc.Input(id='input-glasses')),
    # html.Div(dcc.Input(id='input-hair_length')),
    # html.Div(dcc.Input(id='input-facial_hair')),
    # html.Div(dcc.Input(id='input-hat')),
    # html.Div(dcc.Input(id='input-necklace')),
    html.Button('Correct', id='save-button', n_clicks=0),
    html.Div(id='output-save', children='')
])


@app.server.route('/<path:path>')
def serve_images(path):
    """
    Pass local images to the web server
    """
    print(path)
    root_dir = os.getcwd()
    # return flask.send_from_directory(os.path.join(root_dir, 'data/images/faces'), path)
    return flask.send_from_directory(image_directory, path)


@app.callback(
    dash.dependencies.Output('image', 'src'),
    [dash.dependencies.Input('image-dropdown', 'value')]
)
def update_image_src(value):
    """
    Show the selected image
    """
    if value is None or value == '':
        return '/assets/dummy.png'
    return os.path.join(image_directory, value)


@app.callback(
    dash.dependencies.Output('data-container', 'accessKey'),
    [dash.dependencies.Input('image-dropdown', 'value')]
)
def choose_image(dropdown_value):
    """
    Use selected image to score model on and return estimated features
    """
    if dropdown_value is None or dropdown_value == '':
        return ''
    print('You\'ve selected "{}"'.format(dropdown_value))
    image_file = os.path.join(image_directory, dropdown_value)
    global current_image_object
    print('model caluculation..')
    data_raw = main_model.main_model(image_file)
    data = data_raw
    data['features'] = { 
        x['key']: {
            'value': x['value'],
            'score': x['score']
        } for x in data_raw['features']
    }
    print(data)
    current_image_object = data
    print('model done calculating')
    # return data
    return json.dumps(current_image_object)


@app.callback(
    dash.dependencies.Output('output-save', 'children'),
    [dash.dependencies.Input('data-container2', 'accessKey')]
)
def save_correct_data(json_string):
    features = json.loads(json_string)
    data_output = current_image_object
    print(data_output)
    data_output['features'] = features
    try:
        filepath = './data/checked/{}.json'.format(data_output)
        print("Saving data to {}".format(filepath))
        with open(filepath, 'w') as f:
            json.dump(data_output, f)
        return True
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    app.run_server(debug=True)