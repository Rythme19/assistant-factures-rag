"""Tests du service REST. Le modèle de langage est remplacé par un faux : aucun appel payant."""
from fastapi.testclient import TestClient

from app import llm
from app.api import app

navigateur = TestClient(app)


def test_health():
    reponse = navigateur.get("/health")
    assert reponse.status_code == 200
    assert reponse.json()["statut"] == "ok"
    assert reponse.json()["passages"] > 0


def test_client_inconnu_refuse():
    demande = {"question": "Quel est le loyer ?", "client": "societe-inconnue"}
    assert navigateur.post("/ask", json=demande).status_code == 404


def test_totaux_par_fournisseur():
    totaux = navigateur.get("/totaux", params={"client": "atelier-rivoli"}).json()
    loyer = next(total for total in totaux if total["fournisseur"] == "SCI du Passage")
    assert loyer["factures"] == 3
    # Trois loyers de 1 818,00 € TTC. Le montant sort en texte exact, pas en nombre flottant.
    assert loyer["total_ttc"] == "5454.00"
    assert navigateur.get("/totaux", params={"client": "societe-inconnue"}).status_code == 404


def test_question_vide_refusee():
    demande = {"question": "", "client": "atelier-rivoli"}
    assert navigateur.post("/ask", json=demande).status_code == 422


def test_reponse_avec_ses_sources(monkeypatch):
    monkeypatch.setattr(llm, "generer", lambda question, passages: "réponse du faux modèle")
    demande = {"question": "Quel est le loyer mensuel de l'atelier ?", "client": "atelier-rivoli"}
    corps = navigateur.post("/ask", json=demande).json()
    assert corps["reponse"] == "réponse du faux modèle"
    assert corps["sources"][0]["source"].endswith(".pdf")
    assert corps["sources"][0]["page"] >= 1
    assert {source["client"] for source in corps["sources"]} <= {"atelier-rivoli", "commun"}


def test_hors_sujet_sans_appeler_le_modele(monkeypatch):
    def appel_interdit(question, passages):
        raise AssertionError("le modèle ne doit pas être appelé pour une question hors sujet")

    monkeypatch.setattr(llm, "generer", appel_interdit)
    demande = {"question": "Qui a gagné la coupe du monde de football en 2018 ?", "client": "atelier-rivoli"}
    corps = navigateur.post("/ask", json=demande).json()
    assert corps == {"reponse": llm.JE_NE_SAIS_PAS, "sources": []}


def test_sans_cle_on_renvoie_quand_meme_les_sources(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    demande = {"question": "Quel est le prix de l'abonnement fibre ?", "client": "atelier-rivoli"}
    corps = navigateur.post("/ask", json=demande).json()
    assert "aucune clé" in corps["reponse"]
    assert corps["sources"]
