import copy

from jass.agents.agent import Agent
from jass.game.game_sim import GameSim
from jass.game.game_state import GameState
from jass.game.game_util import *
from jass.game.rule_schieber import RuleSchieber

from ..util import *


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
    checks if stabbing "stäche" is worth it
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


class RuleBasedAgent(Agent):
    def __init__(self, n_simulations=1, n_determinizations=90):
        super().__init__()
        self._rule = RuleSchieber()
        self.n_simulations = n_simulations
        self.n_determinizations = n_determinizations

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

        if observation.forehand == -1 and max_score < 68:
            return PUSH
        else:
            return max_score

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
                # simulate playing the card
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
