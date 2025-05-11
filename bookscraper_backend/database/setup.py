import os
from sqlalchemy import (
    create_engine,
    URL
)
from sqlalchemy.orm import (
    sessionmaker
)
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_PORT = os.getenv("DB_PORT", 5432)
db_url = URL.create(
    "postgresql",
    username=DB_USER,
    password=DB_PASSWORD,
    port=DB_PORT,
    host="localhost",
    database="db",
)
engine = create_engine(
    db_url
)
Session = sessionmaker(bind=engine)
db_session = Session()
