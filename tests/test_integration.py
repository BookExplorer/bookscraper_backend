from testcontainers.neo4j import Neo4jContainer
import pytest
import os
from backend import extract_authors, generate_country_count, process_birthplace
from goodreads_scraper.scrape import scrape_shelf, create_shelf_url
from setup import setup_db
from neomodel import db


@pytest.fixture(scope="module", autouse=True)
def neo4j_container():
    with Neo4jContainer(
        image="neo4j:5.20.0", password="password", username="neo4j"
    ) as n4:
        # Map to different local ports to avoid conflicts
        n4.with_bind_ports(
            7687, 7688
        )  # Map container's Bolt port 7687 to local port 7688
        n4.with_bind_ports(7474, 7475)
        neo4j_uri = n4.get_connection_url()
        neo4j_password = n4.password
        n4.start()
        setup_db(neo4j_uri, neo4j_password)
        yield n4


def test_real_small_shelf():
    books = scrape_shelf(
        "https://www.goodreads.com/review/list/71341746-tamir-einhorn-salem?ref=nav_mybooks&shelf=comprar-em-outra-lingua"
    )
    authors = extract_authors(books)
    country_count = generate_country_count(authors)
    assert len(books) >= sum(
        country_count.values()
    ), "Country counts are larger than the number of books."
