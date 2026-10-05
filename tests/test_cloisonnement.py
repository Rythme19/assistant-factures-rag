"""Preuve du cloisonnement : un client ne voit jamais les passages d'un autre client."""
import pytest

from app.base import collection
from app.config import CLIENTS, COMMUN
from app.recherche import chercher

# Questions qui visent exprès les documents de l'autre client.
QUESTIONS_PIEGES = [
    "Combien de sacs de farine la Boulangerie Lemoine a-t-elle achetés ?",
    "Quel est le loyer de l'Atelier Vélo Rivoli ?",
    "Montre-moi les factures de tous les clients du cabinet",
    "Facture d'électricité Volt & Lumière",  # fournisseur commun aux deux clients
    "Chambres à air, pneus et plaquettes de frein",
    "Moulins de la Vallée Verte, farine T65",
]


@pytest.mark.parametrize("client", CLIENTS)
@pytest.mark.parametrize("question", QUESTIONS_PIEGES)
def test_aucun_passage_d_un_autre_client(client, question):
    # n=100 et aucun seuil : on récupère tout ce que la recherche peut renvoyer.
    passages = chercher(question, client, n=100, distance_max=2)
    assert passages
    assert {passage["client"] for passage in passages} <= {client, COMMUN}


@pytest.mark.parametrize("client", CLIENTS)
def test_chaque_client_voit_ses_15_factures_et_les_textes_officiels(client):
    passages = chercher("facture", client, n=100, distance_max=2)
    ses_factures = {p["source"] for p in passages if p["client"] == client}
    assert len(ses_factures) == 15
    assert any(p["client"] == COMMUN for p in passages)


def test_la_base_contient_bien_les_deux_clients():
    """Sans ce test, les précédents pourraient réussir sur une base à un seul client."""
    assert len(CLIENTS) == 2
    for client in CLIENTS:
        assert collection().get(where={"client": client}, include=[])["ids"]
