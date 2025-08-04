from typing import Generator
import pytest
import os
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql.base import PGInspector
from sqlalchemy.orm import sessionmaker, Session
from testcontainers.postgres import PostgresContainer  # type: ignore
from alembic.config import Config
from alembic import command
from bookscraper_backend.database import db_models
from datetime import date

VALID_EXISTING_COUNTRIES_DATA = [
    {"name": "United States", "still_exists": True, "end_date": None},
    {"name": "France", "still_exists": True, "end_date": None},
    {"name": "Côte d'Ivoire", "still_exists": True, "end_date": None},
]

INVALID_EXISTING_COUNTRIES_DATA = [
    {"name": "United States", "still_exists": True, "end_date": date.today()},
    {"name": "France", "still_exists": True, "end_date": date.today()},
    {"name": "Côte d'Ivoire", "still_exists": True, "end_date": date.today()},
]

VALID_FORMER_COUNTRIES_DATA = [
    {"name": "Soviet Union", "still_exists": False, "end_date": date(1991, 12, 26)},
    {"name": "Yugoslavia", "still_exists": False, "end_date": date(1992, 4, 27)},
    {"name": "East Germany", "still_exists": False, "end_date": date(1990, 10, 3)},
]

INVALID_FORMER_COUNTRIES_DATA = [
    {"name": "Soviet Union", "still_exists": False, "end_date": None},
    {"name": "Yugoslavia", "still_exists": False, "end_date": None},
    {"name": "East Germany", "still_exists": False, "end_date": None},
]


@pytest.fixture(params=VALID_EXISTING_COUNTRIES_DATA)
def valid_existing_country(request: pytest.FixtureRequest) -> db_models.Country:
    return db_models.Country(**request.param)


@pytest.fixture(params=VALID_FORMER_COUNTRIES_DATA)
def valid_former_country(request: pytest.FixtureRequest) -> db_models.Country:
    return db_models.Country(**request.param)


@pytest.fixture(params=INVALID_EXISTING_COUNTRIES_DATA)
def invalid_existing_country(request: pytest.FixtureRequest) -> db_models.Country:
    return db_models.Country(**request.param)


@pytest.fixture(params=INVALID_FORMER_COUNTRIES_DATA)
def invalid_former_country(request: pytest.FixtureRequest) -> db_models.Country:
    return db_models.Country(**request.param)


@pytest.fixture(params=VALID_FORMER_COUNTRIES_DATA + VALID_EXISTING_COUNTRIES_DATA)
def valid_country(request: pytest.FixtureRequest):
    return db_models.Country(**request.param)


@pytest.fixture(scope="module", autouse=True)
def postgres_container(request: pytest.FixtureRequest) -> Generator[str, None, None]:
    with PostgresContainer(
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME"),
    ) as postgres:
        postgres.start()
        yield postgres.get_connection_url()


@pytest.fixture(scope="module")
def apply_migrations(postgres_container: str):
    """Applies Alembic migrations to the test DB."""
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", postgres_container)
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="module")
def engine(postgres_container: str, apply_migrations) -> sa.Engine:
    return sa.create_engine(postgres_container)


@pytest.fixture
def db_session(engine: sa.Engine) -> Generator[Session, None, None]:
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    cleanup_Session = sessionmaker(bind=engine)
    cleanup_sess = cleanup_Session()
    cleanup_tables(cleanup_sess)
    cleanup_sess.close()


def cleanup_tables(session: Session) -> None:
    inspector: PGInspector = sa.inspect(session.bind)  # type: ignore
    table_names = inspector.get_table_names()

    if table_names:
        tables_str = ", ".join(
            f'"{name}"' for name in table_names if name != "alembic_version"
        )
        session.execute(
            sa.text(f"TRUNCATE TABLE {tables_str} RESTART IDENTITY CASCADE;")
        )
        session.commit()


@pytest.fixture
def sample_data(db_session: Session) -> None:
    """Fixture to set up sample data for testing."""
    country = db_models.Country(name="Testland", still_exists=True)
    city = db_models.City(name="Testville", country=country)
    authors = [
        db_models.Author(
            name="Author One",
            goodreads_link="https://www.goodreads.com/author/show/1",
            birth_city=city,
            goodreads_id=1,
        ),
        db_models.Author(
            name="Author Two",
            goodreads_link="https://www.goodreads.com/author/show/2",
            birth_city=city,
            goodreads_id=2,
        ),
    ]

    db_session.add(country)
    db_session.add(city)
    db_session.add_all(authors)
    db_session.commit()
