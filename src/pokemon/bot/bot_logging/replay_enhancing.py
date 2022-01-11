"""Provides the ability to add log data from a file to a battle replay"""
import logging
import os
import re
import shutil


def enhance_replays():
    # Stores the content of all log files
    log_files = []

    enhanced = []

    print(f'Enhancing replays!')

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

            if battle_id not in enhanced:
                enhanced.append(battle_id)
            else:
                continue
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

            # Getting the names of the players
            name_lines = [line for line in replay_file_content if line.startswith('|j|☆')]

            # Player names
            [name1, name2] = [line.replace('|j|☆', '').strip() for line in name_lines[:2]]

            # Team bot
            bot_team_index = 3
            assert battle_lines[bot_team_index].startswith('\t'), 'Team info did not start with a tab'
            bot_team = battle_lines[bot_team_index].strip().split()
            assert len(bot_team) == 6, 'Team info did not contain 6 Pokémon'
            bot_team_string = '-'.join(bot_team)

            # Index of the replay
            existing_replays = os.listdir('src/data/enhanced_replays')
            next_file_index = 0
            if len(existing_replays) > 0:
                existing_replays.sort(key=lambda x: x.split("-")[0], reverse=True)
                next_file_index = int(existing_replays[0].split("-")[0]) + 1

            # Final file name
            new_file_name = re.sub('\\s+', '', f'{next_file_index:08d}-{name1}-{name2}-{bot_team_string}.html')

            # Creating enhanced HTML File
            with open(f'src/data/enhanced_replays/{new_file_name}', 'w') as f:

                current_battle_log_line = 2

                for original_line in replay_file_content:

                    # Changing text below replay
                    if 'Replay created by' in original_line:
                        break

                    if 'poke-env battle replay' in original_line \
                            or 'pokemonshowdown.com' in original_line \
                            or 'target=\"_blank\"' in original_line:
                        if 'let daily' not in original_line:
                            continue

                    f.write(original_line)

                    # Start of a new turn: We add logs of this turn
                    if original_line.startswith("|turn|"):

                        if len(battle_lines) == current_battle_log_line:
                            break

                        while not battle_lines[current_battle_log_line].startswith("Turn"):

                            if len(battle_lines) - 1 == current_battle_log_line:
                                break

                            message = battle_lines[current_battle_log_line]
                            message = re.sub('\\t', '>', message)
                            f.write(f'|chat|DEBUG|{message}\n')
                            current_battle_log_line += 1
                        current_battle_log_line += 1

                # Adding battle information below
                f.write(f'<h1 style="font-weight:normal;text-align:center">'
                        f'<strong>{name1}<br>vs<br>{name2}</strong></h1>\n')
                bot_team_string_info = bot_team_string.replace("-", " ")
                f.write('<br><br>\n')
                f.write(f'<h1 style="font-weight: normal; text-align: center">{bot_team_string_info}</h1>\n')

    # Moving files to archive
    for log in os.listdir('src/data/logs'):
        shutil.copy(f'src/data/logs/{log}', f'src/data/archive/logs/{log}')

    for replay in os.listdir('src/data/replays'):
        shutil.move(f'src/data/replays/{replay}', f'src/data/archive/replays/{replay}')


if __name__ == "__main__":
    enhance_replays()
