from collections import Counter
from bookscraper_backend.database import db_models
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Session
import os
from typing import Sequence
# First, setup basic connections for session making and the like.
USERNAME=os.getenv("DB_USER")
PASSWORD=os.getenv("DB_PASSWORD")
DBNAME=os.getenv("DB_NAME")

DB_URL = sa.URL.create(
    "postgresql",
    username=USERNAME,
    password=PASSWORD,  
    host="localhost",
    database=DBNAME,
)
ENGINE = sa.create_engine(DB_URL)

def fetch_all_authors(db_session: Session) -> Sequence[db_models.Author]:
    results = db_session.execute(sa.select(db_models.Author)).scalars().all()
    return results



def generate_country_count(books_per_author: Counter):
    # If all authors were in db, this is just queries.
    # IDEA: Get authors table in memory.
    # See everyone that is not there.
    # Scrape THOSE authors, then do the query with all joins.
    all_authors_query = sa.select(db_models.Author)
    with Session(bind=ENGINE) as db_session:
        all_authors = db_session.execute(all_authors_query).scalars().all()
    
    pass