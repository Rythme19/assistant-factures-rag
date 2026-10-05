"""La base vectorielle : le modèle qui calcule les vecteurs et la collection Chroma."""
from functools import lru_cache

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from app.config import DOSSIER_CHROMA, MODELE_VECTEURS


@lru_cache
def modele() -> SentenceTransformer:
    """Charge le modèle une seule fois (c'est lent), puis le garde en mémoire."""
    return SentenceTransformer(MODELE_VECTEURS)


def calculer_vecteurs(textes: list[str], role: str) -> list[list[float]]:
    """Transforme des textes en vecteurs.

    `role` vaut "query" pour une question et "passage" pour un document :
    le modèle e5 a été entraîné avec ces deux préfixes.
    """
    prefixes = [f"{role}: {texte}" for texte in textes]
    return modele().encode(prefixes, normalize_embeddings=True).tolist()


@lru_cache
def collection():
    """Ouvre la collection Chroma enregistrée sur le disque."""
    client = chromadb.PersistentClient(
        path=str(DOSSIER_CHROMA),
        settings=Settings(anonymized_telemetry=False),  # aucune statistique envoyée
    )
    # "cosine" : la distance mesure l'angle entre deux vecteurs (0 = même sens).
    return client.get_or_create_collection("passages", metadata={"hnsw:space": "cosine"})
