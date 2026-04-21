"""MAGDB Editor — tkinter GUI for editing MAGDB JSON catalogues."""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from magdb_io import load_json, save_json
from magdb_catalogue import (
    list_catalogues,
    get_catalogue_ids,
    delete_catalogues,
    add_catalogue,
)


class MAGDBEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("MAGDB Editor")
        self.root.geometry("900x600")
        self.root.minsize(700, 400)

        self.data = None
        self.filepath = None

        self._build_menu()
        self._build_toolbar()
        self._build_table()
        self._build_add_panel()
        self._build_statusbar()

    # ── Menu ──────────────────────────────────────────────
    def _build_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open JSON...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())

    # ── Toolbar ───────────────────────────────────────────
    def _build_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=3)

        ttk.Button(toolbar, text="Open", command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Save", command=self.save_file).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)
        ttk.Button(toolbar, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=2)

        self.file_label = ttk.Label(toolbar, text="No file loaded", foreground="gray")
        self.file_label.pack(side=tk.RIGHT, padx=5)

    # ── Catalogue Table ───────────────────────────────────
    def _build_table(self):
        table_frame = ttk.LabelFrame(self.root, text="Catalogues")
        table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=3)

        columns = ("catalogueID", "identifier", "repository", "versions", "speciesCount")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="extended")

        self.tree.heading("catalogueID", text="Catalogue ID")
        self.tree.heading("identifier", text="Identifier")
        self.tree.heading("repository", text="Repository")
        self.tree.heading("versions", text="Versions")
        self.tree.heading("speciesCount", text="Species Count")

        self.tree.column("catalogueID", width=180, minwidth=100)
        self.tree.column("identifier", width=80, minwidth=60)
        self.tree.column("repository", width=300, minwidth=100)
        self.tree.column("versions", width=120, minwidth=60)
        self.tree.column("speciesCount", width=100, minwidth=60)

        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

    # ── Add Catalogue Panel ───────────────────────────────
    def _build_add_panel(self):
        add_frame = ttk.LabelFrame(self.root, text="Add New Catalogue")
        add_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=3)

        row0 = ttk.Frame(add_frame)
        row0.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(row0, text="Name:").pack(side=tk.LEFT)
        self.entry_name = ttk.Entry(row0, width=25)
        self.entry_name.pack(side=tk.LEFT, padx=5)

        ttk.Label(row0, text="Version:").pack(side=tk.LEFT)
        self.entry_version = ttk.Entry(row0, width=15)
        self.entry_version.pack(side=tk.LEFT, padx=5)
        self.entry_version.insert(0, "v1.0")

        row1 = ttk.Frame(add_frame)
        row1.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(row1, text="Folder:").pack(side=tk.LEFT)
        self.entry_folder = ttk.Entry(row1, width=60)
        self.entry_folder.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(row1, text="Browse...", command=self._browse_folder).pack(side=tk.LEFT, padx=2)

        row2 = ttk.Frame(add_frame)
        row2.pack(fill=tk.X, padx=5, pady=(2, 5))
        ttk.Button(row2, text="Add Catalogue", command=self._on_add_catalogue).pack(side=tk.RIGHT, padx=2)

    # ── Status Bar ────────────────────────────────────────
    def _build_statusbar(self):
        self.statusbar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    # ── Actions ───────────────────────────────────────────
    def open_file(self):
        path = filedialog.askopenfilename(
            title="Open MAGDB JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            self.data = load_json(path)
            self.filepath = path
            self.file_label.config(text=os.path.basename(path), foreground="black")
            self._refresh_table()
            self._set_status(f"Loaded {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{e}")

    def save_file(self):
        if self.data is None:
            messagebox.showwarning("Warning", "No data loaded.")
            return
        if self.filepath is None:
            self.save_file_as()
            return
        try:
            save_json(self.filepath, self.data)
            self._set_status(f"Saved to {self.filepath} (backup: {self.filepath}.bak)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")

    def save_file_as(self):
        if self.data is None:
            messagebox.showwarning("Warning", "No data loaded.")
            return
        path = filedialog.asksaveasfilename(
            title="Save MAGDB JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        self.filepath = path
        self.file_label.config(text=os.path.basename(path), foreground="black")
        try:
            save_json(path, self.data)
            self._set_status(f"Saved to {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")

    def delete_selected(self):
        if self.data is None:
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "No catalogue selected.")
            return

        ids = [self.tree.item(s, "values")[0] for s in selected]
        if not messagebox.askyesno("Confirm Delete", f"Delete {len(ids)} catalogue(s)?\n\n" + "\n".join(ids)):
            return

        count = delete_catalogues(self.data, ids)
        self._refresh_table()
        self._set_status(f"Deleted {count} catalogue(s)")

    def _browse_folder(self):
        folder = filedialog.askdirectory(title="Select Catalogue Folder")
        if folder:
            self.entry_folder.delete(0, tk.END)
            self.entry_folder.insert(0, folder)

    def _on_add_catalogue(self):
        if self.data is None:
            messagebox.showwarning("Warning", "Load a JSON file first.")
            return

        name = self.entry_name.get().strip()
        folder = self.entry_folder.get().strip()
        version = self.entry_version.get().strip()

        if not name:
            messagebox.showwarning("Warning", "Please enter a catalogue name.")
            return
        if not folder:
            messagebox.showwarning("Warning", "Please select a folder.")
            return
        if not version:
            messagebox.showwarning("Warning", "Please enter a version.")
            return

        try:
            species_count, dir_found, identifier = add_catalogue(self.data, name, folder, version)
        except ValueError as e:
            messagebox.showwarning("Warning", str(e))
            return

        if not dir_found:
            messagebox.showinfo(
                "Info",
                f"Folder 'original_db' not found in:\n{folder}\n\nspeciesCount set to 0.",
            )

        self._refresh_table()
        self._set_status(
            f"Added catalogue '{name}' (identifier={identifier}, speciesCount={species_count})"
        )

        self.entry_name.delete(0, tk.END)
        self.entry_folder.delete(0, tk.END)

    # ── Helpers ───────────────────────────────────────────
    def _refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        if self.data is None:
            return
        for entry in list_catalogues(self.data):
            versions = ", ".join(v.get("version", "") for v in entry.get("versionlist", []))
            species = ", ".join(str(v.get("speciesCount", "")) for v in entry.get("versionlist", []))
            self.tree.insert(
                "",
                tk.END,
                values=(
                    entry.get("catalogueID", ""),
                    entry.get("identifier", ""),
                    entry.get("repository", "") or "",
                    versions,
                    species,
                ),
            )

    def _set_status(self, msg):
        self.statusbar.config(text=msg)


def main():
    root = tk.Tk()
    MAGDBEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
