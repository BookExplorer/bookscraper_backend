from testcontainers.neo4j import Neo4jContainer
import pytest
import os


@pytest.fixture(scope="module", autouse=True)
def neo4j_container():
    with Neo4jContainer(
        image="neo4j:5.20.0", password="password", username="neo4j"
    ) as n4:
        neo4j_uri = n4.get_connection_url()
        neo4j_password = n4.password
        os.environ["NEO4J_URI"] = neo4j_uri
        os.environ["NEO4J_PASSWORD"] = neo4j_password
        yield n4


def test_whatever():
    assert True is True
