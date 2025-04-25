from typing import List
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship



class Base(DeclarativeBase):
    pass

class Countries(Base):
    __tablename__ = "countries"
    country_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country_name: Mapped[str]

class Region(Base):
    __tablename__ = "regions"
    region_id: Mapped[int] = mapped_column(primary_key=True)
    region_name: Mapped[str]

class City(Base):
    __tablename__ = "cities"
    city_id: Mapped[int] = mapped_column(primary_key=True)
    city_name: Mapped[str]

class Author(Base):
    __tablename__ = "authors"
    author_id: Mapped[int] = mapped_column(primary_key=True)
    author_name: Mapped[str]
    goodreads_id: Mapped[int]
    goodreads_link: Mapped[str]
