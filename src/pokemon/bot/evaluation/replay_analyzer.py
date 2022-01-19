import os
import re
import sys

import numpy as np
from matplotlib import pyplot as plt

from src.pokemon import logger

REPLAY_LOCATIONS = [
    ('/home/buckfae/Documents/BachelorThesis/Evaluation/HerrGewitter/HerrGewitterRanked/enhanced_replays', 'McGewitter'),
    ('/home/buckfae/Documents/BachelorThesis/Evaluation/HerrDonner/HerrDonnerRanked/enhanced_replays', 'McDonner')
]

def main():

    bot_wins = 0
    bot_loss = 0

    elo_histories = {}
    bot_w_l = {}

    for replay_path, bot_name in REPLAY_LOCATIONS:

        logger.info(f'Evaluating replays for: {bot_name}')

        elo_histories[bot_name] = []
        bot_w_l[bot_name] = (0, 0)

        # Evaluating all replays for the bot
        for path, _, files in os.walk(replay_path):
            for file_name in sorted(files):

                # Analyzing the current replay
                with open(os.path.join(path, file_name), 'r') as f:
                    replay = f.readlines()

                    name_p1_line = [line.strip() for line in replay if line.startswith('|player|p1|')]
                    name_p2_line = [line.strip() for line in replay if line.startswith('|player|p2|')]

                    name_p1 = re.sub('\\|player\\|p1\\|', '', name_p1_line[0]).split('|')[-3]
                    name_p2 = re.sub('\\|player\\|p2\\|', '', name_p2_line[0]).split('|')[-3]

                    assert name_p1 != name_p2

                    assert name_p1 == bot_name or name_p2 == bot_name
                    #assert name_p1 == 'jok3r_de'
                    #assert name_p2 == 'HerrDonner1'

                    # Adding current ELO
                    if name_p1 == bot_name:
                        elo_histories[bot_name] += [int(name_p1_line[0].split('|')[-1])]
                    if name_p2 == bot_name:
                        elo_histories[bot_name] += [int(name_p2_line[0].split('|')[-1])]

                    faint_lines = [line.strip() for line in replay if line.startswith('|faint|p')]

                    # The bot never forfeits
                    if any(['forfeited.' in line.strip() for line in replay]):
                        bot_w_l[bot_name] = (bot_w_l[bot_name][0] + 1, bot_w_l[bot_name][1])
                        continue

                    # Inactivity
                    if any(['lost due to inactivity.' in line.strip() for line in replay]):
                        lost_line = [line.strip() for line in replay if 'inactivity.' in line.strip()]
                        assert len(lost_line) == 1
                        if bot_name in lost_line[0]:
                            bot_w_l[bot_name] = (bot_w_l[bot_name][0], bot_w_l[bot_name][1] + 1)
                        else:
                            bot_w_l[bot_name] = (bot_w_l[bot_name][0] + 1, bot_w_l[bot_name][1])
                        continue

                    try:
                        if 'p1' in faint_lines[-1] and name_p1 != bot_name:
                            continue
                        if 'p2' in faint_lines[-1] and name_p2 != bot_name:
                            bot_w_l[bot_name] = (bot_w_l[bot_name][0] + 1, bot_w_l[bot_name][1])
                            continue
                        else:
                            bot_w_l[bot_name] = (bot_w_l[bot_name][0], bot_w_l[bot_name][1] + 1)
                    except:
                        logger.critical(f'Broken Replay: {file_name}')
                        bot_w_l[bot_name] = (bot_w_l[bot_name][0], bot_w_l[bot_name][1] + 1)

    # Plotting elo for all bots
    for bot in elo_histories.keys():
        bot_wins, bot_loss = bot_w_l[bot]
        elo_history = elo_histories[bot]

        logger.info(f'Win {bot_wins} / {bot_loss} Loss')

        mean_elo = int(sum(elo_history) / len(elo_history))
        max_elo = max(elo_history)

        logger.info(f'Mean Elo: {mean_elo}')
        logger.info(f'Max Elo: {max_elo}')

        plt.plot(range(len(elo_history)), elo_history, label=f'Elo over time')
        plt.plot(range(len(elo_history)), [mean_elo] * len(elo_history), label=f'Mean Elo: {mean_elo}')
        plt.plot(range(len(elo_history)), [max_elo] * len(elo_history), label=f'Max Elo: {max_elo}')

        plt.legend(loc='upper left')
        plt.xlabel('Games')
        plt.ylabel('Elo')
        plt.yticks(np.arange(1000, 1650, 100))
        plt.title(f'{bot}')
        plt.show()
        
    for bot in elo_histories.keys():
        elo_history = elo_histories[bot]

        smoothed_elo = []
        step = 20
        for i in range(0, len(elo_history), step):
            part = elo_history[i: i + step]
            smoothed_elo += [(i, sum(part) / len(part))]

        plt.plot(*zip(*smoothed_elo), label=f'{bot}')

        plt.title('Elo smoothed')
        plt.legend(loc='upper left')
        plt.xlabel('Games')
        plt.yticks(np.arange(1000, 1600, 100))
        plt.ylabel('Elo')

    plt.show()


if __name__ == '__main__':
    main()