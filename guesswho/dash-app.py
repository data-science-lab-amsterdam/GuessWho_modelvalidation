
import numpy as np
import glob
import os
import json
import logging
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import flask

from game import *

logging.basicConfig(level=logging.INFO)

game = GuessWhoGame(data_file='./guesswho/data/test.json')


# characters = [
#     {'name': os.path.splitext(os.path.basename(filename))[0].split('-')[0],
#      'file': filename
#      } for filename in glob.glob('./images/*.jpg')
# ]
characters = game.get_characters()
questions = game.PROPERTIES
initial_hidden_state = json.dumps({c['id']: True for c in characters})
default_image = './images/unknown.jpg'


def create_test_data(out_file):
    idx = 0
    data = []
    for c in characters:
        idx += 1
        x = c
        x['id'] = idx
        x['properties'] = {}
        for k, v in questions.items():
            choice = np.random.randint(0, len(v))
            x['properties'][k] = v[choice]
        data.append(x)
    with open(out_file, 'w') as f:
        json.dump(data, f)


#create_test_data('./guesswho/data/test.json')

def get_character_options():
    return [{'label': c['name'], 'value': c['name']} for c in game.board.get_characters()]


def get_question_type_options():
    return [{'label': x, 'value': x} for x in questions.keys()]


def get_question_value_options(question_type):
    return [{'label': x, 'value': x} for x in questions[question_type]]


def get_answer(question_type, question_value):
    ok = question_type is not None and question_value is not None
    if not ok:
        return False, False

    ok, answer = game.human_player.ask_question((question_type, question_value))
    return ok, answer


def guess_character(name):
    ok, answer = game.human_player.guess_character(name)
    return ok, answer

# def render_board_characters(player_id):
#     elements = []
#     for c in characters:
#         elements.append(html.Div(className='xcolumn is-1', children=[
#             html.A(
#                 id='a-p{}-character-{}'.format(player_id, c['id']),
#                 href="javascript:clickCharacter({}, {})".format(player_id, c['id']),
#                 n_clicks=0,
#                 children=[
#                     html.Div(className='has-text-centered', children=[
#                         html.Img(id='img-p{}-character-{}'.format(player_id, c['id']), className='character-image', src=c['file']),
#                         html.Figcaption(c['name'])
#                     ])
#                 ]
#             )
#         ]))
#     return html.Div(className='xcolumns is-gapless is-multiline', children=elements)
def render_board_characters(player_id):
    elements = []
    for c in characters:
        elements.append(#html.Div(className='xcolumn is-inline', children=[
            html.A(
                id='a-p{}-character-{}'.format(player_id, c['id']),
                href="javascript:clickCharacter({}, {})".format(player_id, c['id']),
                n_clicks=0,
                children=[
                    html.Figure(className='character-container has-text-centered', children=[
                        html.Img(id='img-p{}-character-{}'.format(player_id, c['id']), className='character-image', src=c['file']),
                        html.Figcaption(className='character-caption', children=c['name'])
                    ])
                ]
            )
        )#]))
    return elements


def bulma_with_label(component, label):
    """
    Handle boiler plate stuff for putting a label on a dcc / input field
    """
    return html.Div(className='field', children=[
        html.Label(className='label', children=label),
        html.Div(className='control', children=[
            component
        ])
    ])


def bulma_center(component):
    return html.Div(className='columns', children=[
        html.Div(className='column', children=[]),
        html.Div(className='column has-text-centered', children=[component]),
        html.Div(className='column', children=[])
    ])


def bulma_columns(components):
    return html.Div(className='columns', children=[
        html.Div(className='column has-text-centered', children=[c]) for c in components
    ])


app = dash.Dash()

app.css.append_css({'external_url': 'https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.1/css/bulma.min.css'})

app.layout = html.Div(children=[
    bulma_columns([
        html.Img(className='header-logo', src='./images/guesswho_logo.png'),
        '',
        html.Img(className='header-logo', src='./images/Logo_datasciencelab.png')
    ]),

    # Computer player board
    html.Div(className='character-board panel', children=[
        html.P(className="panel-heading", children="Computer"),
        html.Div(className="panel-block is-block", children=[
            html.Div(id="computer-board", children=render_board_characters(player_id=1)),
            html.Progress(id='computer-progress', className="progress is-info", value="0", max="100"),
            html.Div(id='output-hidden-state', accessKey=initial_hidden_state)
        ])
    ]),

    # Select computer character
    bulma_center(
        html.Div(id='computer-character', className='level', children=[
            html.Div(className='level-left', children=[
                html.Div(className='level-item', children=[
                    bulma_with_label(component=dcc.Dropdown(id='input-character-select', options=get_character_options()),
                                     label='Opponent\'s character'
                                     )
                ]),
                html.Div(className='level-item', children=[
                    html.Img(id='output-selected-character', src=default_image)
                ])
            ]),
            html.Div(className='level-right', children=[])
        ])
    ),

    # Human player board
    html.Div(className='character-board panel', children=[
        html.P(id="player-name", className="panel-heading", children="Player"),
        html.Div(className="panel-block is-block", children=[
            html.Div(id='player-board', children=render_board_characters(player_id=2)),
            html.Progress(id='player-progress', className="progress is-danger", value="0", max="100"),
            html.Div(className='columns', children=[
                html.Div(className='column', children=[
                    html.H4('Select your next question:')
                ]),
                html.Div(className='column', children=[
                    html.Span('Category:'),
                    dcc.Dropdown(id='input-question-type', options=get_question_type_options(), multi=False)
                ]),
                html.Div(className='column', children=[
                    html.Span('Options:'),
                    dcc.Dropdown(id='input-question-value', options=[], multi=False)
                ]),
                html.Div(className='column', children=[
                    html.Button(id='input-question-button', className='button is-info is-large', n_clicks=0, children='Ask!')
                ])
            ]),
            html.Div(className='columns', children=[
                html.Div(className='column', children=[
                    html.H4('...or make a guess!')
                ]),
                html.Div(className='column is-half', children=[
                    html.Span('Pick a character:'),
                    dcc.Dropdown(id='input-character-guess', options=get_character_options(), multi=False)
                ]),
                html.Div(className='column', children=[
                    html.Button(id='input-guess-button', className='button is-info is-large', n_clicks=0, children='Guess!')
                ])
            ]),
            html.Div([
                bulma_with_label(component=html.Div(id='output-question-answer', children=''),
                                 label='Answer'
                                 ),
                html.Div(id='output-guess-answer', children='')
            ])
        ])
    ]),

    # Bottom part
    bulma_center(
        html.Button(id='input-endturn-button', className='button is-info is-large', n_clicks=0, children='End turn')
    ),

    html.Div(className='modal', id='end-modal', children=[
        html.Div(className='modal-background'),
        html.Div(className='modal-content', id='end-modal-content', children=''),
    ]),

    html.Div(' ', id='spacer')
])


@app.server.route('/images/<path:path>')
def serve_images(path):
    root_dir = os.getcwd()
    return flask.send_from_directory(os.path.join(root_dir, 'images'), path)


@app.callback(
    Output(component_id='output-selected-character', component_property='src'),
    [Input(component_id='input-character-select', component_property='value')]
)
def select_character(name):
    if name is None:
        return default_image
    for c in characters:
        if c['name'] == name:
            game.set_computer_character(name)
            return c['file']
    raise ValueError("Character '{}' not found".format(name))


@app.callback(
    Output(component_id='input-question-value', component_property='options'),
    [Input(component_id='input-question-type', component_property='value')]
)
def set_question_options(question_type):
    if question_type is None:
        return []
    return get_question_value_options(question_type)


@app.callback(
    Output('output-question-answer', 'children'),
    [Input('input-question-button', 'n_clicks')],
    [State('input-question-type', 'value'),
     State('input-question-value', 'value')],
)
def ask_question(_, question_type, question_value):
    if _ is None or _ == 0:
        return ''
    logging.info('{}: {}'.format(question_type, question_value))
    ok, answer = get_answer(question_type, question_value)
    if not ok:
        return ''
    else:
        return '{}, {} {} {}'.format(
            'Yes' if answer else 'No',
            question_type,
            'is' if answer else 'isn\'t',
            question_value
        )


@app.callback(
    Output('output-guess-answer', 'children'),
    [Input('input-guess-button', 'n_clicks')],
    [State('input-character-guess', 'value')],
)
def make_guess(_, character_name):
    if _ is None or _ == 0:
        return ''
    logging.info('Player is guessing for character {}'.format(character_name))
    ok, answer = guess_character(character_name)
    if not ok:
        return ''
    if answer:
        return 'Correct! You\'ve won the game!'
    else:
        return 'Too bad. That\'s not correct'


@app.callback(
    Output('output-hidden-state', 'accessKey'),
    [Input('input-endturn-button', 'n_clicks')]
)
def end_human_turn(_):
    if _ is None or _ == 0:
        return initial_hidden_state
    game.end_turn()
    game_finished, updated_computer_board = game.do_computer_move()
    if game_finished:
        logging.info("Computer has won!")
        return 'FINISHED'
    else:
        logging.info(updated_computer_board)
        return json.dumps(updated_computer_board)


if __name__ == '__main__':
    app.run_server(debug=True, port=8123)
