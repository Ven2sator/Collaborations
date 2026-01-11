import tkinter as tk
from tkinter import ttk
import csv
import os

FILE = "inhalte.csv"

class InhaltsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Buch-Inhaltsverzeichnisse")
        self.mode = "Neu"  # oder "Alt"

        self.data = []
        self.load_data()

        # --- Hauptmenü ---
        menu = ttk.Frame(root)
        menu.pack(fill="x")

        ttk.Button(menu, text="Inhalt hinzufügen", command=self.add_view).pack(side="left", padx=5)
        ttk.Button(menu, text="Neu", command=lambda: self.list_view("Neu")).pack(side="left")
        ttk.Button(menu, text="Alt", command=lambda: self.list_view("Alt")).pack(side="left")

        self.main = ttk.Frame(root)
        self.main.pack(fill="both", expand=True)

        self.list_view("Neu")

    # ---------- CSV ----------
    def load_data(self):
        if os.path.exists(FILE):
            with open(FILE, newline="", encoding="utf-8") as f:
                self.data = list(csv.DictReader(f))
        else:
            self.data = []

    def save_data(self):
        with open(FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["titel", "inhalt", "status"])
            writer.writeheader()
            writer.writerows(self.data)

    # ---------- Views ----------
    def clear(self):
        for w in self.main.winfo_children():
            w.destroy()

    def add_view(self):
        self.clear()

        ttk.Label(self.main, text="Titel").pack(anchor="w")
        titel = ttk.Entry(self.main)
        titel.pack(fill="x")

        ttk.Label(self.main, text="Inhalt").pack(anchor="w", pady=(10, 0))
        inhalt = tk.Text(self.main, height=15)
        inhalt.pack(fill="both", expand=True)

        def speichern():
            self.data.append({
                "titel": titel.get(),
                "inhalt": inhalt.get("1.0", "end").strip(),
                "status": "Neu"
            })
            self.save_data()
            self.list_view("Neu")

        ttk.Button(self.main, text="Speichern", command=speichern).pack(pady=5)

    def list_view(self, status):
        self.mode = status
        self.clear()

        for item in self.data:
            if item["status"] == status:
                row = ttk.Frame(self.main)
                row.pack(fill="x", pady=2)

                ttk.Button(
                    row,
                    text=item["titel"],
                    command=lambda i=item: self.edit_view(i)
                ).pack(side="left", fill="x", expand=True)

                ttk.Button(
                    row,
                    text="X",
                    width=3,
                    command=lambda i=item: self.delete(i)
                ).pack(side="right")

    def edit_view(self, item):
        self.clear()

        titel = ttk.Entry(self.main)
        titel.insert(0, item["titel"])
        titel.pack(fill="x")

        inhalt = tk.Text(self.main, height=15)
        inhalt.insert("1.0", item["inhalt"])
        inhalt.pack(fill="both", expand=True)

        def speichern():
            item["titel"] = titel.get()
            item["inhalt"] = inhalt.get("1.0", "end").strip()
            self.save_data()
            self.list_view(item["status"])

        def verschieben():
            item["status"] = "Alt" if item["status"] == "Neu" else "Neu"
            self.save_data()
            self.list_view(item["status"])

        btns = ttk.Frame(self.main)
        btns.pack(pady=5)

        ttk.Button(btns, text="Speichern", command=speichern).pack(side="left", padx=5)
        ttk.Button(btns, text="Verschieben", command=verschieben).pack(side="left")

    def delete(self, item):
        self.data.remove(item)
        self.save_data()
        self.list_view(self.mode)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x500")
    InhaltsApp(root)
    root.mainloop()
