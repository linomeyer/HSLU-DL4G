from jass.game.const import DIAMONDS, HEARTS, SPADES, CLUBS, UNE_UFE, OBE_ABE, offset_of_card, color_of_card, lower_trump
from jass.game.game_observation import GameObservation

# Score for each card of a color from Ace to 6
# score if the color is trump
trump_score = [15, 10, 7, 25, 6, 19, 5, 5, 5]
# score if the color is not trump
no_trump_score = [9, 7, 5, 2, 1, 0, 0, 0, 0]
# score if obenabe is selected (all colors)
obenabe_score = [14, 10, 8, 7, 5, 0, 5, 0, 0, ]
# score if uneufe is selected (all colors)
uneufe_score = [0, 2, 1, 1, 5, 5, 7, 9, 11]


def calculate_trump_selection_score(cards, trump: int) -> int:
    score = 0
    for card in cards:
        color = ""
        if card < 9:
            color = DIAMONDS
        elif card >= 9 & card < 18:
            color = HEARTS
        elif card >= 18 & card < 27:
            color = SPADES
        elif card >= 27 & card < 36:
            color = CLUBS

        if color == trump:
            score += trump_score[card % 9]
        elif trump == UNE_UFE:
            score += uneufe_score[card % 9]
        elif trump == OBE_ABE:
            score += obenabe_score[card % 9]
        else:
            score += no_trump_score[card % 9]

    return score


def determine_team(player: int) -> int:
    return player % 2


def calculate_point_value(card, trump_suit):
    card_offset = offset_of_card[card]
    if color_of_card[card] == trump_suit:
        return trump_score[card_offset]
    else:
        return no_trump_score[card_offset]


def highest_card_in_trick(trick, obs: GameObservation):
    number_of_played_cards = len([card for card in trick if card != -1])
    trump = obs.trump
    card_color = color_of_card[trick[0]]
    # if trump has been played as first card
    if card_color == trump:
        winner = 0
        highest_card = trick[0]
        for i in range(1, number_of_played_cards):
            if color_of_card[trick[i]] == trump and lower_trump[trick[i], highest_card]:
                highest_card = trick[i]
                winner = i

        return highest_card, winner

    # a card that is not trump has been played as first card
    else:
        winner = 0
        highest_card = trick[0]
        trump_played = False
        trump_card = None
        for i in range(1, number_of_played_cards):
            if color_of_card[trick[i]] == trump:
                if trump_played:
                    # more than one trump card has been played
                    if lower_trump[trick[i], trump_card]:
                        winner = i
                        trump_card = trick[i]
                else:
                    trump_played = True
                    trump_card = trick[i]
                    winner = i
            elif trump_played:
                # ignore non trump cards if trump has been played
                pass
            elif color_of_card[trick[i]] == card_color:
                # trump has not been played but "g'farbet"
                if trick[i] < highest_card:
                    highest_card = trick[i]
                    winner = i

        return highest_card, winner
