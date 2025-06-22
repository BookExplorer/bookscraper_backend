from hypothesis import given, assume, strategies as st
import string
import pytest
from sqlalchemy.exc import IntegrityError
import os
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Session
from testcontainers.postgres import PostgresContainer
from bookscraper_backend.database import db_models
from bookscraper_backend.database.setup import db_session
from alembic.config import Config
from alembic import command

naming_strategy = st.text(alphabet=string.ascii_letters + " -", min_size=1)

@pytest.fixture(scope="module", autouse=True)
def postgres_container(request) -> Session:
    with PostgresContainer(
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME")
    ) as postgres:
        postgres.start()
        engine = sa.create_engine(postgres.get_connection_url())
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", postgres.get_connection_url()) # I think this is failing now?
        command.upgrade(alembic_cfg, "head")
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()

        yield session

        session.close()

@pytest.fixture(scope="function", autouse=True)
def cleanup_tables(postgres_container: Session):
    postgres_container.rollback()
    
    # Reflect and get all table names
    inspector = sa.inspect(postgres_container.bind)
    table_names = inspector.get_table_names()
    
    if table_names:
        # Format: "table1", "table2", ...
        tables_str = ", ".join(f'"{name}"' for name in table_names)
        postgres_container.execute(
            sa.text(f'TRUNCATE TABLE {tables_str} RESTART IDENTITY CASCADE;')
        )
        postgres_container.commit()

@st.composite
def valid_existing_country(draw):
    name = draw(naming_strategy)
    return db_models.Country(name=name, still_exists=True, end_date = None)

@st.composite
def invalid_existing_country(draw):
    name = draw(naming_strategy)
    return db_models.Country(name=name, still_exists=True, end_date = draw(st.dates()))

@st.composite
def valid_former_country(draw):
    name = draw(naming_strategy)
    return db_models.Country(name=name, still_exists=False, end_date = draw(st.dates()))

@st.composite
def invalid_former_country(draw):
    name = draw(naming_strategy)
    return db_models.Country(name=name, still_exists=False, end_date = None)

@given(valid_existing_country())
def test_valid_country(country: db_models.Country) -> None:
    db_session.add(country)
    db_session.commit()
    assert country.id is not None
