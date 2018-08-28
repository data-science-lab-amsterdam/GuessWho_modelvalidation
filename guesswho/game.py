from abc import ABC, abstractmethod
import json
import numpy as np
import logging
import time


def random_from(mylist):
    mylist = list(mylist)
    return mylist[np.random.randint(0, len(mylist))]


class GuessWhoGame:

    SLEEP_BETWEEN_TURNS = 2
    PROPERTIES = {
        'hair color': ['dark', 'light', 'none'],
        'hair length': ['short', 'long', 'bald'],
        'hair type': ['curly', 'straight'],
        'glasses': ['yes', 'no'],
        'head wear': ['hat', 'cap', 'none'],
        'sex': ['male', 'female'],
        'facial hair': ['beard', 'moustache', 'none'],
        'accessories': ['chain', 'necklace', 'none']
    }

    def __init__(self, data_file):
        self.data_file = data_file
        with open(data_file, 'r') as f:
            self.data = json.loads(f.read())

        self.board = Board(self.data)

        self.human_player = HumanPlayer(self, 'human')
        self.computer_player = ComputerPlayer(self, 'computer')
        self.computer_player.set_board(self.board)

        self.human_player.set_character(self.data[np.random.randint(0, len(self.data))])
        self.whose_turn_is_it = random_from(['human', 'computer'])  # randomly choose start player

    def set_computer_character(self, name):
        for x in self.data:
            if x['name'] == name:
                self.computer_player.set_character(x)
                return
        raise ValueError("Invalid name: '{}'".format(name))

    def get_characters(self):
        return [{k: v for k, v in x.items() if k in ['id', 'name', 'file']} for x in self.data]

    def get_question_types(self):
        return self.PROPERTIES.keys()

    def answer_question(self, player_name, character, question):
        if self.whose_turn_is_it != player_name:
            logging.warning("Wait for your turn!")
            return False, None

        k, v = question
        answer = character['properties'][k] == v
        return True, answer

    def end_turn(self):
        if self.whose_turn_is_it == 'human':
            self.whose_turn_is_it = 'computer'
        else:
            self.whose_turn_is_it = 'human'

    def do_computer_move(self):
        time.sleep(self.SLEEP_BETWEEN_TURNS)
        updated_board = self.computer_player.move()
        self.end_turn()
        return updated_board


class Board:

    def __init__(self, data):
        self.data = data

    def __iter__(self):
        return iter(self.data)

    def get_characters(self):
        return self.data

    @staticmethod
    def get_properties():
        return GuessWhoGame.PROPERTIES.keys()

    @staticmethod
    def get_property_options(key):
        return GuessWhoGame.PROPERTIES[key]


class BasePlayer(ABC):

    def __init__(self, game, name):
        super().__init__()
        self.game = game
        self.name = name
        self.is_human = None
        self.character = None

    def set_character(self, character):
        self.character = character

    @abstractmethod
    def move(self):
        pass

    def ask_question(self, question):
        ok, answer = self.game.answer_question(self.name, self.character, question)
        return ok, answer


class HumanPlayer(BasePlayer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_human = True

    def move(self):
        # wait for user to ask a question
        pass


class ComputerPlayer(BasePlayer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_human = False
        self.board = None
        self.options = None

    def set_board(self, board):
        self.board = board
        self.options = {c['id']: True for c in self.board}

    def move(self):
        question = self._find_question()
        ok, answer = self.ask_question(question)
        if not ok:
            logging.error(question)
            raise ValueError("Could not answer question")

        self._update_board(question, answer)
        return self.options

    def _find_question(self):
        k = random_from(self.board.get_properties())
        v = random_from(self.board.get_property_options(k))
        return k, v

    def _update_board(self, question, answer):
        k, v = question
        for character in self.board:
            if (character['properties'][k] == v) != answer:
                self.options[character['id']] = False
