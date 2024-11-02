from fastapi.testclient import TestClient
from bookscraper_backend.backend_api import app
import os
client = TestClient(app)

#FIXME: The issue here is that if the app calls the DB url locally, it wont resolve because it references graph_db (its meant to run inside containers)


def test_profile_endpoint():
    os.environ["NEO4J_URI"] = "localhost:7687"
    with TestClient(app) as client:
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


def test_profile_endpoint_bad_url():
    os.environ["NEO4J_URI"] = "localhost:7687"
    # FIXME: The main problem here is having different settings for development and whatever
    
    with TestClient(app) as client:
        response = client.post(
            "/process-profile/",
            json={
                "profile_url": "sdfdsd"
            },
        )

    assert response.status_code == 422
