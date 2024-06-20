from sqlalchemy import create_engine, Row
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from models import Author
from typing import Dict, List
import os

DATABASE_URI = os.getenv(
    "DATABASE_URL", "postgresql://myuser:mysecretpassword@localhost/bookmap_db"
)


engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(
    bind=engine,
)


def fetch_author_by_id(session: Session, id: int) -> Author:
    """Fetches author from authors table by their GR id.

    Args:
        session (Session): Database session.
        id (int): Id of the author.

    Returns:
        Author: An instance of the author class.
    """
    return session.query(Author).filter(Author.id == id).first()


def fetch_authors_by_id(session: Session, ids: List[int]) -> Row:
    return session.query(Author).filter(Author.id.in_(ids)).all()


def insert_author(session: Session, author_data: Dict) -> Author:
    """Inserts a new author to the DB. Their info will be unpacked from the provided author_data dictionary.
    Thus, if the object comes in and has mismatching attributes to the class, this will fail.

    Args:
        session (Session): Database session.
        author_data (Dict): Dictionary with the relevant fields.

    Returns:
        Author: The new instance of the author class.
    """
    author = Author(**author_data)
    session.add(author)
    session.commit()
    return author


def insert_authors(session: Session, authors_data):
    """Insert multiple authors into the database."""
    session.bulk_insert_mappings(Author, authors_data)
    session.commit()
