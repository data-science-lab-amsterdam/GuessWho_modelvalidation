from abc import ABC, abstractmethod
import json
import numpy as np
import logging
import time


def random_from(my_list):
    my_list = list(my_list)
    return my_list[np.random.randint(0, len(my_list))]


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
        logging.info("Answering question if {} is {} for character '{}'".format(k, v, character['name']))
        answer = character['properties'][k] == v
        return True, answer

    def answer_guess(self, player_name, character, character_name):
        if self.whose_turn_is_it != player_name:
            logging.warning("Wait for your turn!")
            return False, None

        answer = character['name'] == character_name
        return True, answer

    def end_turn(self):
        if self.whose_turn_is_it == 'human':
            self.whose_turn_is_it = 'computer'
        else:
            self.whose_turn_is_it = 'human'

    def do_computer_move(self):
        time.sleep(self.SLEEP_BETWEEN_TURNS)
        game_finished, updated_board = self.computer_player.move()
        self.end_turn()
        return game_finished, updated_board


class Board:

    def __init__(self, data):
        self.data = data

    def __iter__(self):
        return iter(self.data)

    def get_characters(self):
        return self.data

    def get_character_by_name(self, name):
        for character in self.data:
            if character['name'] == name:
                return character
        raise ValueError("Character '{}' not found".format(name))

    def get_character_by_id(self, id):
        for character in self.data:
            if character['id'] == id:
                return character
        raise ValueError("Character '{}' not found".format(id))

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

    def guess_character(self, character_name):
        ok, answer = self.game.answer_guess(self.name, self.character, character_name)
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
        logging.info('{} options left'.format(sum(self.options.values())))
        if sum(self.options.values()) == 1:
            id = [k for k, v in self.options.items() if v][0]
            character = self.board.get_character_by_id(id)
            ok, answer = self.guess_character(character)
            if answer:
                return True, self.options

        question = self._find_question()
        ok, answer = self.ask_question(question)
        if not ok:
            logging.error(question)
            raise ValueError("Could not answer question")

        self._update_board(question, answer)
        return False, self.options

    def _find_question(self):
        k = random_from(self.board.get_properties())
        v = random_from(self.board.get_property_options(k))
        logging.info('Computer\'s question: {}: {}'.format(k, v))
        return k, v

    def _update_board(self, question, answer):
        k, v = question
        for character in self.board:
            if (character['properties'][k] == v) != answer:
                self.options[character['id']] = False
