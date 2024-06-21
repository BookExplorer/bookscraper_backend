from neomodel import config, db
import os
from graph_models import Author, City, Country, Region
from typing import List, Dict

NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
config.DATABASE_URL = f"bolt://neo4j:{NEO4J_PASSWORD}@localhost:7687"


# TODO: This is not efficient, as every author created is a roundtrip to the DB...
@db.transaction
def insert_author(author: Dict):
    if "name" not in author or not author["name"]:
        raise ValueError(f"Missing name for this author dict: {author}")
    # TODO: Here, we don't get the author's relationship with city.
    author_node = Author.get_or_create(
        {"goodreads_id": author["goodreads_id"], "name": author["name"]},
        defaults=author,
    )
    return author_node


EXAMPLE = [
    {"name": "J.K. Rowling", "goodreads_id": "12345", "city_name": "Edinburgh"},
    {"name": "Neil Gaiman", "goodreads_id": "67890", "city_name": "Portsmouth"},
    {"name": "Agatha Christie", "goodreads_id": "54321", "city_name": "Torquay"},
]


for author in EXAMPLE:
    insert_author(author)
