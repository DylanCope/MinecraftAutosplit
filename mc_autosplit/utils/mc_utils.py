import sys
import os
import json
from pathlib import Path

from nbt import nbt

from mc_autosplit.utils.exception import FailedToReadAdvancements


def get_default_minecraft_dir():
    if sys.platform == "win32":
        return os.path.join(os.environ["APPDATA"], ".minecraft")
    elif sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/minecraft/")
    else:
        return os.path.expanduser("~/.minecraft/")


def get_last_played_level():
    mc_dir = Path(get_default_minecraft_dir())
    mc_saves = mc_dir / 'saves'

    world_paths = [
        mc_saves / s for s in os.listdir(mc_saves)
        if (mc_saves / s).is_dir()
    ]

    worlds_recently_modified = sorted(world_paths, key=os.path.getmtime, reverse=True)
    for path in worlds_recently_modified.copy()[:5]:
        level = nbt.NBTFile(path / "level.dat")
        if not int(str(level["Data"]["Time"])):
            continue
        else:
            return level, path

    raise FileNotFoundError('Unable to load any worlds.')


def get_stats(level_path):
    stats_dir = level_path / 'stats'
    stats_path = stats_dir / os.listdir(stats_dir)[0]

    with open(stats_path, "r") as f:
        stats = json.load(f)

    return stats


def get_advancements(level_path):
    advancements_dir = level_path / 'advancements'
    advancements_path = advancements_dir / os.listdir(advancements_dir)[0]

    try:
        with open(advancements_path, "r") as f:
            advancements = json.load(f)
    except json.decoder.JSONDecodeError:
        raise FailedToReadAdvancements()

    return advancements
