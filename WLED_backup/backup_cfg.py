import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1]))
from wrappers.WLED_wrapper import WLED

# I don't think there's any way to backup the presets other than
# going to http://192.168.1.101/edit and copying /presets.json

led = WLED()
with open(Path(__file__).parent / "cfg.json", "w") as f:
    json.dump(led.config, f, separators=(',', ':'))
