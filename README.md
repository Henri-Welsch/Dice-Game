# Verteilte Systeme - Übung 1

Dieses Repository enthält die Lösungen für die Übung 1 des Moduls "Verteilte Systeme". Es umfasst zwei Hauptaufgaben: Uhrensynchronisation und ein verteiltes Würfelspiel. Die Implementierungen und Berichte sind in diesem Repository zu finden.

## Inhaltsverzeichnis

- [Aufgabe 1: Uhrensynchronisation](#aufgabe-1-uhrensynchronisation)
- [Aufgabe 2: Verteiltes Würfelspiel](#aufgabe-2-verteiltes-würfelspiel)
  - [Teilaufgabe 2a](#teilaufgabe-2a)
  - [Teilaufgabe 2b](#teilaufgabe-2b)
  - [Teilaufgabe 2c](#teilaufgabe-2c)
- [Ergebnisse und Diskussion](#ergebnisse-und-diskussion)
- [Setup und Ausführung](#setup-und-ausführung)

## Aufgabe 1: Uhrensynchronisation

Ziel dieser Aufgabe war es, die Genauigkeit der lokalen Uhr eines Rechners über einen Zeitraum von mindestens einer Stunde kontinuierlich mit einem oder mehreren Zeitservern aus dem Internet zu vergleichen. 

### Durchführung

1. **Zeitserverauswahl**: Es wurde der NTP-Zeitserver `time.google.com` verwendet.
2. **Datenabfrage**: Abfragen wurden alle 5 Sekunden durchgeführt, um die lokale Uhrzeit und die NTP-Serverzeit zu erfassen.
3. **Datenspeicherung**: Ergebnisse wurden in einer CSV-Datei gespeichert (`data.csv`).
4. **Datenvisualisierung**: Die Ergebnisse wurden mit der Python-Bibliothek `matplotlib` visualisiert.

### Ergebnis

Ein Diagramm zeigt die Abweichungen der lokalen Uhrzeit von der NTP-Serverzeit. Die Daten zeigen eine geringe, aber konstante Drift der lokalen Uhr.

## Aufgabe 2: Verteiltes Würfelspiel

Ziel war es, ein verteiltes Würfelspiel zu entwickeln, das aus einem Spielleiter und mehreren Spielern besteht. Das Spiel wurde in mehreren Implementierungen realisiert.

### Teilaufgabe 2a

- **Technologieauswahl**: Implementierung mit Flask und SocketIO.
- **Spielablauf**: Der Spielleiter sendet START-Nachrichten, Spieler warten zufällig, würfeln und senden ihre Ergebnisse zurück.
- **Ergebnisprotokollierung**: Ergebnisse werden in einer CSV-Datei protokolliert.

### Teilaufgabe 2b

- **Logische Uhren**: Verwendung von Vektoruhren zur Kausalitätsbewahrung.
- **Spielablauf**: Spieler und Spielleiter aktualisieren ihre Vektoruhren bei jeder Nachricht.

### Teilaufgabe 2c

- **Lokale Ausführung**: Das Spiel wurde mit mehreren Tabs auf einem lokalen Rechner simuliert.

## Ergebnisse und Diskussion

- **Teilaufgabe 2a**: Funktionierende Webanwendung mit Echtzeitkommunikation.
- **Teilaufgabe 2b**: Sicherstellung der Kausalität durch Vektoruhren.
- **Teilaufgabe 2c**: Konsistente Ergebnisse bei lokaler Ausführung.

## Setup und Ausführung

### Voraussetzungen

- Python 3.x
- Flask
- Flask-SocketIO
- matplotlib

### Installation

1. Klone das Repository:
   git clone <repository-url>
   cd <repository-directory>

2. Installiere die Abhängigkeiten:
   pip install -r requirements.txt

## Ausführung

### Aufgabe 1

1. Führe das Skript zur Uhrensynchronisation aus:
   python time_sync.py
   
3. Erstelle das Diagramm:
   python plot_results.py
   
### Aufgabe 2

1. Starte den Server:
   python server.py
   
3. Starte die Spieler (in separaten Terminals):
   python player.py --name Spieler1
   python player.py --name Spieler2
   python player.py --name Spieler3
