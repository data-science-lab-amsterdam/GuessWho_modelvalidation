
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


def render_board_characters(player_id):
    elements = []
    for c in characters:
        elements.append(html.A(
            id='a-p{}-character-{}'.format(player_id, c['id']),
            href="javascript:clickCharacter({}, {})".format(player_id, c['id']),
            n_clicks=0,
            children=html.Img(id='img-p{}-character-{}'.format(player_id, c['id']), className='character-image', src=c['file'])
        ))
    return elements


def dcc_with_label(component, label):
    """
    Handle boiler plate stuff for putting a label on a dcc / input field
    """
    return html.Div(className='field', children=[
        html.Label(className='label', children=label),
        html.Div(className='control', children=[
            component
        ])
    ])


app = dash.Dash()

app.css.append_css({'external_url': 'https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.1/css/bulma.min.css'})

app.layout = html.Div(children=[
    html.H1(className='title is-1', children='Guess Who??'),

    html.Div(className='character-board', children=[
        html.H3("Computer"),
        html.Div(id="computer-board", children=render_board_characters(player_id=1)),
        html.Progress(id='computer-progress', className="progress is-danger", value="0", max="100"),
        html.Hr(),
        html.Div(className='level', children=[
            html.Div(className='level-left', children=[
                html.Div(className='level-item', children=[
                    dcc_with_label(component=dcc.Dropdown(id='input-character-select', options=get_character_options()),
                                   label='Opponent\'s character'
                                   )
                ]),
                html.Div(className='level-item', children=[
                    html.Img(id='output-selected-character', src='./images/unknown.jpg')
                ])
            ]),
            html.Div(className='level-right', children=[])
        ]),
        dcc.Input(id='output-hidden-state', type='hidden', value={c['id']: True for c in characters})
    ]),

    html.Div(className='character-board', children=[
        html.H3(id="player-name", children="Player 1"),
        html.Div(id='player-board', children=render_board_characters(player_id=2)),
        # html.Div(className='columns', children=[
        #     html.Div(className='column is-one-fifth', children='Computer progress'),
        #     html.Div(className='column', children=[
        #         html.Progress(id='player-progress', className="progress is-info", value="0", max="100")
        #     ])
        # ]),
        html.Progress(id='player-progress', className="progress is-info", value="0", max="100"),
        html.Div(className='columns', children=[
            html.Div(className='column', children=[
                html.H4('Select your next question:')
            ]),
            html.Div(className='column', children=[
                html.Span('Category:'),
                dcc.RadioItems(id='input-question-type', options=get_question_type_options(), labelStyle={'display': 'block', 'padding-left': '2px'})
            ]),
            html.Div(className='column', children=[
                html.Span('Options:'),
                dcc.RadioItems(id='input-question-value', options=[], labelStyle={'display': 'block'})
            ]),
            html.Div(className='column', children=[
                html.Button(id='input-question-button', className='button is-primary is-large', n_clicks=0, children='Ask!')
            ])
        ]),
        html.Div([
            dcc_with_label(component=dcc.Input(id='output-answer', className='input is-large is-info', disabled=True, readonly=True),
                           label='Answer'
                           )
        ]),
        html.Button(id='input-endturn-button', className='button is-primary is-large', n_clicks=0, children='End turn')
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
    return get_question_value_options(question_type)


@app.callback(
    Output('output-answer', 'value'),
    [Input('input-question-button', 'n_clicks')],
    [State('input-question-type', 'value'),
     State('input-question-value', 'value')],
)
def ask_question(_, question_type, question_value):
    logging.info(question_type, question_value)
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
    Output('output-hidden-state', 'value'),
    [Input('input-endturn-button', 'n_clicks')]
)
def end_human_turn(_):
    game.end_turn()
    updated_computer_board = game.do_computer_move()
    return updated_computer_board

# for i, c in enumerate(characters):
#     @app.callback(
#         Output(component_id='img-p2-character-{}'.format(i), component_property='src'),
#         [Input(component_id='a-p2-character-{}'.format(i), component_property='n_clicks')]
#     )
#     def flip_character(n_clicks):
#         return './images/closed.jpg'

if __name__ == '__main__':
    app.run_server(debug=True, port=8123)
