Projet : IA Génétique pour Jeu Vidéo 2D

Ce projet implémente une Intelligence Artificielle (IA) basée sur un algorithme génétique utilisant la librairie NEAT (NeuroEvolution of Augmenting Topologies).
L'objectif est de permettre à une IA d'apprendre à jouer à un jeu 2D en s'améliorant de génération en génération grâce à un processus évolutif.

🛠️ Environnement requis

    Python : version 3.10 ou supérieure

📦 Dépendances :

    Pygame : pour gérer la structure et les interactions dans le jeu.
    NEAT-Python : pour l'évolution génétique des réseaux de neurones.

Installez les dépendances via :

    pip install pygame neat-python

📂 Structure du projet

    .
    |-- assets/               # Dossier contenant les fichiers et ressources du jeu (images, arrière-plans, etc.)
    |-- second.py             # Script principal où l'algorithme génétique est implémenté
    |-- config-neat.txt       # Fichier de configuration pour NEAT (paramètres génétiques et réseau)

🚀 Fonctionnalités principales

    Définition des classes du jeu :
    Utilisation de Pygame pour modéliser les entités du jeu (joueur, objets, environnements).

    Classe Game :
    Fournit un environnement simulé où les génomes peuvent être évalués.

    Évaluation d'un génome (eval_genom) :
        Chaque génome est testé dans une instance du jeu.
        Le score (fitness) est attribué en fonction des performances du génome (collecte d'objets, évitement des obstacles, progression dans le niveau).

    Évaluation d'une population (eval_genomes) :
        Tous les génomes d'une génération sont évalués.
        Utilisation de multiprocessing pour accélérer l'évaluation en parallèle.

    Entraînement et évolution (run_neat) :
        Initialisation d'une population de génomes.
        Entraînement sur plusieurs générations.
        Sauvegarde du meilleur génome sous forme d'un fichier pickle (winner.pkl).

    Test du génome gagnant :
        Permet de charger et tester le génome ayant obtenu le meilleur score après l'entraînement.

⚙️ Utilisation :

1️⃣ Configuration de NEAT

    Ajustez les paramètres génétiques dans le fichier config-neat.txt (nombre de neurones, mutations, stagnation, etc.).

2️⃣ Lancer l'entraînement

Exécutez le script principal pour démarrer l'entraînement de l'IA :

python second.py

3️⃣ Tester le génome gagnant

Une fois l'entraînement terminé, le génome gagnant est sauvegardé dans winner.pkl. Chargez ce génome pour observer ses performances dans le jeu.
📈 Optimisation du Fitness

Le score (fitness) de chaque génome est calculé en fonction :

    Des objets collectés (exemple : pommes).
    Du niveau atteint (progresser dans le jeu augmente la fitness).
    Des erreurs commises (chutes ou collisions réduisent la fitness).

🖼️ Améliorations possibles

    Utiliser les niveaux généré aléatoirement en y ajoutant des obstacles pour enrichir l'apprentissage de l'IA.
    Ajuster les paramètres de mutation et croisement pour améliorer l'évolution.
    Visualiser en temps réel les décisions de l'IA (debugging).

🧠 Inspiration

Ce projet démontre comment utiliser un algorithme génétique pour entraîner une IA à jouer à un jeu simple.
NEAT est particulièrement puissant pour concevoir des réseaux de neurones capables d'apprendre des tâches complexes de manière autonome.

    