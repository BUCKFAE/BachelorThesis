import os
import sys
import matplotlib.pyplot as plt

REPLAY_PATH = '/home/buckfae/Documents/BachelorThesis/Evaluation/HerrGewitter/Ranked/enhanced_replays'

def main():

    elo_history = []

    for path, _, files in os.walk(REPLAY_PATH):
        for file_name in sorted(files):
            with open(os.path.join(path, file_name), 'r') as f:
                replay = f.readlines()

                print(f'Replay: {file_name}')

                # Replays that don't contain the closing script tag are broken
                if not any(['</script>' in line for line in replay]):
                    print(f'Replay {file_name.split("-")[0]} is broken!')

                line_p1 = [line for line in replay if line.startswith('|player|p1|') and len(line.split('|')) == 6]
                assert len(line_p1) == 1
                line_p1 = line_p1[0].strip()
                line_p2 = [line for line in replay if line.startswith('|player|p2|') and len(line.split('|')) == 6]
                assert len(line_p2) == 1
                line_p2 = line_p2[0].strip()

                print(f'Line p1: {line_p1}')
                print(f'Line p2: {line_p2}')

                if line_p1.split('|')[3] == 'HerrGewitter':
                    elo_history += [int(line_p1.split('|')[-1])]
                elif line_p2.split('|')[3] == 'HerrGewitter':
                    elo_history += [int(line_p2.split('|')[-1])]
                else:
                    raise ValueError(f'Neither of the two players was HerrGewitter')

    print(elo_history)

    mean_elo = int(sum(elo_history) / len(elo_history))
    print(f'Mean Elo: {mean_elo}')

    plt.plot(range(len(elo_history)), elo_history, label='Elo over time')
    plt.plot(range(len(elo_history)), [mean_elo] * len(elo_history), label='Mean Elo')
    plt.legend()
    plt.xlabel('Games')
    plt.ylabel('Elo')
    plt.show()

if __name__ == '__main__':
    main()