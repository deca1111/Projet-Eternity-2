# Projet du cours INF6102 de Polytechnique Montréal - Hiver 2024

## Équipe
- Armel Ngounou Tchawe - 2238017
- Léo Valette - 2307835

## Arborescence

```
2238017_2307835_Projet.zip
|
└─ README.md : Ce fichier
|
└─ bestSolutionsRendu : Dossier contenant les meilleures solutions trouvées pour chaque instance
|   └─ solutionX.txt : Meilleure solution trouvée pour l'instance X
|     ...
|   └─ visu_eternity_X.png : Visualisation de la meilleure solution trouvée pour l'instance X
|     ...
|
└─ instances : Dossier contenant les instances
|   └─ eternity_X.txt : Instance X
|     ...
|
└─ 2238017_2307835_Projet.pdf : Rapport du projet
|
└─ xx.py : Code source
|   ...
|
└─ requirements.txt : Fichier de dépendances
```

## Lancer le projet

### Installation des dépendances
```bash
pip install -r requirements.txt
```

### Exécution du projet
```bash
python main.py --agent=<agent> --infile=<instance>
```
avec `<agent>` le nom de l'agent à utiliser parmis `random`, `heuristic`, `local_search` et `advanced`.  
avec `<instance>` le chemin vers le fichier d'instance.

Exemple:
```bash
python main.py --agent=heuristic --infile=./instances/eternity_B.txt
```