"""MAGDB catalogue operations (add, delete, list)."""

import glob
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta

PARENT_ID_LENGTH = 11  # "MGYG" + 7 digits
DEFAULT_IDENTIFIER = "MGYG"  # Fallback identifier when no .faa files are found


def list_catalogues(data):
    """Return the list of MGnify catalogue entries."""
    return data.get("MGnify", [])


def get_catalogue_ids(data):
    """Return a list of all catalogueID values."""
    return [c["catalogueID"] for c in list_catalogues(data)]


def delete_catalogues(data, ids_to_delete):
    """Remove catalogues whose catalogueID is in ids_to_delete. Returns count deleted."""
    ids_set = set(ids_to_delete)
    original = list_catalogues(data)
    filtered = [c for c in original if c["catalogueID"] not in ids_set]
    deleted_count = len(original) - len(filtered)
    data["MGnify"] = filtered
    return deleted_count


def list_faa_files(folder):
    """Return sorted list of .faa file paths in folder/original_db/.

    Returns (faa_paths, found_dir).
    """
    original_db_path = os.path.join(folder, "original_db")
    if os.path.isdir(original_db_path):
        faa_files = sorted(glob.glob(os.path.join(original_db_path, "*.faa")))
        return faa_files, True
    return [], False


def count_faa_files(folder):
    """Count .faa files inside folder/original_db/. Returns (count, found_dir)."""
    faa_files, found = list_faa_files(folder)
    return len(faa_files), found


def detect_identifier(faa_paths):
    """Detect the identifier (leading alphabetic prefix) from .faa file names.

    Extracts the leading alphabetic characters of each filename (e.g. "MGYG"
    from "MGYG000000001", "GCA" from "GCA000508425") and returns the most
    common prefix.

    Returns DEFAULT_IDENTIFIER if faa_paths is empty.
    """
    if not faa_paths:
        return DEFAULT_IDENTIFIER

    prefixes = []
    for path in faa_paths:
        name = os.path.splitext(os.path.basename(path))[0]
        match = re.match(r"^[A-Za-z]+", name)
        if match:
            prefixes.append(match.group(0))

    if not prefixes:
        return DEFAULT_IDENTIFIER

    most_common, _ = Counter(prefixes).most_common(1)[0]
    return most_common


def build_mgyg_tree(faa_paths):
    """Build the MGYG parent/children structure from a list of .faa file paths.

    Each child ID = filename without the .faa extension (e.g. "MGYG000001066.1").
    Parent ID = first 11 characters of the child ID (e.g. "MGYG0000010").
    Children are grouped by parent prefix.

    Returns a list of dicts:
        [{"parent": "MGYG0000010",
          "children": [{"child": "MGYG000001066"}, ...]}, ...]
    """
    groups = defaultdict(list)
    for path in faa_paths:
        child_id = os.path.splitext(os.path.basename(path))[0]
        if len(child_id) < PARENT_ID_LENGTH:
            # Skip entries that don't match the expected pattern
            continue
        parent_id = child_id[:PARENT_ID_LENGTH]
        groups[parent_id].append(child_id)

    result = []
    for parent_id in sorted(groups.keys()):
        children = sorted(groups[parent_id])
        result.append(
            {
                "parent": parent_id,
                "children": [{"child": c} for c in children],
            }
        )
    return result


def make_date_string():
    """Return current date/time as e.g. 'Thu Sep 04 00:00:00 GMT+09:00 2025'."""
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)
    return now.strftime("%a %b %d %H:%M:%S") + " GMT+09:00 " + now.strftime("%Y")


def create_catalogue_entry(name, folder, version, species_count, mgyg_tree, identifier):
    """Build a new catalogue dict ready to append to MGnify list."""
    return {
        "catalogueID": name,
        "identifier": identifier,
        "repository": folder,
        "versionlist": [
            {
                "version": version,
                "speciesCount": species_count,
                "date": make_date_string(),
                "localAvailable": True,
                "dbName": "original_db",
                "funcName": "eggNOG",
                "taxaName": "genomes-all_metadata.tsv",
            }
        ],
        "MGYG": mgyg_tree,
        "models": [],
        "pepLibs": [],
    }


def add_catalogue(data, name, folder, version):
    """Add a new catalogue to data. Returns (species_count, dir_found, identifier).

    Scans <folder>/original_db/*.faa to determine speciesCount, detect the
    identifier (leading alphabetic prefix of filenames), and build the
    MGYG parent/children structure.

    Raises ValueError if the catalogueID already exists.
    """
    if name in get_catalogue_ids(data):
        raise ValueError(f"Catalogue '{name}' already exists.")

    faa_paths, dir_found = list_faa_files(folder)
    species_count = len(faa_paths)
    identifier = detect_identifier(faa_paths)
    mgyg_tree = build_mgyg_tree(faa_paths)
    entry = create_catalogue_entry(name, folder, version, species_count, mgyg_tree, identifier)
    data["MGnify"].append(entry)
    return species_count, dir_found, identifier
