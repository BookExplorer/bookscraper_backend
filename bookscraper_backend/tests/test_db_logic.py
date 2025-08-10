from bookscraper_backend.database import db_models, db_logic
from bookscraper_backend.backend import GeoDict
from collections import Counter
import sqlalchemy as sa
from sqlalchemy.orm import Session


def test_fetch_all_authors(test_db_session: Session, sample_data: None) -> None:
    test_db_session.commit()
    all_authors = db_logic.fetch_all_authors(test_db_session)
    assert len(all_authors) == 2


def test_find_missing_authors(test_db_session: Session, sample_data: None) -> None:
    # We get a few authors that are not in the db for sure.

    db_authors = test_db_session.query(db_models.Author).all()
    scrapped_authors = Counter(
        {
            (
                696805,
                "https://www.goodreads.com/author/show/696805.Jules_Verne",
                "Jules Vernes",
            ): 2,
            (
                22458,
                "https://www.goodreads.com/author/show/22458.Machado_de_Assis",
                "Machado de Assis",
            ): 1,
        }
    )
    existing_ids = [1, 2]
    expected_missing_authors = [
        item for item in scrapped_authors.items() if item[0][0] not in existing_ids
    ]
    actual_missing_authors = db_logic.find_missing_authors(
        db_authors=db_authors, scrapped_authors=scrapped_authors
    )
    assert actual_missing_authors == expected_missing_authors



def test_insert_geo_dict_with_region(test_db_session: Session) -> None:
    simple_geo_dict: GeoDict = {
        "country": "Brazil",
        "region": "Ceará",
        "city": "Limoeiro do Norte",
        "latitude": -5.1455607,
        "longitude": -38.0984936,
    }
    db_logic.insert_geo_dict(test_db_session, simple_geo_dict)
    country_results = test_db_session.execute(sa.select(db_models.Country)).scalars().all()
    assert len(country_results) == 1
    region_results = test_db_session.execute(sa.select(db_models.Region)).scalars().all()
    assert len(region_results) == 1
    city_results = test_db_session.execute(sa.select(db_models.City)).scalars().all()
    assert len(city_results) == 1


def test_insert_geo_dict_without_region(test_db_session: Session) -> None:
    simple_geo_dict: GeoDict = {
        "country": "Brazil",
        "city": "Limoeiro do Norte",
        "latitude": -5.1455607,
        "longitude": -38.0984936,
    }
    db_logic.insert_geo_dict(test_db_session, simple_geo_dict)
    country_results = test_db_session.execute(sa.select(db_models.Country)).scalars().all()
    assert len(country_results) == 1
    region_results = test_db_session.execute(sa.select(db_models.Region)).scalars().all()
    assert len(region_results) == 0
    city_results = test_db_session.execute(sa.select(db_models.City)).scalars().all()
    assert len(city_results) == 1

