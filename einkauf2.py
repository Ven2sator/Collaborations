# --- Importe und Setup (Definitionen)) ---
# Dieser Block importiert die notwendigen Qt-Module und Standardbibliotheken.
# Name: Importe_und_Setup
import sys
from PySide6 import QtCore, QtWidgets, QtGui

# --- Hilfsfunktion: Farbinterpolation (rot → gelb → grün) ---
# Zweck: berechnet die RGB-Farbe für einen Prozentsatz 0..100
# Name: farbinterpolation
def progress_color(percent: float) -> str:
    """
    Interpoliert eine Farbe entlang Rot -> Gelb -> Grün.
    Input: percent 0..100
    Output: CSS rgb(...) string
    """
    p = max(0.0, min(100.0, percent))
    if p <= 50:
        # Rot (255,0,0) -> Gelb (255,255,0)
        ratio = p / 50.0
        r = 255
        g = int(0 + ratio * 255)
        b = 0
    else:
        # Gelb (255,255,0) -> Grün (0,255,0)
        ratio = (p - 50.0) / 50.0
        r = int(255 - ratio * 255)
        g = 255
        b = 0
    return f"rgb({r},{g},{b})"

# --- Hauptfensterklasse: GUI, Logik, Verknüpfungen ---
# Zweck: definiert das Hauptfenster mit allen Widgets und Verhalten.
# Name: MainWindow (Hauptklasse)
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        # Konstruktor: GUI initialisieren
        super().__init__()
        self.setWindowTitle("Einkaufsverwaltung — Rezepte & Zutaten")
        # Setze dunklen blauen Hintergrund und weiße Schrift
        self.setStyleSheet("""
            QMainWindow { background-color: #001f3f; color: #ffffff; }

            QLabel { color: #ffffff; }

            QLineEdit, QTextEdit, QListWidget {
                color: #ffffff;               /* Text weiß */
                background-color: #002b59;     /* dunkleres Blau, sichtbar */
                border: 1px solid #00509e;
            }

            QPushButton {
                color: #ffffff;
                background-color: #003366;
            }

            QProgressBar {
                color: #ffffff;
            }
        """)

        # Datenmodelle: Rezepte als dict; Zutaten als dict (verfügbar: bool)
        self.recipes = {}   # {"Rezeptname": ["zut1","zut2",...]}
        self.ingredients = {}  # {"Zutat": bool}

        # Aufbau der UI
        self._create_widgets()
        self._create_layout()
        self._connect_signals()

    # --- Widgets erzeugen (Definitionen) ---
    # Zweck: instanziiert alle Widgets
    # Name: _create_widgets
    def _create_widgets(self):
        # Rezeptbereich (links oben): Eingabe für Rezeptname + Zutaten
        self.recipe_name_edit = QtWidgets.QLineEdit()
        self.recipe_name_edit.setPlaceholderText("Rezeptname")
        self.recipe_ingredients_edit = QtWidgets.QTextEdit()
        self.recipe_ingredients_edit.setPlaceholderText("Zutaten, durch Komma getrennt (z.B. Eier, Mehl, Milch)")
        self.add_recipe_btn = QtWidgets.QPushButton("Rezept hinzufügen")

        # Rezeptliste (links mitte): zeigt alle Rezepte an
        self.recipe_list = QtWidgets.QListWidget()

        # Anzeige (Mitte): zeigt Details des ausgewählten Rezepts
        self.current_recipe_label = QtWidgets.QLabel("Kein Rezept ausgewählt")
        font = self.current_recipe_label.font()
        font.setPointSize(12)
        font.setBold(True)
        self.current_recipe_label.setFont(font)
        # Fortschrittsbalken unter dem Rezeptnamen
        self.recipe_progress = QtWidgets.QProgressBar()
        self.recipe_progress.setRange(0, 100)
        self.recipe_progress.setTextVisible(True)
        # Zutatenauflistung für das Rezept: Liste mit Verfügbarkeitsanzeige
        self.recipe_ingredients_view = QtWidgets.QListWidget()

        # Zutatenverwaltung (rechts): Zutat hinzufügen + Verfügbarkeitsliste
        self.ingredient_name_edit = QtWidgets.QLineEdit()
        self.ingredient_name_edit.setPlaceholderText("Zutatenname")
        self.add_ingredient_btn = QtWidgets.QPushButton("Zutat hinzufügen")
        # Zutatenliste: mit Checkboxen (Verfügbar/fehlend)
        self.ingredient_list = QtWidgets.QListWidget()
        self.ingredient_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        # Buttons unten: Rezept löschen, Zutat löschen, Export (klein)
        self.delete_recipe_btn = QtWidgets.QPushButton("Rezept löschen")
        self.delete_ingredient_btn = QtWidgets.QPushButton("Zutat löschen (markierte)")
        self.export_btn = QtWidgets.QPushButton("Export (JSON)")

    # --- Layout erstellen (Hauptschleife UI-Aufbau) ---
    # Zweck: arrangiert Widgets in Layouts
    # Name: _create_layout
    def _create_layout(self):
        # Linke Spalte: Rezept erstellen + Liste
        recipe_group = QtWidgets.QGroupBox("Rezepte erstellen & Liste")
        left_v = QtWidgets.QVBoxLayout()
        left_v.addWidget(QtWidgets.QLabel("Neues Rezept:"))
        left_v.addWidget(self.recipe_name_edit)
        left_v.addWidget(self.recipe_ingredients_edit)
        left_v.addWidget(self.add_recipe_btn)
        left_v.addWidget(QtWidgets.QLabel("Alle Rezepte:"))
        left_v.addWidget(self.recipe_list)
        left_v.addWidget(self.delete_recipe_btn)
        recipe_group.setLayout(left_v)

        # Mittlere Spalte: Rezeptdetails
        detail_group = QtWidgets.QGroupBox("Rezeptdetails")
        mid_v = QtWidgets.QVBoxLayout()
        mid_v.addWidget(self.current_recipe_label)
        mid_v.addWidget(self.recipe_progress)
        mid_v.addWidget(QtWidgets.QLabel("Zutaten (Status):"))
        mid_v.addWidget(self.recipe_ingredients_view)
        detail_group.setLayout(mid_v)

        # Rechte Spalte: Zutatenverwaltung
        ingredient_group = QtWidgets.QGroupBox("Zutatenverwaltung")
        right_v = QtWidgets.QVBoxLayout()
        right_v.addWidget(QtWidgets.QLabel("Neue Zutat:"))
        right_v.addWidget(self.ingredient_name_edit)
        right_v.addWidget(self.add_ingredient_btn)
        right_v.addWidget(QtWidgets.QLabel("Zutaten (Verfügbar = Haken setzen):"))
        right_v.addWidget(self.ingredient_list)
        right_v.addWidget(self.delete_ingredient_btn)
        right_v.addWidget(self.export_btn)
        ingredient_group.setLayout(right_v)

        # Hauptlayout: drei Spalten
        central = QtWidgets.QWidget()
        main_h = QtWidgets.QHBoxLayout()
        main_h.addWidget(recipe_group, 3)
        main_h.addWidget(detail_group, 4)
        main_h.addWidget(ingredient_group, 3)
        central.setLayout(main_h)
        self.setCentralWidget(central)

    # --- Signale & Slots verbinden (Interaktivität) ---
    # Zweck: verknüpft Buttons/Listen mit Methoden
    # Name: _connect_signals
    def _connect_signals(self):
        self.add_recipe_btn.clicked.connect(self.add_recipe)
        self.add_ingredient_btn.clicked.connect(self.add_ingredient)
        self.recipe_list.itemSelectionChanged.connect(self.on_recipe_selected)
        self.ingredient_list.itemChanged.connect(self.on_ingredient_toggled)
        self.delete_recipe_btn.clicked.connect(self.delete_selected_recipe)
        self.delete_ingredient_btn.clicked.connect(self.delete_marked_ingredients)
        self.export_btn.clicked.connect(self.export_json)

    # --- Logik: Rezept hinzufügen ---
    # Zweck: Liest Felder, speichert Rezept und aktualisiert UI
    # Name: add_recipe
    def add_recipe(self):
        name = self.recipe_name_edit.text().strip()
        if not name:
            QtWidgets.QMessageBox.warning(self, "Fehler", "Bitte einen Rezeptnamen eingeben.")
            return
        # Zutaten durch Komma trennen, trimmen, leere entfernen
        raw = self.recipe_ingredients_edit.toPlainText()
        ingredients = [z.strip() for z in raw.split(",") if z.strip()]
        # Speichere Rezept (überschreibt bestehendes mit gleichem Namen)
        self.recipes[name] = ingredients
        self._refresh_recipe_list()
        # Reset Eingabefelder
        self.recipe_name_edit.clear()
        self.recipe_ingredients_edit.clear()

    # --- UI-Aktualisierung: Rezeptliste neu zeichnen ---
    # Zweck: füllt die QListWidget der Rezepte
    # Name: _refresh_recipe_list
    def _refresh_recipe_list(self):
        self.recipe_list.clear()
        for name in sorted(self.recipes.keys()):
            item = QtWidgets.QListWidgetItem(name)
            self.recipe_list.addItem(item)

    # --- Logik: Zutat hinzufügen ---
    # Zweck: Zutat in ingredients dict hinzufügen (standard: nicht verfügbar)
    # Name: add_ingredient
    def add_ingredient(self):
        name = self.ingredient_name_edit.text().strip()
        if not name:
            QtWidgets.QMessageBox.warning(self, "Fehler", "Bitte einen Zutatenamen eingeben.")
            return
        if name in self.ingredients:
            QtWidgets.QMessageBox.information(self, "Hinweis", "Zutat existiert bereits.")
            return
        # Standardmäßig nicht verfügbar (False)
        self.ingredients[name] = False
        self._refresh_ingredient_list()
        self.ingredient_name_edit.clear()
        self._update_all_recipe_displays()

    # --- UI-Aktualisierung: Zutatenliste neu zeichnen (mit Checkboxen) ---
    # Zweck: füllt die QListWidget der Zutaten und setzt Checkboxen
    # Name: _refresh_ingredient_list
    def _refresh_ingredient_list(self):
        self.ingredient_list.blockSignals(True)
        self.ingredient_list.clear()
        for name in sorted(self.ingredients.keys()):
            item = QtWidgets.QListWidgetItem(name)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked if self.ingredients[name] else QtCore.Qt.Unchecked)
            self.ingredient_list.addItem(item)
        self.ingredient_list.blockSignals(False)

    # --- Reaktion auf Zutatstoggle (Checkbox geändert) ---
    # Zweck: beim An-/Abhaken einer Zutat wird das Modell aktualisiert
    # Name: on_ingredient_toggled
    def on_ingredient_toggled(self, item: QtWidgets.QListWidgetItem):
        name = item.text()
        checked = item.checkState() == QtCore.Qt.Checked
        self.ingredients[name] = checked
        # Aktualisiere Anzeige der Rezepte
        self._update_all_recipe_displays()

    # --- Wenn ein Rezept ausgewählt wird: Detail-Anzeige füllen ---
    # Zweck: zeigt Zutatenliste und Fortschritt des Rezepts
    # Name: on_recipe_selected
    def on_recipe_selected(self):
        items = self.recipe_list.selectedItems()
        if not items:
            self.current_recipe_label.setText("Kein Rezept ausgewählt")
            self.recipe_ingredients_view.clear()
            self.recipe_progress.setValue(0)
            self.recipe_progress.setFormat("")
            return
        name = items[0].text()
        self._show_recipe_details(name)

    # --- Anzeige aktualisieren für ein bestimmtes Rezept ---
    # Zweck: füllt die Zutatenanzeige und setzt den Fortschrittsbalken farblich
    # Name: _show_recipe_details
    def _show_recipe_details(self, name: str):
        ingredients = self.recipes.get(name, [])
        self.current_recipe_label.setText(name)
        self.recipe_ingredients_view.clear()
        if not ingredients:
            self.recipe_progress.setValue(0)
            self.recipe_progress.setFormat("Keine Zutaten definiert")
            return
        # Zähle verfügbare Zutaten
        total = len(ingredients)
        available = 0
        for z in ingredients:
            # Verfügbarkeit: True wenn in ingredients dict und True
            avail = self.ingredients.get(z, False)
            if avail:
                available += 1
            # Erzeuge Eintrag mit Text und kleinem Indikator im Text (●)
            item = QtWidgets.QListWidgetItem(f"{z} — {'verfügbar' if avail else 'fehlend'}")
            # Setze Farbe des Eintrags (hellgrün/hellrot) für schnelle Lesbarkeit
            if avail:
                item.setForeground(QtGui.QBrush(QtGui.QColor(180, 255, 180)))
            else:
                item.setForeground(QtGui.QBrush(QtGui.QColor(255, 180, 180)))
            self.recipe_ingredients_view.addItem(item)
        percent = (available / total) * 100
        # Setze Fortschritt und Format
        self.recipe_progress.setValue(int(percent))
        self.recipe_progress.setFormat(f"{available}/{total} Zutaten verfügbar ({int(percent)}%)")
        # Style: passe die Chunk-Farbe an die berechnete Farbe an
        color = progress_color(percent)
        # QProgressBar::chunk steuert die Füllfarbe
        self.recipe_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 4px;
                background: rgba(255,255,255,0.03);
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)

    # --- Hilfsfunktion: alle Rezeptanzeigen aktualisieren (bei Zutatänderung) ---
    # Zweck: sorgt dafür, dass aktuell ausgewähltes Rezept/Progressbar aktualisiert wird
    # Name: _update_all_recipe_displays
    def _update_all_recipe_displays(self):
        # Wenn ein Rezept ausgewählt ist, zeige Details neu (damit Progressbar und Liste aktualisiert werden)
        sel = self.recipe_list.selectedItems()
        if sel:
            self._show_recipe_details(sel[0].text())

    # --- Löschen: ausgewähltes Rezept entfernen ---
    # Zweck: löscht markiertes Rezept aus Datenmodell
    # Name: delete_selected_recipe
    def delete_selected_recipe(self):
        sel = self.recipe_list.selectedItems()
        if not sel:
            return
        name = sel[0].text()
        del self.recipes[name]
        self._refresh_recipe_list()
        self.recipe_ingredients_view.clear()
        self.recipe_progress.setValue(0)
        self.current_recipe_label.setText("Kein Rezept ausgewählt")

    # --- Löschen markierter Zutaten in der rechten Liste ---
    # Zweck: entfernt Zutaten, die in ingredient_list markiert (ausgewählt) sind
    # Name: delete_marked_ingredients
    def delete_marked_ingredients(self):
        # Hier: löschen derjenigen, die markiert/ausgewählt sind (we use selection to pick)
        selected = self.ingredient_list.selectedItems()
        if not selected:
            QtWidgets.QMessageBox.information(self, "Hinweis", "Bitte Zutaten markieren (Auswahl), die gelöscht werden sollen.")
            return
        for it in selected:
            name = it.text()
            if name in self.ingredients:
                del self.ingredients[name]
        self._refresh_ingredient_list()
        self._update_all_recipe_displays()

    # --- Exportfunktion (einfach JSON in Datei speichern) ---
    # Zweck: ermöglicht Export der Rezepte + Zutaten (einfacher Datensicherung)
    # Name: export_json
    def export_json(self):
        import json
        data = {"recipes": self.recipes, "ingredients": self.ingredients}
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Exportieren als JSON", "einkauf_export.json", "JSON-Datei (*.json)")
        if not fname:
            return
        try:
            with open(fname, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            QtWidgets.QMessageBox.information(self, "Export", f"Export erfolgreich: {fname}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Fehler", f"Export fehlgeschlagen:\n{e}")

# --- Programmstart (Hauptschleife) ---
# Zweck: startet die Qt-Anwendung und zeigt das Hauptfenster
# Name: main
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.resize(1000, 640)
    window.show()
    sys.exit(app.exec())

# Wenn diese Datei direkt ausgeführt wird, starte die Anwendung.
if __name__ == "__main__":
    main()