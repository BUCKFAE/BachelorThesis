import os
import re
import sys

from matplotlib import pyplot as plt

REPLAY_PATH = '/Users/buckfae/Documents/BachelorThesis/Evaluation/HerrGewitter/HerrGewitterRanked/enhanced_replays'


def main():

    bot_wins = 0
    bot_loss = 0
    bot_name = 'McGewitter'

    elo_history = []

    for path, _, files in os.walk(REPLAY_PATH):
        for file_name in sorted(files):
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

                if name_p1 == bot_name:
                    elo_history += [int(name_p1_line[0].split('|')[-1])]
                if name_p2 == bot_name:
                    elo_history += [int(name_p2_line[0].split('|')[-1])]

                faint_lines = [line.strip() for line in replay if line.startswith('|faint|p')]

                # The bot never forfeits
                if any(['forfeited.' in line.strip() for line in replay]):
                    bot_wins += 1
                    continue

                # Inactivity
                if any(['lost due to inactivity.' in line.strip() for line in replay]):
                    lost_line = [line.strip() for line in replay if 'inactivity.' in line.strip()]
                    assert len(lost_line) == 1
                    if bot_name in lost_line[0]:
                        bot_loss += 1
                    else:
                        bot_wins += 1
                    continue

                try:
                    if 'p1' in faint_lines[-1] and name_p1 != bot_name:
                        bot_wins += 1
                        continue
                    if 'p2' in faint_lines[-1] and name_p2 != bot_name:
                        bot_wins += 1
                        continue
                    else:
                        bot_loss += 1
                except:
                    print(f'Broken Replay: {file_name}')
                    bot_loss += 1

    print(f'Win {bot_wins} / {bot_loss} Loss')

    mean_elo = int(sum(elo_history) / len(elo_history))
    max_elo = max(elo_history)
    print(f'Mean Elo: {mean_elo}')
    print(f'Max Elo: {max_elo}')
    print(f'Current Elo: {elo_history[-1]}')
    print(len(elo_history))

    plt.plot(range(len(elo_history)), elo_history, label='Elo over time')
    plt.plot(range(len(elo_history)), [mean_elo] * len(elo_history), label=f'Mean Elo: {mean_elo}')
    plt.figtext(0.225, 0.925, f'Max Elo: {max_elo}', wrap=True, horizontalalignment='center', fontsize=12)
    plt.legend()
    plt.xlabel('Games')
    plt.ylabel('Elo')
    plt.show()


if __name__ == '__main__':
    main()