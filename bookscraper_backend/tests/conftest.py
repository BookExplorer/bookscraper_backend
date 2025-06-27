from typing import Generator, Callable, ContextManager
import pytest
import os
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql.base import PGInspector
from sqlalchemy.orm import sessionmaker, Session
from testcontainers.postgres import PostgresContainer
from alembic.config import Config
from alembic import command
from contextlib import contextmanager


SessionFactory = Callable[[], ContextManager[Session]]


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
        except:
            session.expunge_all()
            session.rollback()
        finally:
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
