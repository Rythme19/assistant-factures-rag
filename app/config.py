"""Tous les réglages du projet, regroupés à un seul endroit."""
from pathlib import Path

RACINE = Path(__file__).parent.parent
DOSSIER_FACTURES = RACINE / "data" / "factures"
DOSSIER_OFFICIEL = RACINE / "data" / "officiel"
DOSSIER_CHROMA = RACINE / "data" / "chroma"
FICHIER_MONTANTS = RACINE / "data" / "montants.csv"

# Un client = un sous-dossier de data/factures.
CLIENTS = sorted(d.name for d in DOSSIER_FACTURES.glob("*") if d.is_dir())
# Valeur du champ « client » pour les textes officiels, visibles par tous.
COMMUN = "commun"

# Modèle multilingue léger (118 millions de paramètres, environ 470 Mo) qui tourne
# en local : aucun texte de facture n'est envoyé à l'extérieur pour calculer les vecteurs.
MODELE_VECTEURS = "intfloat/multilingual-e5-small"
TAILLE_PASSAGE = 1200  # longueur maximale d'un passage, en caractères
RECOUVREMENT = 200     # caractères repris d'un passage au suivant
NB_PASSAGES = 4        # passages retenus par recherche (factures du client, textes officiels)

# Si le meilleur passage est plus loin que cette distance, la question est jugée hors sujet.
# Valeur mesurée : les questions pertinentes vont jusqu'à 0,183, les questions
# clairement hors sujet commencent à 0,204 (voir le README).
# Limite connue : l'écart est faible, ce seuil n'arrête que le hors-sujet évident.
DISTANCE_MAX = 0.195

# Modèle utilisé selon la clé présente dans l'environnement (voir app/llm.py).
MODELE_GROQ = "openai/gpt-oss-120b"  # modèle ouvert, hébergé par Groq
MODELE_CLAUDE = "claude-opus-5-5"
