"""Interface : une page Streamlit qui interroge l'API et affiche la réponse et ses sources.

Usage : streamlit run app/interface.py
"""
import os

import requests
import streamlit as st

URL_API = os.environ.get("URL_API", "http://localhost:8000")

st.title("Assistant factures")
st.caption("Réponses fondées sur les factures du client et sur les textes officiels, sources citées.")

try:
    etat = requests.get(f"{URL_API}/health", timeout=5).json()
except requests.RequestException:
    st.error(f"L'API ne répond pas à l'adresse {URL_API}.")
    st.stop()

client = st.selectbox("Société cliente", etat["clients"])

with st.expander("Totaux par fournisseur (calcul exact, sans modèle de langage)"):
    st.dataframe(requests.get(f"{URL_API}/totaux", params={"client": client}, timeout=5).json())

with st.form("question"):
    question = st.text_input("Votre question")
    envoyee = st.form_submit_button("Poser la question")

if envoyee and question:
    with st.spinner("Recherche en cours..."):
        reponse = requests.post(f"{URL_API}/ask", timeout=120,
                                json={"question": question, "client": client})
    if reponse.status_code != 200:
        st.error(f"Erreur {reponse.status_code} : {reponse.text}")
        st.stop()

    corps = reponse.json()
    st.subheader("Réponse")
    st.write(corps["reponse"])

    st.subheader(f"Passages cités ({len(corps['sources'])})")
    for source in corps["sources"]:
        titre = (f"{source['source']}, page {source['page']} "
                 f"({source['type_document']}, distance {source['distance']})")
        with st.expander(titre):
            st.text(source["texte"])
