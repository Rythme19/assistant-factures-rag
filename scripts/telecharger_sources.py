"""Télécharge les textes officiels publics et note leur source et leur date.

Usage : python scripts/telecharger_sources.py
"""
import hashlib
import urllib.request
from datetime import date
from pathlib import Path

DOSSIER = Path(__file__).parent.parent / "data" / "officiel"
BASE = ("https://www.impots.gouv.fr/sites/default/files/media/1_metier/"
        "2_professionnel/EV/2_gestion/290_facturation_electronique/")

# nom du fichier local -> adresse d'origine
SOURCES = {
    "faq_facturation_electronique.pdf": BASE + "faq---fe_je-decouvre-la-facturation-electronique.pdf",
    "guide_pratique_facturation_electronique.pdf": BASE + "guide_pratique_facturation_electronique.pdf",
}

# Source demandée mais non téléchargeable par script (voir SOURCES.md).
PAGE_BLOQUEE = ("https://www.economie.gouv.fr/entreprises/gerer-son-entreprise-au-quotidien/"
                "gerer-sa-comptabilite-et-ses-demarches/mentions-obligatoires-dune-facture-tout-savoir")


def telecharger(url: str) -> bytes:
    """Renvoie le contenu du fichier. Lève une erreur si le serveur refuse."""
    requete = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(requete, timeout=60) as reponse:
        return reponse.read()


def main() -> None:
    DOSSIER.mkdir(parents=True, exist_ok=True)
    lignes = [
        "# Sources des textes officiels",
        "",
        f"Téléchargés le {date.today().isoformat()} depuis impots.gouv.fr (DGFiP).",
        "Licence : licence ouverte Etalab 2.0, d'après https://www.impots.gouv.fr/mentions-legales",
        "(réutilisation libre à condition de citer la source et la date).",
        "",
        "| Fichier | Adresse d'origine | Taille | SHA-256 |",
        "|---|---|---|---|",
    ]
    for nom, url in SOURCES.items():
        contenu = telecharger(url)
        # On refuse d'enregistrer autre chose qu'un PDF (page d'erreur, etc.).
        if not contenu.startswith(b"%PDF"):
            raise SystemExit(f"{nom} : le serveur n'a pas renvoyé un PDF")
        (DOSSIER / nom).write_bytes(contenu)
        empreinte = hashlib.sha256(contenu).hexdigest()
        lignes.append(f"| {nom} | {url} | {len(contenu) // 1024} Ko | `{empreinte}` |")
        print(f"OK  {nom} ({len(contenu) // 1024} Ko)")

    lignes += [
        "",
        "## Source non téléchargée",
        "",
        f"- {PAGE_BLOQUEE}",
        "",
        "Le site economie.gouv.fr répond 403 (protection anti-robot) aux téléchargements",
        "automatiques. Ses conditions de réutilisation n'ont donc pas pu être vérifiées.",
        "Pour l'ajouter : ouvrir la page dans un navigateur, l'enregistrer en PDF dans ce",
        "dossier, noter ici la date, puis relancer `python -m app.ingestion`.",
    ]
    (DOSSIER / "SOURCES.md").write_text("\n".join(lignes) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
