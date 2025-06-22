from hypothesis import given, assume, strategies as st
from typing import Generator
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
from datetime import date

naming_strategy = st.text(alphabet=string.ascii_letters + " -", min_size=1)

@pytest.fixture(scope="module", autouse=True)
def postgres_container(request) -> Generator[Session, None, None]:
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
def test_valid_existing_country(postgres_container: Session, country: db_models.Country) -> None:
    postgres_container.add(country)
    postgres_container.commit()
    assert country.id is not None


@given(valid_former_country())
def test_valid_former_country(postgres_container: Session, country: db_models.Country) -> None:
    postgres_container.add(country)
    postgres_container.commit()
    assert country.id is not None


@given(invalid_existing_country())
def test_invalid_existing_country(postgres_container: Session, country: db_models.Country) -> None:
    postgres_container.add(country)
    with pytest.raises(IntegrityError) as exc:
        postgres_container.commit()
    postgres_container.rollback()
    assert "chk_country_status" in str(exc.value)


@given(invalid_former_country())
def test_invalid_former_country(postgres_container: Session, country: db_models.Country) -> None:
    postgres_container.add(country)
    with pytest.raises(IntegrityError) as exc:
        postgres_container.commit()
    postgres_container.rollback()
    assert "chk_country_status" in str(exc.value)


@pytest.mark.parametrize("name", ["A", "B", "Long Country Name"])
def test_unique_active_country_name(postgres_container: Session, name) -> None:
    country_1 = db_models.Country(name=name, still_exists=True)
    postgres_container.add(country_1)
    postgres_container.commit()
    assert country_1.id is not None
    country_2 = db_models.Country(name=name, still_exists=True)
    postgres_container.add(country_2)
    with pytest.raises(IntegrityError) as exc:
        postgres_container.commit()
    assert "uq_active_country_name" in str(exc.value)
    postgres_container.rollback()
    postgres_container.expire_all()



@pytest.mark.parametrize("name", ["A", "B", "Long Country Name"])
def test_unique_former_country_name(postgres_container: Session, name) -> None:
    country_1 = db_models.Country(name=name, still_exists=False, end_date=date.today())
    postgres_container.add(country_1)
    postgres_container.commit()
    assert country_1.id is not None
    country_2 = db_models.Country(name=name, still_exists=False, end_date=date.today())
    postgres_container.add(country_2)
    with pytest.raises(IntegrityError) as exc:
        postgres_container.commit()
    assert "uq_inactive_country" in str(exc.value)
    postgres_container.rollback()
    postgres_container.expire_all()