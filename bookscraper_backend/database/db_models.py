from typing import Optional
from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    Index,
    text,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

import datetime


class Base(DeclarativeBase):
    pass


# TODO: Auto generate migrations from models, assume tests will have all applied?, then run tests


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
    cities: Mapped[list["City"]] = relationship(back_populates="country")
    still_exists: Mapped[Optional[bool]] = mapped_column(default=True)
    end_date: Mapped[Optional[datetime.date]]
    __table_args__ = (
        Index(
            "uq_inactive_country",
            "name",
            "end_date",
            unique=True,
            postgresql_where=text("still_exists IS FALSE"),
        ),
        CheckConstraint(
            "(still_exists IS TRUE AND end_date IS NULL) OR "
            "(still_exists IS FALSE AND end_date IS NOT NULL)",
            name="chk_country_status",
        ),
        Index(
            "uq_active_country_name",
            "name",
            unique=True,
            postgresql_where=text("still_exists IS TRUE"),
        ),
    )


class Region(BaseModel):
    __tablename__ = "regions"
    country_id: Mapped[Optional[int]] = mapped_column(ForeignKey(Country.id))
    country: Mapped[Country] = relationship(back_populates="regions") # Country.regions
    cities: Mapped[Optional[list["City"]]] = relationship(back_populates="region") # City.region
    __table_args__ = (UniqueConstraint("country_id", "name"),)


class City(BaseModel):
    __tablename__ = "cities"
    region_id: Mapped[Optional[int]] = mapped_column(ForeignKey(Region.id))
    region: Mapped[Optional["Region"]] = relationship(back_populates="cities")
    country_id: Mapped[Optional[int]] = mapped_column(ForeignKey(Country.id))
    country: Mapped[Optional["Country"]] = relationship(back_populates="cities")
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
    birth_city_id: Mapped[Optional[int]] = mapped_column(ForeignKey(City.id))
    birth_city: Mapped[Optional["City"]] = relationship(back_populates="authors")
