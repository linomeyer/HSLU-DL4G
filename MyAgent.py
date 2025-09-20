import numpy as np
from jass.agents.agent import Agent
from jass.game.const import CLUBS, SPADES, DIAMONDS, HEARTS, OBE_ABE, UNE_UFE, PUSH
from jass.game.game_observation import GameObservation
from jass.game.game_util import convert_one_hot_encoded_cards_to_int_encoded_list
from jass.game.rule_schieber import RuleSchieber

from util import calculate_trump_selection_score


class MyAgent(Agent):
    def __init__(self):
        super().__init__()
        # we need a rule object to determine the valid cards
        self._rule = RuleSchieber()

    def action_trump(self, observation: GameObservation) -> int:
        """
        Determine trump action for the given observation
        Args:
            observation: the game observation, it must be in a state for trump selection

        Returns:
            selected trump as encoded in jass.game.const or jass.game.const.PUSH
        """
        # add your code here using the function above

        hand_int = convert_one_hot_encoded_cards_to_int_encoded_list(observation.hand)
        trump_scores = {
            CLUBS: calculate_trump_selection_score(hand_int, CLUBS),
            SPADES: calculate_trump_selection_score(hand_int, SPADES),
            DIAMONDS: calculate_trump_selection_score(hand_int, DIAMONDS),
            HEARTS: calculate_trump_selection_score(hand_int, HEARTS),
            OBE_ABE: calculate_trump_selection_score(hand_int, OBE_ABE),
            UNE_UFE: calculate_trump_selection_score(hand_int, UNE_UFE)
        }

        max_score_trump_type = max(trump_scores, key=trump_scores.get)
        max_score = trump_scores[max_score_trump_type]

        if observation.forehand == 1 & max_score < 68:
            return PUSH
        else:
            return max_score_trump_type

    def action_play_card(self, observation: GameObservation) -> int:
        """
        Determine the card to play.

        Args:
            observation: the game observation

        Returns:
            the card to play, int encoded as defined in jass.game.const
        """
        valid_cards = self._rule.get_valid_cards_from_obs(observation)
        # we use the global random number generator here
        return np.random.choice(np.flatnonzero(valid_cards))
