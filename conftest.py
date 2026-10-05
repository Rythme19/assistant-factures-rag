"""Préparation commune à tous les tests (fichier lu automatiquement par pytest)."""
import pytest

from app import ingestion
from app.base import collection
from app.config import FICHIER_MONTANTS


@pytest.fixture(scope="session", autouse=True)
def base_remplie():
    """Les tests interrogent la vraie base : on la construit si elle manque."""
    if collection().count() == 0 or not FICHIER_MONTANTS.exists():
        ingestion.main()
