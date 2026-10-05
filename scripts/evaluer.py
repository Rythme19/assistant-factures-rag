"""Contrôle de la pertinence : mesure si la recherche trouve le bon document.

Pour chaque question de eval/questions.json :
- question normale : le document attendu doit figurer parmi les passages retenus ;
- question hors sujet : aucun passage ne doit être retenu (l'assistant dit qu'il ne sait pas).

Usage : python -m scripts.evaluer
"""
import json
from pathlib import Path

from app.recherche import chercher

QUESTIONS = Path(__file__).parent.parent / "eval" / "questions.json"


def rang_du_bon_passage(passages: list[dict], cas: dict) -> int | None:
    """Renvoie la position (1 = premier) du premier passage attendu, ou None."""
    for rang, passage in enumerate(passages, start=1):
        bonne_page = "pages" not in cas or passage["page"] in cas["pages"]
        if passage["source"] in cas["attendus"] and bonne_page:
            return rang
    return None


def main() -> None:
    tous = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    normales = [cas for cas in tous if cas["attendus"]]
    hors_sujet = [cas for cas in tous if not cas["attendus"]]

    trouvees = 0
    for cas in normales:
        passages = chercher(cas["question"], cas["client"])
        rang = rang_du_bon_passage(passages, cas)
        trouvees += rang is not None
        resultat = f"rang {rang}" if rang else "ABSENT"
        print(f"{resultat:8s} | {cas['question']}")

    refusees = 0
    for cas in hors_sujet:
        passages = chercher(cas["question"], cas["client"])
        refusees += not passages
        resultat = "refusée" if not passages else f"{len(passages)} passages"
        print(f"{resultat:8s} | {cas['question']}")

    print(f"\nBon document trouvé : {trouvees}/{len(normales)}")
    print(f"Questions hors sujet refusées sans appeler le modèle : {refusees}/{len(hors_sujet)}")


if __name__ == "__main__":
    main()
