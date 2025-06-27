from bookscraper_backend.tests.conftest import SessionFactory, random_world, cleanup_tables
from hypothesis import given, settings, HealthCheck
from bookscraper_backend.database import db_models, db_logic

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