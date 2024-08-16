from fastapi.testclient import TestClient
from backend_api import app

client = TestClient(app)


def test_profile_endpoint():
    response = client.post(
        "/process-profile/",
        json={
            "profile_url": "https://www.goodreads.com/user/show/6681479-lucas-pavanelli"
        },
    )

    assert response.status_code == 200
