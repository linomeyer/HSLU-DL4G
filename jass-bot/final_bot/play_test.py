from jass.agents.agent_random_schieber import AgentRandomSchieber
from jass.arena.arena import Arena

from rule_based_agent import RuleBasedAgent


def main(nr_of_games):
    arena = Arena(nr_games_to_play=nr_of_games, save_filename='playtest_games')
    player = AgentRandomSchieber()
    my_player = RuleBasedAgent()

    arena.set_players(my_player, player, my_player, player)
    print('Playing {} games'.format(arena.nr_games_to_play))

    arena.play_all_games()

    print('Average Points Team 0: {:.2f})'.format(arena.points_team_0.mean()))
    print('Average Points Team 1: {:.2f})'.format(arena.points_team_1.mean()))
    print('------------------------------------------------------------------')
    print('Sum Points Team 0: {:.2f})'.format(arena.points_team_0.sum()))
    print('Sum Points Team 1: {:.2f})'.format(arena.points_team_1.sum()))


main(100)
