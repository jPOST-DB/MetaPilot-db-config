"""MAGDB JSON file I/O with backup support."""

import json
import os
import shutil


def load_json(path):
    """Load and return data from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    """Save data to a JSON file, creating a .bak backup of the existing file first."""
    if os.path.exists(path):
        bak_path = path + ".bak"
        shutil.copy2(path, bak_path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
