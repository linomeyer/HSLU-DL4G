from jass.game.const import DIAMONDS, HEARTS, SPADES, CLUBS, UNE_UFE, OBE_ABE

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
