"""Set the MGYG array of a specific catalogue to []."""

import sys
from magdb_io import load_json, save_json


def main():
    if len(sys.argv) != 3:
        print("Usage: python clear_mgyg.py <json_path> <catalogueID>")
        sys.exit(1)

    json_path = sys.argv[1]
    catalogue_id = sys.argv[2]

    data = load_json(json_path)

    found = False
    for entry in data.get("MGnify", []):
        if entry.get("catalogueID") == catalogue_id:
            before = len(entry.get("MGYG", []))
            entry["MGYG"] = []
            found = True
            print(f"Cleared MGYG for '{catalogue_id}' (was {before} parent groups -> now 0)")
            break

    if not found:
        print(f"ERROR: catalogueID '{catalogue_id}' not found in MGnify.")
        sys.exit(1)

    save_json(json_path, data)
    print(f"Saved to {json_path} (backup: {json_path}.bak)")


if __name__ == "__main__":
    main()
