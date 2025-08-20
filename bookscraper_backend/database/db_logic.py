
from collections import Counter
from bookscraper_backend.database import db_models
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
import os
from typing import Sequence,TypedDict
from goodreads_scraper.scrape import scrape_gr_author
from bookscraper_backend.backend import process_birthplace, GeoDict

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

class AuthorDict(TypedDict):
    name: str
    goodreads_id: int  | None
    goodreads_link: str  | None


def fetch_all_authors(db_session: Session) -> Sequence[db_models.Author]:
    results = db_session.execute(sa.select(db_models.Author)).scalars().all()
    return results


def find_missing_authors(db_authors: Sequence[db_models.Author], scrapped_authors: Counter) -> list[AuthorDict]:
    existing_ids = [author.goodreads_id for author in db_authors]
    missing_authors = [AuthorDict(goodreads_id=item[0][0],goodreads_link=item[0][1], name=item[0][2]) for item in scrapped_authors.items() if item[0][0] not in existing_ids]
    return missing_authors


def insert_geo_dict(db_session: Session, geo_dict: GeoDict) -> db_models.City:
    # vc precisa da cidade pra ligar ao resto, entao vc precisa inserir y ahi selectionar
    country_name = geo_dict["country"]
    stmt = insert(db_models.Country).values({'name': country_name}).on_conflict_do_nothing()
    db_session.execute(stmt)
    country = db_session.execute(sa.select(db_models.Country).where(db_models.Country.name == country_name)).scalars().one()
    city_name = geo_dict['city']
    city = db_models.City(name = city_name)
    region = None
    region_name = geo_dict["region"]
    if region_name:
        db_session.execute(insert(db_models.Region).values({'name':region_name, 'country_id': country.id}))
        region = db_session.execute(sa.select(db_models.Region).where(db_models.Region.name == region_name)).scalars().one()
    if region:
       city.region = region
    else:
        city.country = country
    db_session.add(city)
    db_session.commit()
    return city
    



def generate_country_count(db_session: Session, books_per_author: Counter):
    # If all authors were in db, this is just queries.
    # IDEA: Get authors table in memory.
    # See everyone that is not there.
    # Scrape THOSE authors, then do the query with all joins.
    all_authors = fetch_all_authors(db_session)
    missing_authors = find_missing_authors(all_authors, books_per_author)
    for author in missing_authors:
        insert_missing_author(db_session, author)
    pass


def insert_missing_author(db_session: Session, author: AuthorDict) -> None:
    birthplace, _ = scrape_gr_author(author["goodreads_link"])
    geo_dict = process_birthplace(birthplace)
    author_object = db_models.Author(**author)
    if geo_dict:
        city = insert_geo_dict(db_session, geo_dict)
        author_object.birth_city = city
    db_session.add(author_object)
    db_session.commit()