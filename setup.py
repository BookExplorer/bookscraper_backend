import os
from neomodel import db
from urllib.parse import urlparse

NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_URI = os.getenv("NEO4J_URI")


def setup_db(uri: str | None, password: str | None):
    if not uri:
        uri = NEO4J_URI
    else:
        uri = urlparse(uri).netloc
    if not password:
        password = NEO4J_PASSWORD
    connection_string = f"bolt://neo4j:{password}@{uri}"
    print(f"Setting up con string {connection_string}")
    db.set_connection(connection_string)
    print(f"Con done")
