from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    birth_place = Column(String)
    birth_country = Column(String)
    gr_link = Column(String, nullable=False)


# Define your SQLALCHEMY_DATABASE_URI (the same one used in alembic.ini)
SQLALCHEMY_DATABASE_URI = (
    "postgresql://myuser:mysecretpassword@localhost:5432/bookmap_db"
)
if __name__ == "__main__":
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)

    # Create the table in the database
    Base.metadata.create_all(engine)
