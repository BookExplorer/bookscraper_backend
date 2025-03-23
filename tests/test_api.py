from fastapi.testclient import TestClient
from bookscraper_backend.backend_api import app
from dotenv import load_dotenv
import pytest


@pytest.fixture(scope="module", autouse=True)
def client():
    # Testing happens (now) locally. So .env.test points to localhost. However, since env vars are used when the app is setup
    # and they are needed to connect the app to the db...
    # We need to undo the .env.test, hence what we do here.
    load_dotenv(".env.test", override=True)
    with TestClient(app) as test_client:
        yield test_client
    load_dotenv(".env", override=True)

def test_profile_endpoint(client: TestClient) -> None:
    response = client.post(
            "/process-profile/",
            json={
                "profile_url": "https://www.goodreads.com/user/show/183326807"
            },
        )

    assert response.status_code == 200

def test_profile_endpoint_bad_url(client: TestClient) -> None:
    response = client.post(
            "/process-profile/",
            json={
                "profile_url": "sdfdsd"
            },
        )

    assert response.status_code == 422
