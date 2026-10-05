"""Recherche : trouve les passages les plus proches d'une question."""
from app.base import calculer_vecteurs, collection
from app.config import COMMUN, DISTANCE_MAX, NB_PASSAGES


def chercher(question: str, client: str, n: int = NB_PASSAGES,
             distance_max: float = DISTANCE_MAX) -> list[dict]:
    """Renvoie les passages les plus proches de la question, pour ce client seulement.

    On fait deux recherches : dans les factures du client, puis dans les textes
    officiels communs à tous. Sans cette séparation, les textes officiels (qui
    répètent le mot « facture ») passent toujours devant les vraies factures.

    Cloisonnement : le filtre est donné à Chroma, qui l'applique AVANT de comparer
    les vecteurs. Les passages d'un autre client ne sont donc jamais candidats.
    """
    vecteur = calculer_vecteurs([question], "query")
    passages = []
    for proprietaire in (client, COMMUN):
        resultat = collection().query(query_embeddings=vecteur, n_results=n,
                                      where={"client": proprietaire})
        # Chroma renvoie une liste par question ; on n'en pose qu'une, d'où le [0].
        trouves = zip(resultat["documents"][0], resultat["metadatas"][0], resultat["distances"][0])
        passages += [{"texte": texte, "distance": round(distance, 3), **meta}
                     for texte, meta, distance in trouves]
    passages.sort(key=lambda passage: passage["distance"])

    # Contrôle de la pertinence : si même le meilleur passage est loin de la
    # question, on considère qu'on n'a rien trouvé.
    if not passages or passages[0]["distance"] > distance_max:
        return []
    return passages
