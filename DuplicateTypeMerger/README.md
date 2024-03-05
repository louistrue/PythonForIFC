### VirtualElementConverter Benutzerhandbuch 📘

## Inhaltsverzeichnis

1. [Übersicht](#übersicht)
2. [Anforderungen](#anforderungen)
3. [Installation](#installation)
4. [Verwendung](#verwendung)
   - [Anwendung starten](#anwendung-starten)
   - [Benutzeroberfläche](#benutzeroberfläche)
   - [IFC-Datei laden](#ifc-datei-laden)
   - [IFC-Klassen anzeigen](#ifc-klassen-anzeigen)
   - [Umwandlung in IfcVirtualElement](#umwandlung-in-ifcvirtualelement)
   - [Modifizierte Datei speichern](#modifizierte-datei-speichern)
- [Contributing](#contributing-)
- [License](#license-)
- [Acknowledgments](#acknowledgments-)

---

## Übersicht

Der VirtualElementConverter ist ein nützliches Tool zur Umwandlung bestimmter IFC-Klassen in `IfcVirtualElement`. Es ermöglicht eine vereinfachte Darstellung komplexer Baustrukturen und verbessert die Gesamtleistung Ihrer IFC-Projekte.

---

## Anforderungen

- Python 3.x
- PyQt5
- ifcopenshell

---

## Installation

1. Installieren Sie Python 3.x, falls noch nicht geschehen.
2. Installieren Sie die erforderlichen Python-Pakete mit dem Befehl `pip install PyQt5 ifcopenshell`.

---

## Verwendung

### Anwendung starten

Führen Sie das Python-Skript aus, um die Anwendung zu starten.

### Benutzeroberfläche

Nach dem Start der Anwendung wird die Haupt-Benutzeroberfläche angezeigt, die alle notwendigen Optionen für den Konvertierungsprozess enthält.

### IFC-Datei laden

Klicken Sie auf die Schaltfläche "IFC-Datei laden", um den Dateidialog zu öffnen und die gewünschte IFC-Datei auszuwählen.

### IFC-Klassen anzeigen

Ein Dropdown-Menü listet alle verfügbaren IFC-Klassen in der geladenen Datei auf. Wählen Sie die Klasse, die Sie in `IfcVirtualElement` umwandeln möchten.

### Umwandlung in IfcVirtualElement

Nach der Auswahl der IFC-Klasse, klicken Sie auf die Schaltfläche "Konvertieren", um den Umwandlungsprozess zu starten.

### Modifizierte Datei speichern

Nach der Umwandlung wird ein "Speichern unter"-Dialog angezeigt. Geben Sie den Speicherort und den Dateinamen für die modifizierte IFC-Datei an.

---

## Contributing 🤝

For contributions, please create a new branch and submit a Pull Request.

---

## License 📜

tbd 

---

## Acknowledgments 👏

- IfcOpenShell https://ifcopenshell.org