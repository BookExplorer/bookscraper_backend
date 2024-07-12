import os
from neomodel import db
from urllib.parse import urlparse
import logging

NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_URI = os.getenv("NEO4J_URI")


def setup_db(uri: str | None, password: str | None):
    """This sets up the DB connection globally for every Neo4J operation using the parameters.
    In contrast with other modules, you DON'T pass sessions/connections to the OGM.
    So in order to have operations run in a specific DB, this needs to run first.
    This is what allows us to use testcontainers on the side, for instance.

    Args:
        uri (str | None): URI for Neo4J.
        password (str | None): Password for Neo4j.
    """
    if not uri:
        uri = NEO4J_URI
    else:
        # The URI from Testcontainers comes like: bolt://neo4j@localhost:port
        # So to assemble it with password, we need to do this.
        uri = urlparse(uri).netloc
    if not password:
        password = NEO4J_PASSWORD
    connection_string = f"bolt://neo4j:{password}@{uri}"
    logging.info(f"[Neo4j Setup] Setting up connection string to {uri}")
    db.set_connection(connection_string)
    logging.info(f"[Neo4j Setup] Connection done!")
