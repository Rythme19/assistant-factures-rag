"""Montants : range les totaux des factures dans un tableau et les additionne par le calcul.

Un RAG retrouve des passages, il ne sait pas additionner quinze factures.
Les questions de total passent donc par ce fichier, sans modèle de langage.
"""
import csv
import re
from decimal import Decimal

from app.config import FICHIER_MONTANTS

COLONNES = ["client", "fichier", "fournisseur", "numero", "date", "total_ht", "tva", "total_ttc"]


def en_decimal(montant: str) -> Decimal:
    """'1 234,56' -> Decimal('1234.56'). Decimal évite les erreurs d'arrondi des float."""
    return Decimal(montant.replace(" ", "").replace(",", "."))


def extraire(texte: str) -> dict:
    """Lit le fournisseur, le numéro, la date et les totaux dans le texte d'une facture.

    Limite connue : suppose une facture d'une page, au format du générateur.
    De vraies factures, toutes différentes, demanderaient une extraction plus robuste.
    """
    def trouver(motif: str) -> str:
        resultat = re.search(motif, texte)
        if resultat is None:  # on préfère une erreur claire à un total faux
            raise ValueError(f"Information introuvable dans la facture : {motif}")
        return resultat.group(1)

    jour, mois, annee = trouver(r"Date d'émission : (\S+)").split("/")
    return {
        "fournisseur": trouver(r"VENDEUR\n(.+)"),
        "numero": trouver(r"Facture n° (\S+)"),
        "date": f"{annee}-{mois}-{jour}",
        "total_ht": en_decimal(trouver(r"Total HT : ([\d ]+,\d\d)")),
        "tva": en_decimal(trouver(r"Total TVA : ([\d ]+,\d\d)")),
        "total_ttc": en_decimal(trouver(r"Total TTC : ([\d ]+,\d\d)")),
    }


def enregistrer(lignes: list[dict]) -> None:
    """Écrit le tableau des montants (une ligne par facture) dans un fichier CSV."""
    with open(FICHIER_MONTANTS, "w", newline="", encoding="utf-8") as fichier:
        tableau = csv.DictWriter(fichier, fieldnames=COLONNES)
        tableau.writeheader()
        tableau.writerows(lignes)


def totaux_par_fournisseur(client: str) -> list[dict]:
    """Additionne les factures d'un client, fournisseur par fournisseur."""
    totaux = {}
    with open(FICHIER_MONTANTS, newline="", encoding="utf-8") as fichier:
        for ligne in csv.DictReader(fichier):
            if ligne["client"] != client:  # cloisonnement : seulement les factures de ce client
                continue
            total = totaux.setdefault(ligne["fournisseur"], {
                "fournisseur": ligne["fournisseur"], "factures": 0,
                "total_ht": Decimal(0), "tva": Decimal(0), "total_ttc": Decimal(0)})
            total["factures"] += 1
            for colonne in ("total_ht", "tva", "total_ttc"):
                total[colonne] += Decimal(ligne[colonne])
    return sorted(totaux.values(), key=lambda total: total["total_ttc"], reverse=True)
