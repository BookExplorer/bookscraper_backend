from fastapi.testclient import TestClient
from backend_api import app
from pytest import fixture
from alembic.config import Config
from alembic import command


client = TestClient(app)


@fixture(scope="session", autouse=True)
def apply_migrations():
    # Setup: Run migrations
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    yield

    # Teardown: Optionally, you can downgrade or drop tables
    command.downgrade(alembic_cfg, "base")


def test_profile_endpoint():
    response = client.post(
        "/process-profile/",
        json={
            "profile_url": "https://www.goodreads.com/user/show/6681479-lucas-pavanelli"
        },
    )

    assert response.status_code == 200
