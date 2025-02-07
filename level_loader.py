import json

def load_level(level_id):
    with open(f'levels/level_{level_id}.json') as f:
        level_data = json.load(f)
    return level_data