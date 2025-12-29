import copy
import logging

from jass.agents.agent import Agent
from jass.game.game_sim import GameSim
from jass.game.game_state import GameState
from jass.game.game_util import *
from jass.game.rule_schieber import RuleSchieber
from keras.src.saving import load_model

from util import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def simulate_possible_hands(obs: GameObservation) -> np.ndarray:
    hands = play_hands(obs)
    return hands


def play_hands(obs: GameObservation):
    played_cards_per_round = obs.tricks
    played_cards = set([card for this_round in played_cards_per_round for card in this_round if card != -1])

    rounds_started_by = obs.trick_first_player
    num_cards_per_player = np.full(4, (9 - obs.nr_tricks))

    first_player = rounds_started_by[obs.nr_tricks]
    for i in range(4):
        player = (first_player + i) % 4
        if obs.current_trick[i] != -1:
            num_cards_per_player[player] -= 1

    all_cards = set(range(36))

    unplayed_cards = list(all_cards - played_cards)
    opponents_unplayed_cards = list(set(unplayed_cards) - set(convert_one_hot_encoded_cards_to_int_encoded_list(obs.hand)))
    np.random.shuffle(opponents_unplayed_cards)

    hands = np.zeros(shape=[4, 36], dtype=np.int32)
    hands[obs.player] = obs.hand

    for player in range(4):
        if player != obs.player:
            players_random_cards = opponents_unplayed_cards[:num_cards_per_player[player]]
            hands[player, players_random_cards] = 1
            opponents_unplayed_cards = opponents_unplayed_cards[num_cards_per_player[player]:]

    return hands


def check_high_card(valid_card_indices, obs: GameObservation):
    for card in valid_card_indices:
        trick = copy.deepcopy(obs.current_trick)
        card_idx = len([card for card in trick if card != -1])
        trick[card_idx] = card
        highest_card, winner_player = highest_card_in_trick(trick, obs)
        if highest_card == card:
            return True, card

    return False, None


def check_stabbing(valid_card_indices, obs: GameObservation):
    """
    checks if "stäche" is worth it
    """
    trump_suit = obs.trump
    points_of_trick = sum(calculate_point_value(card, trump_suit) for card in obs.current_trick if card != -1)
    for card in valid_card_indices:
        card_suit = color_of_card[card]

        # if point value of trick is high enough, determine if "stächen" makes sense
        if points_of_trick >= 11 and card_suit == trump_suit:
            trick = copy.deepcopy(obs.current_trick)
            trick[len([card for card in trick if card != -1])] = card
            highest_card, winner_player = highest_card_in_trick(trick, obs)
            if highest_card == card:
                return True, card

    return False, None


class DLTrumpFixMCTSAgent(Agent):
    def __init__(self, n_simulations=1, n_determinizations=90):
        super().__init__()
        self._rule = RuleSchieber()
        self.n_simulations = n_simulations
        self.n_determinizations = n_determinizations
        self.model = load_model("trump_model.keras")

    def action_trump(self, obs: GameObservation) -> int:
        hand = obs.hand
        if obs.forehand == -1:
            hand = np.append(hand, 1)
        else:
            hand = np.append(hand, 0)
        logger.debug("Hand: " + str(hand))

        hand = hand.reshape(1, -1)

        model = self.model
        probabilities = model.predict(hand)
        logger.debug("Model probabilities: " + str(probabilities))

        trump_categories = [
            "trump_DIAMONDS",
            "trump_HEARTS",
            "trump_SPADES",
            "trump_CLUBS",
            "trump_OBE_ABE",
            "trump_UNE_UFE",
            "trump_PUSH",
        ]

        scores = probabilities[0]

        trump_push_index = trump_categories.index("trump_PUSH")
        ignored_indices = [
            trump_categories.index("trump_OBE_ABE"),
            trump_categories.index("trump_UNE_UFE"),
        ]

        if scores[trump_push_index] > 0.8:
            logger.debug("Decision: Push (Threshold exceeded)")
            return trump_push_index

        filtered_scores = [
            score if idx not in ignored_indices else -1 for idx, score in enumerate(scores)
        ]

        highest_score_index = filtered_scores.index(max(filtered_scores))
        logger.debug(f"Filtered scores: {filtered_scores}")
        logger.debug(f"Highest score index: {highest_score_index}")

        return highest_score_index

    def action_play_card(self, obs: GameObservation) -> int:
        valid_cards = self._rule.get_valid_cards_from_obs(obs)
        valid_card_indices = np.flatnonzero(valid_cards)

        if len(valid_card_indices) == 1:
            return int(valid_card_indices[0])

        should_stab, card = check_stabbing(valid_card_indices, obs)
        if should_stab:
            return card
        should_high_card, card = check_high_card(valid_card_indices, obs)
        if should_high_card:
            return card

        # use monte carlo tree search if no play was made
        card_scores = np.zeros(len(valid_card_indices))
        for _ in range(self.n_determinizations):
            hands = simulate_possible_hands(obs)
            scores = self._score_simulations(hands, obs, valid_card_indices)
            card_scores += scores

        best_card_index = np.argmax(card_scores)
        best_card = valid_card_indices[best_card_index]

        return int(best_card)

    def _score_simulations(self, hands: np.ndarray, obs: GameObservation, valid_card_indices: np.ndarray) -> np.ndarray:
        """
        run {n_simulations} simulations and return the score for each valid card
        """
        score = np.zeros(len(valid_card_indices))

        for _ in range(self.n_simulations):
            # simulate outcome for each valid card
            for i, card in enumerate(valid_card_indices):
                simulation = GameSim(rule=self._rule)
                simulation.init_from_state(GameState.from_json(copy.deepcopy(obs).to_json()))
                simulation._state.hands = copy.deepcopy(hands)
                simulation.action_play_card(card)

                # play out game randomly
                while not simulation.is_done():
                    valid_cards = self._rule.get_valid_cards_from_obs(simulation.get_observation())
                    # check if there are any valid cards
                    if np.flatnonzero(valid_cards).size == 0:
                        break

                    simulation.action_play_card(np.random.choice(np.flatnonzero(valid_cards)))

                points = simulation.state.points[determine_team(obs.player)]
                score[i] += points

        return score
