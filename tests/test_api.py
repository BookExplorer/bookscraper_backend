from fastapi.testclient import TestClient
from bookscraper_backend.backend_api import app
import os
import pytest


#FIXME: The issue here is that if the app calls the DB url locally, it wont resolve because it references graph_db (its meant to run inside containers)

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_profile_endpoint(client):
    os.environ["NEO4J_URI"] = "localhost:7687"
    response = client.post(
            "/process-profile/",
            json={
                "profile_url": "https://www.goodreads.com/user/show/183326807"
            },
        )

    assert response.status_code == 200
    # In this profile, we have just 2 books, one from Orwell (India) and Twain (USA)
    # For stupid reasons, the USA from Goodreads fails. So we expect india = 1, rest 0.
    data =  response.json()["data"]
    assert data["India"] == 1
    assert all(data[country] == 0 for country in data if country != "India")


def test_profile_endpoint_bad_url(client):
    os.environ["NEO4J_URI"] = "localhost:7687"
    response = client.post(
            "/process-profile/",
            json={
                "profile_url": "sdfdsd"
            },
        )

    assert response.status_code == 422
