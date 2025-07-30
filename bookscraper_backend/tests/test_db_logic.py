from bookscraper_backend.tests.conftest import SessionFactory, random_world, cleanup_tables
from hypothesis import given, settings, HealthCheck
from bookscraper_backend.database import db_models, db_logic
from collections import Counter
import sqlalchemy as sa

settings.register_profile(
    "my_profile", suppress_health_check=[HealthCheck.function_scoped_fixture]
)
settings.load_profile("my_profile")
#TODO: Remove this. Hypothesis is simply too cumbersome for use in this project.

def test_fetch_all_authors(db_session_factory: SessionFactory, sample_data: None) -> None:
    with db_session_factory() as db_session:
        cleanup_tables(db_session) # A single session has multiple examples due to shrinkage, so better cleanup!
        db_session.commit()
        all_authors = db_logic.fetch_all_authors(db_session)
        assert len(all_authors) == 2



def test_find_missing_authors(db_session_factory: SessionFactory, sample_data: None) -> None:
    # We get a few authors that are not in the db for sure.
    with db_session_factory() as db_session:
        db_authors = db_session.query(db_models.Author).all()
    scrapped_authors = Counter({(696805, 'https://www.goodreads.com/author/show/696805.Jules_Verne', 'Jules Vernes'): 2, (22458, 'https://www.goodreads.com/author/show/22458.Machado_de_Assis', 'Machado de Assis'): 1})
    existing_ids = [1,2]
    expected_missing_authors = [item for item in scrapped_authors.items() if item[0][0] not in existing_ids]
    actual_missing_authors =db_logic.find_missing_authors(db_authors=db_authors, scrapped_authors=scrapped_authors) 
    assert actual_missing_authors == expected_missing_authors

@given(authors = random_world())
def test_generate_country_count(db_session_factory: SessionFactory, authors: list[db_models.Author]) -> None:
    
    scrapped_authors = Counter({(696805, 'https://www.goodreads.com/author/show/696805.Jules_Verne', 'Jules Vernes'): 2, (22458, 'https://www.goodreads.com/author/show/22458.Machado_de_Assis', 'Machado de Assis'): 1})
    with db_session_factory() as db_session:
        cleanup_tables(db_session) # A single session has multiple examples due to shrinkage, so better cleanup!
        db_session.add_all(authors)
        db_session.commit()
        db_logic.generate_country_count(db_session, scrapped_authors)


def test_insert_geo_dict(db_session_factory: SessionFactory) -> None:
    with db_session_factory() as db_session:
        cleanup_tables(db_session)
        simple_geo_dict =  {"country": "Brazil", "region": "Ceará", "city": "Limoeiro do Norte", "latitude": -5.1455607, "longitude": -38.0984936}
        city =  db_logic.process_geo_dict(db_session,simple_geo_dict)
        results = db_session.execute(sa.select(db_models.Country)).scalars().one()
        assert results is not None
        assert results.id == 1

@given(authors = random_world())
def test_double_insertion_geo_dict(db_session_factory: SessionFactory, authors: list[db_models.Author]) -> None:
        with db_session_factory() as db_session:
            cleanup_tables(db_session)
            db_session.add_all(authors)
            db_session.commit()
            simple_geo_dict =  {"country": "Brazil", "region": "Ceará", "city": "Limoeiro do Norte", "latitude": -5.1455607, "longitude": -38.0984936}
            db_logic.process_geo_dict(db_session,simple_geo_dict)
            db_logic.process_geo_dict(db_session,simple_geo_dict)
            country_results = db_session.execute(sa.select(db_models.Country)).scalars().all()
            assert country_results is not None
            assert len(country_results) == 1
            region_results = db_session.execute(sa.select(db_models.Region)).scalars().all()
            assert region_results is not None
            assert len(region_results) == 1
            city_results = db_session.execute(sa.select(db_models.City)).scalars().all()
            assert city_results is not None
            assert len(city_results) == 1