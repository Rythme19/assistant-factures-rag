FROM python:3.12-slim

# PyTorch en version « processeur seul » : l'image reste petite (pas de bibliothèques GPU).
RUN pip install --no-cache-dir torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Le service tourne avec un utilisateur sans droits d'administration.
RUN useradd --create-home assistant && mkdir /projet && chown assistant /projet
USER assistant
WORKDIR /projet

# Le modèle de vecteurs est téléchargé pendant la construction, avant le code :
# modifier un fichier Python ne le retélécharge pas. Ensuite, plus besoin d'Internet
# pour la recherche. Le nom doit rester celui de MODELE_VECTEURS dans app/config.py
# (sinon l'ingestion ci-dessous échoue, faute de réseau autorisé).
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-small')"
ENV HF_HUB_OFFLINE=1

# Les documents sont ingérés pendant la construction : le conteneur démarre avec sa base prête.
COPY --chown=assistant app/ app/
COPY --chown=assistant data/ data/
RUN python -m app.ingestion

EXPOSE 8000
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
