from bookscraper_backend.tests.conftest import SessionFactory, random_world, cleanup_tables
from hypothesis import given, settings, HealthCheck
from bookscraper_backend.database import db_models, db_logic
from collections import Counter

settings.register_profile(
    "my_profile", suppress_health_check=[HealthCheck.function_scoped_fixture]
)
settings.load_profile("my_profile")

@given(authors = random_world())
def test_fetch_all_authors(db_session_factory: SessionFactory, authors: list[db_models.Author]) -> None:
    print(f"Running test with {len(authors)} authors")
    with db_session_factory() as db_session:
        cleanup_tables(db_session) # A single session has multiple examples due to shrinkage, so better cleanup!
        db_session.add_all(authors)
        db_session.commit()
        all_authors = db_logic.fetch_all_authors(db_session)
    assert len(all_authors) == len(authors)

@given(authors=random_world())
def test_find_missing_authors(db_session_factory: SessionFactory, authors: list[db_models.Author]) -> None:
    # We get a few authors that are not in the db for sure.
    scrapped_authors = Counter({(696805, 'https://www.goodreads.com/author/show/696805.Jules_Verne', 'Jules Vernes'): 2, (22458, 'https://www.goodreads.com/author/show/22458.Machado_de_Assis', 'Machado de Assis'): 1})
    existing_ids = [author.goodreads_id for author in authors]
    missing_authors = [item for item in scrapped_authors.items() if item[0][0] not in existing_ids]
    assert db_logic.find_missing_authors(db_authors=authors, scrapped_authors=scrapped_authors) == missing_authors
    