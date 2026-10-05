"""Tests des montants : l'extraction doit retrouver exactement ce que le générateur a écrit."""
import csv
from decimal import Decimal

from app.config import CLIENTS, DOSSIER_FACTURES, FICHIER_MONTANTS
from app.montants import en_decimal, totaux_par_fournisseur


def lire_csv(chemin) -> list[dict]:
    with open(chemin, newline="", encoding="utf-8") as fichier:
        return list(csv.DictReader(fichier))


MANIFESTE = lire_csv(DOSSIER_FACTURES / "manifeste.csv")  # écrit par scripts/generer_factures.py


def test_conversion_d_un_montant_francais():
    assert en_decimal("1 234,56") == Decimal("1234.56")


def test_les_30_factures_sont_extraites_sans_erreur():
    extraites = {(ligne["client"], ligne["fichier"]): ligne for ligne in lire_csv(FICHIER_MONTANTS)}
    assert len(extraites) == len(MANIFESTE) == 30
    for attendue in MANIFESTE:
        extraite = extraites[attendue["client"], attendue["fichier"]]
        for colonne in ("fournisseur", "numero", "date", "total_ht", "tva", "total_ttc"):
            assert extraite[colonne] == attendue[colonne]


def test_le_total_d_un_client_ne_compte_que_ses_factures():
    for client in CLIENTS:
        attendu = sum(Decimal(l["total_ttc"]) for l in MANIFESTE if l["client"] == client)
        calcule = sum(total["total_ttc"] for total in totaux_par_fournisseur(client))
        assert calcule == attendu


def test_un_fournisseur_d_un_autre_client_n_apparait_pas():
    fournisseurs = {total["fournisseur"] for total in totaux_par_fournisseur("atelier-rivoli")}
    assert "Moulins de la Vallée Verte SAS" not in fournisseurs  # fournisseur de la boulangerie
    assert "Cycles Pièces Distribution SARL" in fournisseurs
