# Vortrag

## Einleitung (1:00 Minuten)
- Begrüßung 
- Was ist Pokémon
    - Videospiel-Franchise aus Japan
    - Klassisches RPG, Pokémon fangen, trainieren und tauschen
        - Ziel: Der aller beste sein

- Arbeit: Verschiedene Strategien für Kämpfe
- Weil fangen und trainieren sehr Zeitintensiv, Kampf-Simulatoren wie 
    Showdown (Screenshot: Oben links)

## Spieltheoretische Einordnung (3:10 Minuten - 4:10)
- Es kämpfen zwei Spieler Gegeneinander
- Ziel: alle Pokemon des Gegners besiegen
- Unvollständige Information: Ähnlich wie bei Poker, man kennt nicht alle Optionen des Gegners, kann aber gut schätzen
- Mainline: Fange, trainieren. Hier: zufälliges Team. Man kennt eigenes Team, nur das erste vom Gegner (Bezug zum Bild).
- Warum nicht OU: Es gibt kein "bestes" Team, jedes Team in unterschiedlichen Szenarien gut. Meta verändert sich.
- Wir spielen daher Generation 8 random battles
- Ausgangs-States: Welche Pokemon, welche Varianten
    - $1.5 \times 10^{39}$

## Literatur (2:10 Minuten - 6:20)
- Suchbasiert: Expecti-Minimax:
    - Zusätzlich zu Min / Max Nodes: "Chance" Nodes: erwarteter Wert eines Zufallsereignisses
- Elo / Glicko: Vorlesen (wir sind etwas schlechter, Gründe am Schluss)
- Reinforcement Leraning:
    - Embeddings
    - Kein LSTM
- Kritik an Evaluation
- 612 / 388

## Menschen (0:20 Minuten - 6:40)

## Ansatz der Arbeit (2:10 Minuten -  8:50)
- Zwei Phasen mit verschiedenen Zielen:
    - Discorvery Phase:
        - Passiv spielen
        - Informationen Gewinnen
        - Hazards und status für langfristige Vorteile
            - Stealth Rock: Schaden beim Einwechseln
            - Sticky Web: Verringern Tempo
            - Burn: Schaden
    - Defeat Phase:
        - Solider Matchplan
        - Bestimme welcher Gegner wie besiegt werden kann
        - Minimax: Nicht stumpf n Züge voraus berechnen sondern Matchups
            - Verbesserungspotential: BRN / Boost

## Graphen (3:00 Minuten - 11:50)
- Elo:
    - Zwei Agenten
    - HerrDonner: Guter OTL
    - HerrGewitter: Beschriebener Agent

- Fairness:
    - Wie fair sind die Spiele