import os
from neomodel import db, config
from urllib.parse import urlparse
from logger import logger



def setup_db(uri: str | None = None, password: str | None = None):
    """This sets up the DB connection globally for every Neo4J operation using the parameters.
    In contrast with other modules, you DON'T pass sessions/connections to the OGM.
    So in order to have operations run in a specific DB, this needs to run first.
    This is what allows us to use testcontainers on the side, for instance.

    Args:
        uri (str | None): URI for Neo4J.
        password (str | None): Password for Neo4j.
    """
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    neo4j_uri = os.getenv("NEO4J_URI")
    if not uri:
        uri = neo4j_uri
        logger.debug(f"No uri passed, so using env variable: {uri}")
    else:
        # The URI from Testcontainers comes like: bolt://neo4j@localhost:port
        # So to assemble it with password, we need to do this.
        uri = urlparse(uri).netloc
    if not password:
        logger.debug("Using env variable as password.")
        password = neo4j_password
    connection_string = f"bolt://neo4j:{password}@{uri}"
    logger.info(f"[Neo4j Setup] Setting up connection string to {uri}")
    db.set_connection(connection_string)
    logger.info("[Neo4j Setup] Connection done!")
    config.DATABASE_URL = connection_string # Neomodel needs to know the proper connection string internally.
    return db
