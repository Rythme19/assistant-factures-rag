"""Ingestion : lit les PDF, les découpe en passages et les range dans Chroma.

Usage : python -m app.ingestion
"""
import logging
import re
from pathlib import Path

from pypdf import PdfReader

from app import montants
from app.base import calculer_vecteurs, collection
from app.config import (CLIENTS, COMMUN, DOSSIER_FACTURES, DOSSIER_OFFICIEL,
                        RECOUVREMENT, TAILLE_PASSAGE)

logging.getLogger("pypdf").setLevel(logging.ERROR)  # masque les avertissements de lecture


def lire_pages(chemin: Path) -> list[tuple[int, str]]:
    """Renvoie (numéro de page, texte) pour chaque page du PDF."""
    pages = PdfReader(chemin).pages
    return [(numero, page.extract_text() or "") for numero, page in enumerate(pages, start=1)]


def decouper(texte: str, taille: int = TAILLE_PASSAGE, recouvrement: int = RECOUVREMENT) -> list[str]:
    """Découpe un texte en passages de `taille` caractères au plus.

    Deux passages voisins partagent `recouvrement` caractères, pour qu'une phrase
    coupée entre deux passages reste lisible dans l'un des deux.
    """
    # Nettoyage : un seul espace entre les mots, pas de lignes vides.
    texte = re.sub(r"[ \t]+", " ", texte)
    texte = re.sub(r"\s*\n\s*", "\n", texte).strip()
    passages, debut = [], 0
    while debut + taille < len(texte):
        # On coupe sur le dernier espace, pour ne pas couper un mot.
        fin = texte.rfind(" ", debut + recouvrement, debut + taille)
        if fin == -1:
            fin = debut + taille
        passages.append(texte[debut:fin].strip())
        debut = fin - recouvrement
    passages.append(texte[debut:].strip())
    return passages


def lister_documents() -> list[tuple[Path, str, str]]:
    """Renvoie (chemin, type de document, client) pour chaque PDF à ingérer."""
    documents = [(pdf, "texte_officiel", COMMUN) for pdf in sorted(DOSSIER_OFFICIEL.glob("*.pdf"))]
    for client in CLIENTS:
        # Le client d'une facture est le dossier où elle est rangée.
        factures = sorted((DOSSIER_FACTURES / client).glob("*.pdf"))
        documents += [(pdf, "facture", client) for pdf in factures]
    return documents


def main() -> None:
    identifiants, textes, metadonnees, lignes_montants = [], [], [], []
    for chemin, type_document, client in lister_documents():
        for page, texte in lire_pages(chemin):
            if type_document == "facture":  # les totaux vont aussi dans le tableau des montants
                lignes_montants.append({"client": client, "fichier": chemin.name,
                                        **montants.extraire(texte)})
            for rang, passage in enumerate(decouper(texte)):
                if len(passage) < 100:  # page de garde ou page vide : rien à chercher dedans
                    continue
                identifiants.append(f"{client}/{chemin.name}/p{page}/{rang}")
                textes.append(passage)
                metadonnees.append({"source": chemin.name, "page": page,
                                    "type_document": type_document, "client": client})

    base = collection()
    anciens = base.get(include=[])["ids"]
    if anciens:  # on repart de zéro pour ne pas garder de passages périmés
        base.delete(ids=anciens)
    base.add(ids=identifiants, documents=textes, metadatas=metadonnees,
             embeddings=calculer_vecteurs(textes, "passage"))
    montants.enregistrer(lignes_montants)
    print(f"{len(textes)} passages rangés dans la base ({len(lister_documents())} documents)")


if __name__ == "__main__":
    main()
