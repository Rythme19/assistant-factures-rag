"""Service REST : POST /ask pour poser une question, GET /health pour l'état du service,
GET /totaux pour les totaux par fournisseur.

Usage : uvicorn app.api:app
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app import llm
from app.base import collection, modele
from app.config import CLIENTS
from app.montants import totaux_par_fournisseur
from app.recherche import chercher

app = FastAPI(title="Assistant factures (RAG)")
modele()  # chargé dès le démarrage, pour que la première question ne soit pas lente


class Question(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    client: str


class Source(BaseModel):
    source: str
    page: int
    type_document: str
    client: str
    distance: float
    texte: str


class Reponse(BaseModel):
    reponse: str
    sources: list[Source]


@app.get("/health")
def health() -> dict:
    return {"statut": "ok", "passages": collection().count(), "clients": CLIENTS}


def verifier_client(client: str) -> None:
    """Refuse tout client qui n'a pas de dossier de factures."""
    if client not in CLIENTS:
        raise HTTPException(status_code=404, detail="Client inconnu")


@app.get("/totaux")
def totaux(client: str) -> list[dict]:
    """Totaux par fournisseur, obtenus par un calcul et non par le modèle de langage."""
    verifier_client(client)
    return totaux_par_fournisseur(client)


@app.post("/ask")
def ask(demande: Question) -> Reponse:
    verifier_client(demande.client)

    passages = chercher(demande.question, demande.client)
    if not passages:
        # Rien de pertinent dans les documents : on le dit, sans appeler le modèle.
        return Reponse(reponse=llm.JE_NE_SAIS_PAS, sources=[])

    try:
        texte = llm.generer(demande.question, passages)
    except llm.ModeleIndisponible as erreur:
        texte = f"Réponse non générée : {erreur}. Les passages trouvés sont listés ci-dessous."
    return Reponse(reponse=texte, sources=passages)
