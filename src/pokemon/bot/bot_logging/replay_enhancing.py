"""Provides the ability to add log data from a file to a battle replay"""
import os
import re
import shutil
import subprocess


def enhance_replays(delete_old_replays=False):

    # Stores the content of all log files
    log_files = []

    for path, _, files in os.walk('src/data/logs'):
        for file_name in files:
            with open(f'{path}/{file_name}', 'r') as f:
                log_files.append(''.join(f.readlines()))

    for log_file in log_files:
        battles = log_file.strip().split('Battle: battle-gen8randombattle-')
        battles = [b for b in battles if b.strip()]

        for battle in battles:
            battle_lines = battle.split('\n')
            battle_id = battle_lines[0]

            print(f'Enhancing battle \"{battle_id}\"')

            replay_file_content = None

            # Searching matching HTML File
            for replay_file in os.listdir('src/data/replays'):
                if battle_id in replay_file:
                    with open(f'src/data/replays/{replay_file}') as f:
                        replay_file_content = f.readlines()

            # Skipping if we can't find the file
            if replay_file_content is None:
                print(f'Unable to find replay for battle {battle_id}')
                continue

            # TODO: Name replay file with opponent, counter (if multiple times) and team

            # Creating enhanced HTML File
            with open(f'src/data/enhanced_replays/{battle_id}.html', 'w') as f:

                current_battle_log_line = 2

                for original_line in replay_file_content:
                    f.write(original_line)

                    # Start of a new turn: We add logs of this turn
                    if original_line.startswith("|turn|"):
                        # TODO: This breaks for multiple replays
                        while not battle_lines[current_battle_log_line].startswith("Turn"):

                            if len(battle_lines) - 1 == current_battle_log_line:
                                break

                            message = battle_lines[current_battle_log_line]
                            message = re.sub('\\t', '>', message)
                            f.write(f'|chat|DEBUG|{message}\n')
                            current_battle_log_line += 1
                        current_battle_log_line += 1

    if delete_old_replays:
        shutil.rmtree('src/data/logs')
        shutil.rmtree('src/data/replays')
        os.mkdir('src/data/logs')
        os.mkdir('src/data/replays')




if __name__ == "__main__":
    enhance_replays()
