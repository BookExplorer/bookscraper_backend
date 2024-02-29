from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from models import Author
from typing import Dict

DATABASE_URI = "postgresql://myuser:mysecretpassword@localhost/bookmap_db"

engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)


def fetch_author_by_id(session: Session, id: int):
    return session.query(Author).filter(Author.id == id).first()


def insert_author(session: Session, author_data: Dict) -> Author:
    author = Author(**author_data)
    session.add(author)
    session.commit()
    return author
