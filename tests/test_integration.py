from testcontainers.neo4j import Neo4jContainer
import pytest
from backend import extract_authors, generate_country_count
from goodreads_scraper.scrape import scrape_shelf
from graph_db import (
    create_geo_nodes,
    region_country_exists,
    city_region_exists,
    create_constraints,
    city_country_exists
)
from setup import setup_db



@pytest.fixture(scope="module", autouse=True)
def neo4j_container():
    with Neo4jContainer(
        image="neo4j:5.20.0", password="password", username="neo4j"
    ) as n4:
        # Map to different local ports to avoid conflicts with container.
        n4.with_bind_ports(
            7687, 7688
        )  # Map container's Bolt port 7687 to local port 7688
        n4.with_bind_ports(7474, 7475)
        neo4j_uri = n4.get_connection_url()
        neo4j_password = n4.password
        n4.start()
        # This maps out, temporarily, the DB connection to the test container.
        setup_db(neo4j_uri, neo4j_password)
        create_constraints()
        yield n4



# TODO: Add cleanup fixture and something just for good measure checking the db we connect to starts empty here, if not it's not the testcontainer


def test_real_small_shelf():
    # Keep in mind this very small shelf might not have repeated geo nodes and is thus not an extensive test.
    books = scrape_shelf(
        "https://www.goodreads.com/review/list/71341746-tamir-einhorn-salem?ref=nav_mybooks&shelf=comprar-em-outra-lingua"
    )
    authors = extract_authors(books)
    country_count = generate_country_count(authors)
    assert len(books) >= sum(
        country_count.values()
    ), "Country counts are larger than the number of books."


# TODO: Tests need to be created for all operations in Graph DB as well.
# TODO: Maybe we should use pytest coverage to see which functions aren't even tested?
def test_repeated_cr():
    country = "Brazil"
    city = "Rio de Janeiro"
    region = "Rio de Janeiro"
    geo_dict = {"country": country, "region": region, "city": city}
    assert city_region_exists(city, region) is False
    assert region_country_exists(region, country) is False
    create_geo_nodes(geo_dict)
    assert city_region_exists(city, region) is True
    assert region_country_exists(region, country) is True
    # How do I verify, here, that there is no duplicate creation?


def test_city_region_creation() -> None:
    country = "Brazil"
    city = "Rio de Janeiro"
    region = "Rio de Janeiro"
    geo_dict = {"country": country, "region": region, "city": city}
    # First, we make sure the region doesnt exist within the country
    assert not region_country_exists(region, country), "This region doesn't previously exist within the country"
    # We also want to make sure the city within region is not an existing pair
    assert not city_region_exists(city, region), "This city doesn't previously exist within the region"
    # Next, we create everything
    _, _, created_city, created_region = create_geo_nodes(geo_dict)
    assert region_country_exists(region, country), "Now the region exists within country"
    assert city_region_exists(city, region), "Now the city exists within the region"
    assert created_city
    assert created_region
    _, _, created_city, created_region = create_geo_nodes(geo_dict)
    assert not created_city, "We didn't need to create the city within the region because it already exists."
    assert not created_region, "We didn't need to create the region within the country because it already exists."



def test_city_country_creation() -> None:
    country = "Israel"
    city = "Tel Aviv"
    geo_dict = {"country": country, "city": city}
    # First, we make sure the region doesnt exist within the country
    # We also want to make sure the city within region is not an existing pair
    assert not city_country_exists(city, country), "This city doesn't previously exist within the country"
    # Next, we create everything
    _, _, created_city, _ = create_geo_nodes(geo_dict)
    assert city_country_exists(city, country), "Now the city exists within the country"
    assert created_city
    _, _, created_city, _ = create_geo_nodes(geo_dict)
    assert not created_city, "We didn't need to create the city within the country because it already exists."