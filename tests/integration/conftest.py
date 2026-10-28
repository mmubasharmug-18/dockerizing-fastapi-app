import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import store


@pytest.fixture(autouse=True)
def empty_store():
    store.clear()
    yield
    store.clear()


@pytest.fixture
def client():
    return TestClient(app)
