from fastapi.testclient import TestClient
from bookscraper_backend.backend_api import app

client = TestClient(app)


def test_profile_endpoint():
    response = client.post(
        "/process-profile/",
        json={
            "profile_url": "https://www.goodreads.com/user/show/66818479-lucas-pavanelli"
        },
    )

    assert response.status_code == 200


def test_profile_endpoint_bad_url():
    response = client.post(
        "/process-profile/",
        json={
            "profile_url": "sdfdsd"
        },
    )

    assert response.status_code == 422
