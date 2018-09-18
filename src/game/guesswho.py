from abc import ABC, abstractmethod
import json
import os
import numpy as np
import pandas as pd
import logging
import time
from pathlib import Path


def random_from(my_list):
    """
    Select a random element from a list
    """
    my_list = list(my_list)
    return my_list[np.random.randint(0, len(my_list))]


def create_probability_list(amount_of_numbers):
    """
    An exponentially decreasing (sort of) list of probabilities
    """
    # Create logarithmic discounter
    numbers = [x / 100 for x in reversed(np.logspace(0.1, stop=2, num=amount_of_numbers))]

    # Crunch these in a softmax so they sum to 1
    def softmax(x):
        """Compute softmax values for each sets of scores in x."""
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum()

    return softmax(numbers)


class GuessWhoGame:
    """
    Game controller class
    """
    NUM_CHARACTERS = 18
    SLEEP_BETWEEN_TURNS = 1
    PROPERTIES = {
        'hair_colour': ['dark', 'light', 'too_short'],
        'hair_length': ['short', 'long'],
        'hair_type': ['curly', 'straight', 'too_short'],
        'glasses': ['yes', 'no'],
        'hat': ['yes', 'no'],
        'gender': ['male', 'female'],
        'facial_hair': ['yes', 'no'],
        'tie': ['yes', 'no']
    }

    def __init__(self, data_dir):
        logging.info("Game reset")
        self.data_dir = data_dir
        self.data = self._read_data()

        self.board = Board(self.data)

        self.human_player = HumanPlayer(self, 'human')
        self.computer_player = ComputerPlayer(self, 'computer')
        self.computer_player.set_board(self.board)

        self.human_player.set_character(random_from(self.data))
        #self.whose_turn_is_it = random_from(['human', 'computer'])  # randomly choose start player
        self.whose_turn_is_it = 'human'
        self.player_has_made_a_move = False
        self.game_has_started = False

    def _read_data(self):
        all_data = []
        filenames = Path(self.data_dir).glob('*.json')
        most_recent_files = sorted([str(f) for f in filenames], key=os.path.getmtime, reverse=True)[:self.NUM_CHARACTERS]
        logging.info('Most recent file: {}'.format(most_recent_files[0]))
        for filename in most_recent_files:
            with open(str(filename), 'r') as f:
                data = json.loads(f.read())
                data['id'] = data['url']
                all_data.append(data)
        return all_data

    def set_computer_character(self, name):
        """
        Sets the computer player's character for a game
        """
        if self.game_has_started:
            logging.warning("Game has already started. Cannot change computer character")
            return

        for x in self.data:
            if x['name'] == name:
                self.computer_player.set_character(x)
                return
        raise ValueError("Invalid name: '{}'".format(name))

    def set_computer_mode(self, mode):
        """
        Set difficulty level, either 'best' or 'random'
        """
        if mode == 'best':
            self.computer_player.MODE = 'best'
        elif mode == 'random':
            self.computer_player.MODE = 'random'
        else:
            raise ValueError("Invalid mode: {}".format(mode))

    def get_characters(self):
        """
        Get the character items, without the properties
        """
        return [{k: v for k, v in x.items() if k in ['id', 'name', 'url']} for x in self.data]

    def get_question_types(self):
        """
        A list of categories to choose from for a question
        """
        return list(self.PROPERTIES.keys())

    def answer_question(self, player_name, character, question):
        """
        Given a player's question, give the answer
        """
        self.game_has_started = True

        if self.whose_turn_is_it != player_name:
            logging.warning("Wait for your turn!")
            return False, None

        if self.player_has_made_a_move:
            logging.warning("Player has already made a move and needs to end its turn")
            return False, None

        k, v = question
        logging.info("Answering question if {} is {} for character '{}'".format(k, v, character['name']))
        answer = character['features'][k] == v
        logging.info("Answer is {}".format(answer))
        self.player_has_made_a_move = True
        return True, answer

    def answer_guess(self, player_name, player_character, guessed_character):
        """
        Check if a player has guessed the right character
        """
        if self.whose_turn_is_it != player_name:
            logging.warning("Wait for your turn!")
            return False, None

        if self.player_has_made_a_move:
            logging.warning("Player has already made a move and needs to end its turn")
            return False, None

        logging.info('True character id: {}'.format(player_character['id']))
        logging.info('Guessed character id: {}'.format(guessed_character['id']))
        answer = player_character['id'] == guessed_character['id']
        self.player_has_made_a_move = True
        return True, answer

    def end_turn(self):
        """
        Switch turn to other player
        """
        if self.whose_turn_is_it == 'human':
            self.whose_turn_is_it = 'computer'
        else:
            self.whose_turn_is_it = 'human'

        self.player_has_made_a_move = False

    def do_computer_move(self):
        """
        Let the computer player make a move
        """
        time.sleep(self.SLEEP_BETWEEN_TURNS)
        game_finished, updated_board = self.computer_player.move()
        self.end_turn()
        return game_finished, updated_board

    def end(self):
        """
        Reloads the game instance
        """
        self.__init__(self.data_dir)


class Board:

    def __init__(self, data):
        """
        Representation of the board with characters, based on an input data file
        """
        self.data = data

    def __iter__(self):
        return iter(self.data)

    def get_characters(self):
        return self.data

    def get_character_by_name(self, name):
        """
        Lookup character object by name
        """
        for character in self.data:
            if character['name'] == name:
                return character
        raise ValueError("Character '{}' not found".format(name))

    def get_character_by_id(self, id):
        """
        Lookup character object by id
        """
        for character in self.data:
            if character['id'] == id:
                return character
        raise ValueError("Character '{}' not found".format(id))

    @staticmethod
    def get_properties():
        return list(GuessWhoGame.PROPERTIES.keys())

    @staticmethod
    def get_property_options(key):
        """
        Get possible values for a certain property
        """
        return GuessWhoGame.PROPERTIES[key]


class BasePlayer(ABC):

    def __init__(self, game, name):
        """
        Abstract player class, to be extended by either HumanPlayer or ComputerPlayer   
        """
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
        """
        Dispatch a question to the game class to get an answer
        """
        ok, answer = self.game.answer_question(self.name, self.character, question)
        return ok, answer

    def guess_character(self, character):
        """
        Dispatch character guess to the game classs to get an answer
        """
        ok, answer = self.game.answer_guess(self.name, self.character, character)
        return ok, answer


class HumanPlayer(BasePlayer):

    def __init__(self, *args, **kwargs):
        """
        Extension of BasePlayer class, for the human player
        """
        super().__init__(*args, **kwargs)
        self.is_human = True

    def move(self):
        # wait for user to ask a question
        pass


class ComputerPlayer(BasePlayer):

    MODE = 'best'

    def __init__(self, *args, **kwargs):
        """
        Extension of BasePlayer class, for the computer player
        """
        super().__init__(*args, **kwargs)
        self.is_human = False
        self.board = None
        self.options = None
        self.dataframe = None
        self.difficulty = 0.9  # 1 = most difficult, 0 = easiest

    def _set_dataframe(self):
        """
        Transform the properties dict into a dataframe for finding a question
        """
        newrows = []
        for row in self.board.data:
            newrow = {k: v for k, v in row.items() if k in ['id', 'name']}
            newrow.update(row['features'])
            newrow['is_open'] = True
            newrows.append(newrow)
        self.dataframe = pd.DataFrame(newrows).set_index('id')

    def set_board(self, board):
        """
        Assign a board to the player
        """
        self.board = board
        self.options = {c['id']: True for c in self.board}
        self._set_dataframe()

    def move(self):
        """
        Let the computer player choose and execute a move
        """
        logging.info('{} options left'.format(sum(self.options.values())))
        if sum(self.options.values()) == 1:
            id = [k for k, v in self.options.items() if v][0]
            character = self.board.get_character_by_id(id)
            ok, answer = self.guess_character(character)
            if answer:
                computer_move = {
                    'question': ['character', character],
                    'answer': answer,
                    'board': self.options
                }
                return True, computer_move
            else:
                raise ValueError('Only 1 option left, but somehow it isn\'t the right one: {}'.format(character['name']))

        question = self._find_question()
        ok, answer = self.ask_question(question)
        if not ok:
            logging.error(question)
            raise ValueError("Could not answer question")

        self._update_board(question, answer)
        computer_move = {
            'question': list(question),
            'answer': answer,
            'board': self.options
        }
        return False, computer_move

    def _evaluate_question(self, key, value):
        """
        Assess how good a question is
        """
        df = self.dataframe[self.dataframe['is_open']]
        num_options = len(df)
        num_selection = len(df[df[key] == value])
        logging.info('Checking {} = {}: {} out of {}'.format(key, value, num_selection, num_options))
        if num_selection == 0 or num_selection == num_options:
            return 0
        c1 = num_selection / float(num_options)
        c2 = 1 - c1
        probs = np.array([c1, c2])
        entropy = np.sum(-np.log2(probs)*probs)
        return entropy

    def _find_best_question(self):
        """
        Determine which question to ask
        """
        properties = self.board.get_properties()
        num_properties = len(properties)
        max_num_options = np.max([len(self.board.get_property_options(p)) for p in properties])
        scores = np.zeros(shape=(num_properties, max_num_options), dtype='float32')
        for i, key in enumerate(properties):
            for j, value in enumerate(self.board.get_property_options(key)):
                scores[i, j] = self._evaluate_question(key, value)

        logging.info(scores)

        if self.MODE == 'best':
            # select the best option
            idx = np.argmax(scores, axis=None)
        else:
            # select semi-random option
            sorted_idx = np.flip(np.argsort(scores, axis=None), axis=0)
            idx = np.random.choice(len(sorted_idx), 1, p=create_probability_list(len(sorted_idx)))[0]

        logging.info("Best option: {}".format(idx))
        i_sel, j_sel = np.unravel_index(idx, scores.shape)

        k = properties[i_sel]
        v = self.board.get_property_options(k)[j_sel]
        return k, v

    def _find_question(self):
        try:
            k, v = self._find_best_question()
        except Exception as e:
            logging.error("Finding best option failed. Resorting to random option")
            k = random_from(self.board.get_properties())
            v = random_from(self.board.get_property_options(k))
        logging.info('Computer\'s question: {}: {}'.format(k, v))
        return k, v

    def _update_board(self, question, answer):
        """
        Update the board representation (i.e. flip characters) based on the received answer
        """
        k, v = question
        logging.info("Updating board: {}, {}, {}".format(k, v, answer))
        for character in self.board:
            if (character['features'][k] == v) != answer:
                self.options[character['id']] = False
                logging.info('Flipping id {}'.format(character['id']))
                self.dataframe.loc[character['id'], 'is_open'] = False
