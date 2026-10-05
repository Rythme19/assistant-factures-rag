"""Tests du découpage en passages."""
from app.ingestion import decouper


def test_un_texte_court_donne_un_seul_passage():
    assert decouper("Facture n° 1", taille=100, recouvrement=20) == ["Facture n° 1"]


def test_un_texte_long_est_decoupe_sans_rien_perdre():
    mots = [f"mot{i}" for i in range(300)]
    passages = decouper(" ".join(mots), taille=200, recouvrement=40)

    assert len(passages) > 1
    assert all(len(passage) <= 200 for passage in passages)
    # Aucun mot n'est perdu ni coupé en deux.
    assert set(mots) <= set(" ".join(passages).split())
    # Deux passages voisins se recouvrent : le suivant reprend la fin du précédent.
    assert passages[0].split()[-1] in passages[1].split()
