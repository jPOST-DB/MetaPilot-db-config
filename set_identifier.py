"""Set the identifier of a specific catalogue."""

import sys
from magdb_io import load_json, save_json


def main():
    if len(sys.argv) != 4:
        print("Usage: python set_identifier.py <json_path> <catalogueID> <newIdentifier>")
        sys.exit(1)

    json_path = sys.argv[1]
    catalogue_id = sys.argv[2]
    new_identifier = sys.argv[3]

    data = load_json(json_path)

    found = False
    for entry in data.get("MGnify", []):
        if entry.get("catalogueID") == catalogue_id:
            old = entry.get("identifier")
            entry["identifier"] = new_identifier
            found = True
            print(f"Changed identifier for '{catalogue_id}': '{old}' -> '{new_identifier}'")
            break

    if not found:
        print(f"ERROR: catalogueID '{catalogue_id}' not found in MGnify.")
        sys.exit(1)

    save_json(json_path, data)
    print(f"Saved to {json_path} (backup: {json_path}.bak)")


if __name__ == "__main__":
    main()
