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
                "profile_url": "https://www.goodreads.com/user/show/66818479-lucas-pavanelli"
            },
        )

    assert response.status_code == 200


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
