import os
import re
import sys


def main():

    joni_wins = 0
    donner_wins = 0

    for path, _, files in os.walk('/home/buckfae/Documents/BachelorThesis/Evaluation/HerrDonner/Joni/data/enhanced_replays'):
        for file_name in files:
            with open(os.path.join(path, file_name), 'r') as f:
                replay = f.readlines()

                name_p1_line = [line.strip() for line in replay if line.startswith('|player|p1|')]
                assert len(name_p1_line) == 1
                name_p2_line = [line.strip() for line in replay if line.startswith('|player|p2|')]
                assert len(name_p2_line) == 1

                name_p1 = re.sub('\\|player\\|p1\\|', '', name_p1_line[0]).split('|')[-3]
                name_p2 = re.sub('\\|player\\|p2\\|', '', name_p2_line[0]).split('|')[-3]

                assert name_p1 == 'jok3r_de'
                assert name_p2 == 'HerrDonner1'

                print(f'{name_p1=}')
                print(f'{name_p2=}')

                faint_lines = [line.strip() for line in replay if line.startswith('|faint|p')]

                if len(faint_lines) == 0:
                    print(file_name)

                if 'p1' in faint_lines[-1] and name_p1 == 'HerrDoner1':
                    joni_wins += 1
                elif 'p2' in faint_lines[-1] and name_p2 == 'HerrDonner1':
                    joni_wins += 1
                else:
                    donner_wins += 1

            print(f'Joni {joni_wins} / {donner_wins} HerrDonner')


if __name__ == '__main__':
    main()