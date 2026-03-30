"""MAGDB catalogue operations (add, delete, list)."""

import glob
import os
from datetime import datetime, timezone, timedelta


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


def count_faa_files(folder):
    """Count .faa files inside folder/original_db/. Returns (count, found_dir)."""
    original_db_path = os.path.join(folder, "original_db")
    if os.path.isdir(original_db_path):
        faa_files = glob.glob(os.path.join(original_db_path, "*.faa"))
        return len(faa_files), True
    return 0, False


def make_date_string():
    """Return current date/time as e.g. 'Thu Sep 04 00:00:00 GMT+09:00 2025'."""
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)
    return now.strftime("%a %b %d %H:%M:%S") + " GMT+09:00 " + now.strftime("%Y")


def create_catalogue_entry(name, folder, version, species_count):
    """Build a new catalogue dict ready to append to MGnify list."""
    return {
        "catalogueID": name,
        "identifier": "MGYG",
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
        "MGYG": [],
        "models": [],
        "pepLibs": [],
    }


def add_catalogue(data, name, folder, version):
    """Add a new catalogue to data. Returns (species_count, dir_found).

    Raises ValueError if the catalogueID already exists.
    """
    if name in get_catalogue_ids(data):
        raise ValueError(f"Catalogue '{name}' already exists.")

    species_count, dir_found = count_faa_files(folder)
    entry = create_catalogue_entry(name, folder, version, species_count)
    data["MGnify"].append(entry)
    return species_count, dir_found
