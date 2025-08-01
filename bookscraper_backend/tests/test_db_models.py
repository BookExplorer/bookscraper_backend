from hypothesis import given, HealthCheck, settings
import pytest
from sqlalchemy.exc import IntegrityError
from bookscraper_backend.database import db_models
from datetime import date
from bookscraper_backend.tests.conftest import SessionFactory, naming_strategy, random_world

VALID_EXISTING_COUNTRIES = [
    db_models.Country(name="United States", still_exists=True, end_date=None),
    db_models.Country(name="France", still_exists=True, end_date=None),
    db_models.Country(name="Côte d'Ivoire", still_exists=True, end_date=None),
]

INVALID_EXISTING_COUNTRIES = [
    db_models.Country(name="United States", still_exists=True, end_date=date.today()),
    db_models.Country(name="France", still_exists=True, end_date=date.today()),
    db_models.Country(name="Côte d'Ivoire", still_exists=True, end_date=date.today()),
]

VALID_FORMER_COUNTRIES = [
    db_models.Country(name="Soviet Union", still_exists=False, end_date=date(1991, 12, 26)),
    db_models.Country(name="Yugoslavia", still_exists=False, end_date=date(1992, 4, 27)),
    db_models.Country(name="East Germany", still_exists=False, end_date=date(1990, 10, 3)),
]

INVALID_FORMER_COUNTRIES = [
    db_models.Country(name="Soviet Union", still_exists=False, end_date=None),
    db_models.Country(name="Yugoslavia", still_exists=False, end_date=None),
    db_models.Country(name="East Germany", still_exists=False, end_date=None),
]
settings.register_profile(
    "my_profile", suppress_health_check=[HealthCheck.function_scoped_fixture]
)
settings.load_profile("my_profile")

@pytest.mark.parametrize("country", VALID_EXISTING_COUNTRIES)
def test_valid_existing_country(db_session_factory: SessionFactory, country: db_models.Country) -> None:
     """
     A valid existing country can be safely created.
     """
     with db_session_factory() as session:
        session.add(country)
        session.commit()
        assert country.id is not None


@pytest.mark.parametrize("country", VALID_FORMER_COUNTRIES)
def test_valid_former_country(db_session_factory: SessionFactory, country: db_models.Country) -> None:
    """
    A valid former country can be safely created.
    """
    with db_session_factory() as session:
        session.add(country)
        session.commit()
        assert country.id is not None


@pytest.mark.parametrize("country", INVALID_EXISTING_COUNTRIES)
def test_invalid_existing_country(db_session_factory: SessionFactory, country: db_models.Country) -> None:
    """
    An active country cannot have an end date.
    """
    
    with db_session_factory() as db_session:
        db_session.add(country)
        with pytest.raises(IntegrityError) as exc:
            db_session.commit()
    assert "chk_country_status" in str(exc.value)


@pytest.mark.parametrize("country", INVALID_FORMER_COUNTRIES)
def test_invalid_former_country(db_session_factory: SessionFactory, country: db_models.Country) -> None:
    """
    A former country needs to have an end_date.
    """
    with db_session_factory() as db_session:   
        db_session.add(country)
        with pytest.raises(IntegrityError) as exc:
            db_session.commit()
    assert "chk_country_status" in str(exc.value)


@pytest.mark.parametrize("country", VALID_EXISTING_COUNTRIES)
def test_unique_active_country_name(db_session_factory: SessionFactory, country: db_models.Country) -> None:
    """
    There can be no two active countries with the same name.
    """
    with db_session_factory() as db_session:
        db_session.add(country)
        db_session.commit()
        assert country.id is not None
        duplicate = db_models.Country(
            name=country.name,  # Same name!
            still_exists=True,  # Must be active
            end_date=None
        )
        db_session.add(duplicate)
        with pytest.raises(IntegrityError) as exc:
            db_session.commit()
    assert "uq_active_country_name" in str(exc.value)



@pytest.mark.parametrize("country", VALID_FORMER_COUNTRIES)
def test_unique_former_country_name(db_session_factory: SessionFactory, country: db_models.Country) -> None:
    """
    There can be no two former countries with the same name.
    """
    with db_session_factory() as db_session:
        db_session.add(country)
        db_session.commit()
        assert country.id is not None
        duplicate = db_models.Country(name=country.name, still_exists=False, end_date=date.today())
        db_session.add(duplicate)
        with pytest.raises(IntegrityError) as exc:
            db_session.commit()
    assert "uq_inactive_country" in str(exc.value)



@pytest.mark.parametrize("country", VALID_FORMER_COUNTRIES+VALID_EXISTING_COUNTRIES)
def test_valid_region_creation(db_session_factory: SessionFactory, country: db_models.Country) -> None:
    """
    A valid region can be safely created.
    """
    with db_session_factory() as db_session:
        db_session.add(country)
        db_session.commit()
        region = db_models.Region(name=country.name, country=country)
        db_session.add(region)
        db_session.commit()
        assert region.id is not None
        assert region.country.id == country.id



@pytest.mark.parametrize("country", VALID_FORMER_COUNTRIES+VALID_EXISTING_COUNTRIES)
def test_region_unique_constraint(db_session_factory: SessionFactory, country: db_models.Country) -> None:
    """
    Regions inside of a country should be unique by name.
    """
    with db_session_factory() as db_session:
        db_session.add(country)
        db_session.commit()
        region_1 = db_models.Region(name=country.name, country=country)
        db_session.add(region_1)
        db_session.commit()
        assert region_1.id is not None
        assert region_1.country.id == country.id
        region_2 = db_models.Region(name=country.name, country=country)
        db_session.add(region_2)
        with pytest.raises(IntegrityError) as exc:
            db_session.commit()
    assert "regions_country_id_name_key" in str(exc.value)


@pytest.mark.parametrize("country", VALID_FORMER_COUNTRIES+VALID_EXISTING_COUNTRIES)
def test_city_check_constraint_nothing(db_session_factory: SessionFactory, country: db_models.Country) -> None:
    """
    A city must be connected to either a region or a country, it cannot be an orphan.
    """
    with db_session_factory() as db_session:
        db_session.add(country)
        db_session.commit()
        region = db_models.Region(name=country.name, country=country)
        db_session.add(region)
        db_session.commit()
        city_without_anything = db_models.City(name=country.name)
        db_session.add(city_without_anything)
        with pytest.raises(IntegrityError) as exc:
            db_session.commit()
    assert "cities_check" in str(exc.value)

@given(name=naming_strategy)
def test_city_check_constraint_both(db_session_factory: SessionFactory, name: str) -> None:
    """
    A city cannot be directly inside of a country and a region. It's one or the other.
    """
    with db_session_factory() as db_session:
        country_name = f"country_{name}"
        region_name = f"region_{name}"
        city_name = f"city_{name}"    
        country = db_models.Country(name=country_name, still_exists = True)
        region = db_models.Region(name=region_name, country=country)
        city_with_both = db_models.City(name=city_name, country=country, region=region)
        db_session.add(city_with_both)
        with pytest.raises(IntegrityError) as exc:
            db_session.commit()
    assert "cities_check" in str(exc.value)


@given(name=naming_strategy)
def test_city_uq_city_region(db_session_factory: SessionFactory, name: str) -> None:
    """Test uniqueness constraint of city.name directly inside of region.

    If a city is directly inside of a region, 
    then there should be no other city in that region with the same name.
    """
    with db_session_factory() as db_session:
        country_name = f"country_{name}"
        region_name = f"region_{name}"
        city_name = f"city_{name}"    
        country = db_models.Country(name=country_name, still_exists = True)
        region = db_models.Region(name=region_name, country=country)
        city_1 = db_models.City(name=city_name, region=region)
        city_2 = db_models.City(name=city_name, region=region)
        db_session.add(city_1)
        db_session.commit()
        db_session.add(city_2)
        with pytest.raises(IntegrityError) as exc:
            db_session.commit()
        assert "uq_city_region" in str(exc.value)


@given(name=naming_strategy)
def test_city_uq_city_country(db_session_factory: SessionFactory, name: str) -> None:
    """Test uniqueness constraint of city.name directly inside of country.

    If a city is not inside of a region but is directly inside of a country, 
    then there should be no other city in that country with the same name.
    """
    with db_session_factory() as db_session:
        country_name = f"country_{name}"
        city_name = f"city_{name}"    
        country = db_models.Country(name=country_name, still_exists = True)
        city_1 = db_models.City(name=city_name, country=country)
        city_2 = db_models.City(name=city_name, country=country)
        db_session.add(city_1)
        db_session.commit()
        db_session.add(city_2)
        with pytest.raises(IntegrityError) as exc:
            db_session.commit()
        assert "uq_city_country" in str(exc.value)


@given(name=naming_strategy)
def test_linked_creation(db_session_factory: SessionFactory, name: str) -> None:
    """This test should verify that commiting just an author linked to other classes creates everything.

    What this means is that an author born in a city X, 
    inside region Y, inside country Z, can be solely added and commited 
    without other additions and everything gets created.
    """
    #This test is weird and actually shrinking, loops back after author??? 
    #FIXME: Why does shrinkage not fail???
    with db_session_factory() as db_session:
        country_name = f"country_{name}"
        region_name = f"region_{name}"
        city_name = f"city_{name}"
        author_name = f"author_{name}"
        country = db_models.Country(name=country_name, still_exists = True)
        region = db_models.Region(name=region_name, country=country)
        city = db_models.City(name=city_name, region=region)
        author = db_models.Author(name=author_name, birth_city=city)
        db_session.add(author)
        db_session.commit()
        other_author = db_models.Author(name=f"{author_name}a", birth_city=city)
        db_session.add(other_author)
        db_session.commit()
        assert author.id == 1
        assert city.id == 1
        assert region.id ==1
        assert country.id == 1
        assert other_author.id == 2

@given(authors=random_world())
def test_regular_creation(db_session_factory: SessionFactory, authors: list[db_models.Author]) -> None:
    with db_session_factory() as db_session:
        db_session.add_all(authors)
        db_session.commit()
        for author in authors:
            assert author.id is not None
            assert author.birth_city_id is not None
            assert (author.birth_city.region_id is not None) or (author.birth_city.country_id is not None) #type: ignore