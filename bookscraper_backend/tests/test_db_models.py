from hypothesis import given, assume, HealthCheck, settings, strategies as st
from typing import Generator, Callable, ContextManager
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
from contextlib import contextmanager

naming_strategy = st.text(alphabet=string.ascii_letters + " -", min_size=1)
SessionFactory = Callable[[], ContextManager[Session]]

settings.register_profile(
    "my_profile", suppress_health_check=[HealthCheck.function_scoped_fixture]
)
settings.load_profile("my_profile")

@pytest.fixture(scope="module", autouse=True)
def postgres_container(request) -> Generator[sa.Engine, None, None]:
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
        
        yield engine

@pytest.fixture
def db_session_factory(postgres_container):
    """Returns a context manager factory for creating isolated sessions."""
    SessionLocal = sessionmaker(bind=postgres_container)
    
    @contextmanager
    def create_session():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.rollback()
            session.expunge_all()
            session.close()
    
    return create_session

@pytest.fixture(scope="function", autouse=True)
def cleanup_tables(db_session_factory: SessionFactory):
    with db_session_factory() as session:
        inspector: PGInspector = sa.inspect(session.bind) #type: ignore
        table_names = inspector.get_table_names()
        
        if table_names:
            tables_str = ", ".join(f'"{name}"' for name in table_names if name != 'alembic_version')
            # Use testcontainer session for execution
            session.execute(
                sa.text(f'TRUNCATE TABLE {tables_str} RESTART IDENTITY CASCADE;')
            )
            session.commit()


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
def test_valid_existing_country(db_session_factory: SessionFactory, country: db_models.Country) -> None:
     with db_session_factory() as session:
        session.add(country)
        session.commit()
        assert country.id is not None


@given(valid_former_country())
def test_valid_former_country(db_session_factory: SessionFactory, country: db_models.Country) -> None:
    with db_session_factory() as session:
        session.add(country)
        session.commit()
        assert country.id is not None


@given(invalid_existing_country())
def test_invalid_existing_country(db_session_factory: SessionFactory, country: db_models.Country) -> None:
    with db_session_factory() as db_session:
        db_session.add(country)
        with pytest.raises(IntegrityError) as exc:
            db_session.commit()
        assert "chk_country_status" in str(exc.value)


@given(invalid_former_country())
def test_invalid_former_country(db_session_factory: SessionFactory, country: db_models.Country) -> None:
    with db_session_factory() as db_session:   
        db_session.add(country)
        with pytest.raises(IntegrityError) as exc:
            db_session.commit()
        assert "chk_country_status" in str(exc.value)


@given(name=naming_strategy)
def test_unique_active_country_name(db_session_factory: SessionFactory, name: str) -> None:
    with db_session_factory() as db_session:
        country_1 = db_models.Country(name=name, still_exists=True)
        db_session.add(country_1)
        db_session.commit()
        assert country_1.id is not None
        country_2 = db_models.Country(name=name, still_exists=True)
        db_session.add(country_2)
        with pytest.raises(IntegrityError) as exc:
            db_session.commit()
        assert "uq_active_country_name" in str(exc.value)



@given(name=naming_strategy)
def test_unique_former_country_name(db_session_factory: SessionFactory, name: str) -> None:
    with db_session_factory() as db_session:
        country_1 = db_models.Country(name=name, still_exists=False, end_date=date.today())
        db_session.add(country_1)
        db_session.commit()
        assert country_1.id is not None
        country_2 = db_models.Country(name=name, still_exists=False, end_date=date.today())
        db_session.add(country_2)
        with pytest.raises(IntegrityError) as exc:
            db_session.commit()
        assert "uq_inactive_country" in str(exc.value)



@given(name=naming_strategy)
def test_valid_region_creation(db_session_factory: SessionFactory, name: str) -> None:
    with db_session_factory() as db_session:
        country = db_models.Country(name=name, still_exists = True)
        db_session.add(country)
        db_session.commit()
        region = db_models.Region(name=name, country=country)
        db_session.add(region)
        db_session.commit()
        assert region.id is not None
        assert region.country.id == country.id



@given(name=naming_strategy)
def test_region_unique_constraint(db_session_factory: SessionFactory, name: str) -> None:
    with db_session_factory() as db_session:
        country = db_models.Country(name=name, still_exists = True)
        db_session.add(country)
        db_session.commit()
        region_1 = db_models.Region(name=name, country=country)
        db_session.add(region_1)
        db_session.commit()
        assert region_1.id is not None
        assert region_1.country.id == country.id
        region_2 = db_models.Region(name=name, country=country)
        db_session.add(region_2)
        with pytest.raises(IntegrityError) as exc:
            db_session.commit()
        assert "regions_country_id_name_key" in str(exc.value)

@given(name=naming_strategy)
def test_city_check_constraint_nothing(db_session_factory: SessionFactory, name: str) -> None:
    with db_session_factory() as db_session:
        country_name = f"country_{name}"
        region_name = f"region_{name}"
        city_name = f"city_{name}"
        country = db_models.Country(name=country_name, still_exists = True)
        db_session.add(country)
        db_session.commit()
        region = db_models.Region(name=region_name, country=country)
        db_session.add(region)
        db_session.commit()
        city_without_anything = db_models.City(name=city_name)
        db_session.add(city_without_anything)
        with pytest.raises(IntegrityError) as exc:
            db_session.commit()
        assert "cities_check" in str(exc.value)

@given(name=naming_strategy)
def test_city_check_constraint_both(db_session_factory: SessionFactory, name: str) -> None:
    with db_session_factory() as db_session:
        country_name = f"country_{name}"
        region_name = f"region_{name}"
        city_name = f"city_{name}"    
        country = db_models.Country(name=country_name, still_exists = True)
        region = db_models.Region(name=region_name, country=country)
        city_with_both = db_models.City(name=city_name, country=country, region=region)
        db_session.add(city_with_both)
        with pytest.raises(IntegrityError) as exc:
            db_session.commit()
        assert "cities_check" in str(exc.value)