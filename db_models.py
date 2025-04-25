from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped,sessionmaker, mapped_column, relationship

db_url = 'sqlite:///t.db'

engine = create_engine(db_url)

Session = sessionmaker(bind=engine)
session = Session()


class Base(DeclarativeBase):
    pass

class BaseModel(Base):
    __abstract__ = True # This allows it to be inherited by other classes.
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    def __repr__(self):
        return f"Class: {type(self).__name__} Id: {self.id}, name: {self.name}"
    
class Country(BaseModel):
    __tablename__ = "countries"
    regions: Mapped[list["Region"]] = relationship(back_populates="country") # Writes to Region.country


class Region(BaseModel):
    __tablename__ = "regions"
    country_id: Mapped[Optional[int]] = mapped_column(ForeignKey(Country.id))
    country: Mapped[Country] = relationship(back_populates="regions")
    cities: Mapped[Optional[list["City"]]] = relationship(back_populates="region")

class City(BaseModel):
    __tablename__ = "cities"
    region_id: Mapped[Optional[int]] = mapped_column(ForeignKey(Region.id))
    region: Mapped[Optional["Region"]] = relationship(back_populates="cities")
    country_id: Mapped[Optional[int]] = mapped_column(ForeignKey(Country.id))
    authors: Mapped[Optional[list["Author"]]] = relationship(back_populates="city")

class Author(BaseModel):
    __tablename__ = "authors"
    goodreads_id: Mapped[Optional[int]]
    goodreads_link: Mapped[Optional[str]]
    birth_city_id = mapped_column(ForeignKey(City.id))
    city: Mapped[City] = relationship(back_populates="authors")

Base.metadata.create_all(engine)
brasil = Country(name="Brasil")
rio = Region(name="Rio de Janeiro", country=brasil)
tere = City(name="Teresópolis", region = rio)
ni = City(name="Nova Iguacu", region = rio)
a = Author(name= "ze", city = ni)
b = Author(name = "cuin",city=tere)
c = Author(name= "mr", city=ni)
session.add(brasil)
session.commit()
print(brasil)

