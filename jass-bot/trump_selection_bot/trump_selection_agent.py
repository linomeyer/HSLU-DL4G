import numpy as np
from jass.agents.agent import Agent
from jass.game.const import CLUBS, SPADES, DIAMONDS, HEARTS, OBE_ABE, UNE_UFE, PUSH
from jass.game.game_observation import GameObservation
from jass.game.game_util import convert_one_hot_encoded_cards_to_int_encoded_list
from jass.game.rule_schieber import RuleSchieber

from ..util import calculate_trump_selection_score


class TrumpSelectionAgent(Agent):
    def __init__(self):
        super().__init__()
        # we need a rule object to determine the valid cards
        self._rule = RuleSchieber()

    def action_trump(self, observation: GameObservation) -> int:

        hand_int = convert_one_hot_encoded_cards_to_int_encoded_list(observation.hand)
        trump_scores = {
            CLUBS: calculate_trump_selection_score(hand_int, CLUBS),
            SPADES: calculate_trump_selection_score(hand_int, SPADES),
            DIAMONDS: calculate_trump_selection_score(hand_int, DIAMONDS),
            HEARTS: calculate_trump_selection_score(hand_int, HEARTS),
            OBE_ABE: calculate_trump_selection_score(hand_int, OBE_ABE),
            UNE_UFE: calculate_trump_selection_score(hand_int, UNE_UFE)
        }

        max_score = max(trump_scores, key=trump_scores.get)

        if observation.forehand == -1 & max_score < 68:
            return PUSH
        else:
            return max_score

    def action_play_card(self, observation: GameObservation) -> int:
        valid_cards = self._rule.get_valid_cards_from_obs(observation)
        # we use the global random number generator here
        return np.random.choice(np.flatnonzero(valid_cards))
