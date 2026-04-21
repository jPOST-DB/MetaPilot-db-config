# MAGDB Editor

A tkinter-based GUI application for viewing and editing MAGDB catalogue JSON files used by MetaPilot.

## Requirements

- Python 3.8 or later
- No external packages required (uses only the Python standard library)

## File Structure

```
MetaPilot-db-config/
  magdb_editor.py      # GUI application (entry point)
  magdb_catalogue.py   # Catalogue business logic (add, delete, list)
  magdb_io.py          # JSON file I/O with automatic backup
  README.md
```

### Module Responsibilities

| Module | Description |
|---|---|
| `magdb_editor.py` | tkinter GUI. Builds the window, toolbar, catalogue table, input panel, and status bar. Delegates all data operations to the other two modules. |
| `magdb_catalogue.py` | Pure data logic with no GUI dependency. Provides functions to list, add, and delete catalogues, count `.faa` files, and generate date strings. Can be imported independently by scripts or tests. |
| `magdb_io.py` | JSON read/write with automatic `.bak` backup. Can be imported independently. |

## How to Run

```bash
python magdb_editor.py
```

## JSON Format

The application reads and writes JSON files with the following top-level structure:

```json
{
  "MGnify": [ ... ],
  "localMAGs": [ ... ]
}
```

Each entry in the `MGnify` array represents a catalogue:

```json
{
  "catalogueID": "human-gut",
  "identifier": "MGYG",
  "repository": null,
  "versionlist": [
    {
      "version": "v1.0",
      "speciesCount": 4644,
      "date": "Thu Sep 04 00:00:00 GMT+09:00 2025",
      "localAvailable": true,
      "dbName": "original_db",
      "funcName": "eggNOG",
      "taxaName": "genomes-all_metadata.tsv"
    }
  ],
  "MGYG": [],
  "models": [],
  "pepLibs": []
}
```

The file is saved in compact JSON format (no indentation, no spaces) to match the original file format used by MetaPilot.

## GUI Layout

```
+---------------------------------------------------------------+
| File menu  |  [Open] [Save]  |  [Delete Selected]   filename  |  <- Toolbar
+---------------------------------------------------------------+
|  Catalogue ID | Identifier | Repository | Versions | Species  |  <- Table
|  human-gut    | MGYG       |            | v1.0     | 4644     |     header
|  marine       | MGYG       |            | v1.0     | 2274     |
|  ...          | ...        | ...        | ...      | ...      |
+---------------------------------------------------------------+
| Add New Catalogue                                              |
|  Name: [________]   Version: [v1.0___]                         |  <- Add
|  Folder: [____________________________] [Browse...]            |     panel
|                                         [Add Catalogue]        |
+---------------------------------------------------------------+
| Ready                                                          |  <- Status bar
+---------------------------------------------------------------+
```

## Operations

### 1. Open a JSON File

1. Click the **Open** button on the toolbar, or use the menu **File > Open JSON...**, or press **Ctrl+O**.
2. Select a MAGDB JSON file (e.g., `MAGDB_1_0.json`).
3. The catalogue table will be populated with all entries from the `MGnify` array.
4. The status bar shows the loaded file path.

### 2. Save

1. Click the **Save** button on the toolbar, or use the menu **File > Save**, or press **Ctrl+S**.
2. If the file already exists on disk, a backup copy is created automatically as `<filename>.bak` before overwriting.
3. Use **File > Save As...** to save to a different path.

### 3. Delete Catalogues

1. Select one or more rows in the catalogue table. Hold **Ctrl** or **Shift** to select multiple rows.
2. Click the **Delete Selected** button on the toolbar.
3. A confirmation dialog lists the catalogue IDs to be deleted. Click **Yes** to confirm.
4. The selected entries are removed from the `MGnify` array in memory. Save to persist the changes.

### 4. Add a New Catalogue

1. In the **Add New Catalogue** panel at the bottom of the window, fill in:
   - **Name** — The catalogue name (used as `catalogueID`).
   - **Version** — The version string (e.g., `v1.0`). Defaults to `v1.0`.
   - **Folder** — The path to the catalogue data folder. Use the **Browse...** button to select it.
2. Click **Add Catalogue**.
3. The application automatically:
   - Sets `catalogueID` to the specified **Name**.
   - Sets `identifier` by auto-detecting the leading alphabetic prefix of `.faa` filenames (e.g. `MGYG` for `MGYG000000001.faa`, `GCA` for `GCA000508425.faa`). Falls back to `"MGYG"` if no `.faa` files are found.
   - Sets `repository` to the specified **Folder** path.
   - Scans `.faa` files in `<Folder>/original_db/` and sets `speciesCount` to the file count.
   - Builds the `MGYG` parent/child tree from the `.faa` file names (see **MGYG Tree Generation** below).
   - Sets `date` to the current date/time in the format `"Thu Sep 04 00:00:00 GMT+09:00 2025"`.
   - Sets the following fields to fixed values:
     - `localAvailable`: `true`
     - `dbName`: `"original_db"`
     - `funcName`: `"eggNOG"`
     - `taxaName`: `"genomes-all_metadata.tsv"`
4. The new entry is appended to the `MGnify` array. Save to persist the changes.
5. If the `original_db` subfolder does not exist, a notification is shown and `speciesCount` is set to 0 (with an empty `MGYG` array).
6. Duplicate `catalogueID` values are rejected with a warning.

### MGYG Tree Generation

The `MGYG` array groups genome IDs into parent/children relationships. It is built automatically from the `.faa` file names in `<Folder>/original_db/`:

- **Child ID** = file name without the `.faa` extension (e.g., `MGYG000000001.faa` -> `MGYG000000001`, `MGYG000001066.1.faa` -> `MGYG000001066.1`).
- **Parent ID** = first 11 characters of the child ID (`MGYG` + 7 digits; e.g., `MGYG000001066.1` -> `MGYG0000010`).
- Children sharing the same 11-character prefix are grouped under the same parent.

Example:

```
original_db/
  MGYG000000001.faa   ->  parent: MGYG0000000, child: MGYG000000001
  MGYG000000002.faa   ->  parent: MGYG0000000, child: MGYG000000002
  MGYG000001066.1.faa ->  parent: MGYG0000010, child: MGYG000001066.1
```

Produces:

```json
"MGYG": [
  {
    "parent": "MGYG0000000",
    "children": [
      {"child": "MGYG000000001"},
      {"child": "MGYG000000002"}
    ]
  },
  {
    "parent": "MGYG0000010",
    "children": [
      {"child": "MGYG000001066.1"}
    ]
  }
]
```

Both the parent list and the children within each parent are sorted in ascending order.

## Backup Behavior

Every time a file is saved (Save or Save As), if the target file already exists on disk:

- The existing file is copied to `<filename>.bak` (e.g., `MAGDB_1_0.json` -> `MAGDB_1_0.json.bak`).
- The `.bak` file preserves the file content and timestamps from before the save.
- Only the most recent backup is kept (each save overwrites the previous `.bak`).

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| Ctrl+O | Open JSON file |
| Ctrl+S | Save current file |

## Reusing Modules in Scripts

The logic modules can be used independently from the GUI:

```python
from magdb_io import load_json, save_json
from magdb_catalogue import add_catalogue, delete_catalogues, list_catalogues

# Load
data = load_json("MAGDB_1_0.json")

# List all catalogue IDs
for cat in list_catalogues(data):
    print(cat["catalogueID"])

# Add a new catalogue
species_count, dir_found, identifier = add_catalogue(data, "my-catalogue", "/path/to/folder", "v1.0")

# Delete catalogues
delete_catalogues(data, ["old-catalogue"])

# Save (automatically creates .bak backup)
save_json("MAGDB_1_0.json", data)
```
