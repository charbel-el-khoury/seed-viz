import toml
import json

with open('ee-seed-zh-a8326e7c9912.json') as f:
    data = json.load(f)

with open('secrets.toml', 'w') as f:
    toml.dump(data, f)
