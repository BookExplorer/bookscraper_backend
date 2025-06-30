
from collections import Counter
from bookscraper_backend.database import db_models
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Session
import os
from typing import Sequence
from goodreads_scraper.scrape import process_goodreads_url, scrape_gr_author
from bookscraper_backend.backend import process_birthplace

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


def find_missing_authors(db_authors: Sequence[db_models.Author], scrapped_authors: Counter) -> list[tuple]:
    existing_ids = [author.goodreads_id for author in db_authors]
    missing_authors = [item for item in scrapped_authors.items() if item[0][0] not in existing_ids]
    return missing_authors


def insert_geo_dict(geo_dict: dict) -> None:
    if 'region' in geo_dict:
        pass
    pass



def generate_country_count(db_session: Session, books_per_author: Counter):
    # If all authors were in db, this is just queries.
    # IDEA: Get authors table in memory.
    # See everyone that is not there.
    # Scrape THOSE authors, then do the query with all joins.
    all_authors = fetch_all_authors(db_session)
    missing_authors = find_missing_authors(all_authors, books_per_author)
    for author in missing_authors:
        gr_id, gr_link, author_name = author[0]
        birthplace, _ = scrape_gr_author(gr_link)
        geo_dict = process_birthplace(birthplace)
        print(birthplace)
        # do something
    pass