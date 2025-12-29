from jass.agents.agent_random_schieber import AgentRandomSchieber
from jass.arena.arena import Arena

from dl_trump_time_mcts_agent import DLTrumpTimeMCTSAgent
from fix_mcts_agent import FixMCTSAgent
from jass_bot.final.dl_trump_fix_mcts_agent import DLTrumpFixMCTSAgent
from time_mcts_agent import TimeMCTSAgent


def main(nr_of_games):
    arena = Arena(nr_games_to_play=nr_of_games, save_filename='playtest_games')
    player = AgentRandomSchieber()
    dl_trump_time_mcts_agent = DLTrumpTimeMCTSAgent()
    dl_trump_fix_mcts_agent = DLTrumpFixMCTSAgent()
    fix_mcts_agent = FixMCTSAgent()
    time_mcts_agent = TimeMCTSAgent()

    arena.set_players(dl_trump_time_mcts_agent, player, dl_trump_time_mcts_agent, player)
    print("First Game")
    print('Playing {} games'.format(arena.nr_games_to_play))

    # arena.play_all_games()

    print('Average Points Team 0: {:.2f})'.format(arena.points_team_0.mean()))
    print('Average Points Team 1: {:.2f})'.format(arena.points_team_1.mean()))
    print('------------------------------------------------------------------')
    print('Sum Points Team 0: {:.2f})'.format(arena.points_team_0.sum()))
    print('Sum Points Team 1: {:.2f})'.format(arena.points_team_1.sum()))

    arena = Arena(nr_games_to_play=nr_of_games, save_filename='playtest_games')
    arena.set_players(dl_trump_fix_mcts_agent, player, dl_trump_fix_mcts_agent, player)
    print("Second Game")

    arena.play_all_games()

    print('Average Points Team 0: {:.2f})'.format(arena.points_team_0.mean()))
    print('Average Points Team 1: {:.2f})'.format(arena.points_team_1.mean()))
    print('------------------------------------------------------------------')
    print('Sum Points Team 0: {:.2f})'.format(arena.points_team_0.sum()))
    print('Sum Points Team 1: {:.2f})'.format(arena.points_team_1.sum()))

    arena = Arena(nr_games_to_play=nr_of_games, save_filename='playtest_games')
    arena.set_players(fix_mcts_agent, player, fix_mcts_agent, player)
    print("Third Game")

    arena.play_all_games()

    print('Average Points Team 0: {:.2f})'.format(arena.points_team_0.mean()))
    print('Average Points Team 1: {:.2f})'.format(arena.points_team_1.mean()))
    print('------------------------------------------------------------------')
    print('Sum Points Team 0: {:.2f})'.format(arena.points_team_0.sum()))
    print('Sum Points Team 1: {:.2f})'.format(arena.points_team_1.sum()))

    arena = Arena(nr_games_to_play=nr_of_games, save_filename='playtest_games')
    arena.set_players(time_mcts_agent, player, time_mcts_agent, player)
    print("Fourth Game")

    arena.play_all_games()

    print('Average Points Team 0: {:.2f})'.format(arena.points_team_0.mean()))
    print('Average Points Team 1: {:.2f})'.format(arena.points_team_1.mean()))
    print('------------------------------------------------------------------')
    print('Sum Points Team 0: {:.2f})'.format(arena.points_team_0.sum()))
    print('Sum Points Team 1: {:.2f})'.format(arena.points_team_1.sum()))


main(10)
