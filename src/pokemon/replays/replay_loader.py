import json
import os

REPLAY_PATH = "../../Data/anonymized-randbats-batch"

replay_load_count = 5_000

def load_replays(batch_size=64):
    batch = []
    total = 0

    for path, _, files in os.walk(REPLAY_PATH):
        for name in files:
            file_path = os.path.join(path, name)
            assert file_path.endswith(".log.json")

            with open(file_path) as replay_file:
                batch.append(json.load(replay_file))

            total += 1

            if len(batch) == batch_size or total == replay_load_count:
                yield batch
                batch.clear()
                if total == replay_load_count:
                    break
