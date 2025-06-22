from hypothesis import given, assume, strategies as st
import string
import pytest
from sqlalchemy.exc import IntegrityError
import os
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql.base import PGInspector
from sqlalchemy.orm import sessionmaker, Session
from testcontainers.postgres import PostgresContainer
from bookscraper_backend.database import db_models
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
        alembic_cfg.set_main_option("sqlalchemy.url", postgres.get_connection_url()) 
        command.upgrade(alembic_cfg, "head")
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()

        yield session

        session.close()

@pytest.fixture(scope="function", autouse=True)
def cleanup_tables(postgres_container: Session):
    postgres_container.rollback()
    inspector: PGInspector = sa.inspect(postgres_container.bind) #type: ignore
    table_names = inspector.get_table_names()
    
    if table_names:
        tables_str = ", ".join(f'"{name}"' for name in table_names if name != 'alembic_version')
        # Use testcontainer session for execution
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
def test_valid_country(postgres_container: Session, country: db_models.Country) -> None:
    postgres_container.add(country)
    postgres_container.commit()
    assert country.id is not None
