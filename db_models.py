from typing import Optional
from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    create_engine,
    URL,
    UniqueConstraint,
    CheckConstraint,
    Index,
    text
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    sessionmaker,
    mapped_column,
    relationship,
)
import os
import datetime

DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_PORT = os.getenv("DB_PORT", 5432)
db_url = URL.create(
    "postgresql",
    username=DB_USER,
    password=DB_PASSWORD,
    port=5432,
    host="localhost",
    database="db",
)
engine = create_engine(
    db_url
)  # TODO, move this elsewhere, we will likely have to reuse this

Session = sessionmaker(bind=engine)
session = Session()


class Base(DeclarativeBase):
    pass


# TODO: Test out constraints and classes.


class BaseModel(Base):
    __abstract__ = True  # This allows it to be inherited by other classes.
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)

    def __repr__(self):
        return f"Class: {type(self).__name__} Id: {self.id}, name: {self.name}"


class Country(BaseModel):
    __tablename__ = "countries"
    regions: Mapped[list["Region"]] = relationship(
        back_populates="country"
    )  # Writes to Region.country
    still_exists: Mapped[Optional[bool]] = mapped_column(default=True)
    end_date: Mapped[Optional[datetime.date]]
    __table_args__ = (Index(
            "uq_inactive_country",
            "name", "end_date",
            unique=True,
            postgresql_where=text("still_exists IS FALSE")),
            CheckConstraint(
            "(still_exists IS TRUE AND end_date IS NULL) OR "
            "(still_exists IS FALSE AND end_date IS NOT NULL)",
            name="chk_country_status"
        ),
        Index(
            "uq_active_country_name",
            "name",
            unique=True,
            postgresql_where=text("still_exists IS TRUE")
        )
        )
class Region(BaseModel):
    __tablename__ = "regions"
    country_id: Mapped[Optional[int]] = mapped_column(ForeignKey(Country.id))
    country: Mapped[Country] = relationship(back_populates="regions")
    cities: Mapped[Optional[list["City"]]] = relationship(back_populates="region")
    __table_args__ = (UniqueConstraint("country_id", "name"),)


class City(BaseModel):
    __tablename__ = "cities"
    region_id: Mapped[Optional[int]] = mapped_column(ForeignKey(Region.id))
    region: Mapped[Optional["Region"]] = relationship(back_populates="cities")
    country_id: Mapped[Optional[int]] = mapped_column(ForeignKey(Country.id))
    authors: Mapped[Optional[list["Author"]]] = relationship(
        back_populates="birth_city"
    )
    __table_args__ = (
        CheckConstraint(
            "(region_id is NOT NULL and country_id is NULL) OR (country_id is NOT NULL and region_id is NULL)"
        ),
        Index(
            "uq_city_region",
            "region_id",
            "name",
            unique=True,
            postgresql_where=(region_id.isnot(None)),
        ),
        Index(
            "uq_city_country",
            "country_id",
            "name",
            unique=True,
            postgresql_where=(country_id.isnot(None)),
        ),
    )


class Author(BaseModel):
    __tablename__ = "authors"
    goodreads_id: Mapped[Optional[int]] = mapped_column(unique=True)
    goodreads_link: Mapped[Optional[str]] = mapped_column(unique=True)
    birth_city_id = mapped_column(ForeignKey(City.id))
    birth_city: Mapped[City] = relationship(back_populates="authors")


Base.metadata.create_all(engine)
brasil = Country(name="Brasil")
rio = Region(name="Rio de Janeiro", country=brasil)
tere = City(name="Teresópolis", region=rio)
ni = City(name="Nova Iguacu", region=rio)
a = Author(name="ze", birth_city=ni)
b = Author(name="cuin", birth_city=tere)
c = Author(name="mr", birth_city=ni)
session.add_all([brasil])
session.commit()
print(brasil)
