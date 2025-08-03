from typing import Generator, Callable, ContextManager, TypedDict
import pytest
import os
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql.base import PGInspector
from sqlalchemy.orm import sessionmaker, Session
from testcontainers.postgres import PostgresContainer
from alembic.config import Config
from alembic import command
from contextlib import contextmanager
import string
from hypothesis import strategies as st
from bookscraper_backend.database import db_models


type SessionFactory = Callable[[], ContextManager[Session]]
naming_strategy = st.text(alphabet=string.ascii_letters + " -", min_size=1)



@pytest.fixture(scope="module", autouse=True)
def postgres_container(request) -> Generator[str, None, None]:
    with PostgresContainer(
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME")
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
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@st.composite
def random_world(draw) -> list[db_models.Author]:
    "Strategy that creates a bunch of countries, regions, authors and cities to model a populated db."
    num_countries = draw(st.integers(min_value=10, max_value=20))
    num_authors = draw(st.integers(min_value=14, max_value=30))
    countries_names = draw(st.lists(naming_strategy, unique=True, min_size=num_countries, max_size=num_countries))
    authors_names = draw(st.lists(naming_strategy, unique=True, min_size=num_authors, max_size=num_authors))
    authors_ids = draw(st.lists(st.integers(min_value=30), unique=True, min_size=num_authors, max_size=num_authors))
    cities = []
    authors = []
    countries = []
    all_regions = []
    for country_name in countries_names:
        still_exists = draw(st.booleans())
        has_regions = draw(st.booleans())
        end_date = draw(st.dates()) if not still_exists else None
        country = db_models.Country(name=country_name, end_date=end_date, still_exists=still_exists)
        countries.append(country)
        if has_regions:
            num_regions = draw(st.integers(min_value=2, max_value=5))
            region_names = draw(st.lists(naming_strategy, unique=True, min_size=num_regions, max_size=num_regions))
            regions = [db_models.Region(name = region_name, country=country) for region_name in region_names]
            all_regions.extend(regions)
            for region in regions:
                num_cities = draw(st.integers(min_value=2, max_value=4))
                city_names = draw(st.lists(naming_strategy, unique=True, min_size=num_cities, max_size=num_cities))
                region_cities = [db_models.City(name=city_name, region=region) for city_name in city_names]
                cities.extend(region_cities)
        else:
            num_cities = draw(st.integers(min_value=1, max_value=4))
            city_names = draw(st.lists(naming_strategy, unique=True, min_size=num_cities, max_size=num_cities))
            country_cities =[db_models.City(name=city_name, country=country) for city_name in city_names] 
            cities.extend(country_cities)
    for author_name, author_id in zip(authors_names, authors_ids):
        author_city = draw(st.sampled_from(cities))
        goodreads_link = f"https://www.goodreads.com/author/show/{author_id}"
        authors.append(db_models.Author(name=author_name, goodreads_link=goodreads_link, birth_city=author_city, goodreads_id=author_id))
    return authors

@pytest.fixture
def sample_data(db_session_factory: SessionFactory) -> None:
    """Fixture to set up sample data for testing."""
    country = db_models.Country(
            name="Testland", 
            still_exists=True
        )
    city = db_models.City(
            name="Testville", 
            country=country
        )
    authors = [
            db_models.Author(
                name="Author One",
                goodreads_link="https://www.goodreads.com/author/show/1",
                birth_city=city,
                goodreads_id=1
            ),
            db_models.Author(
                name="Author Two",
                goodreads_link="https://www.goodreads.com/author/show/2",
                birth_city=city,
                goodreads_id=2
            )
        ]
    with db_session_factory() as session:
        session.add(country)
        session.add(city)
        session.add_all(authors)
        session.commit()
