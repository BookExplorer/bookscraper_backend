import pytest
from sqlalchemy.exc import IntegrityError
from bookscraper_backend.database import db_models
from sqlalchemy.orm import Session


def test_valid_existing_country(
    test_db_session: Session, valid_existing_country: db_models.Country
) -> None:
    test_db_session.add(valid_existing_country)
    test_db_session.commit()
    assert valid_existing_country.id is not None


def test_valid_former_country(
    test_db_session: Session, valid_former_country: db_models.Country
) -> None:
    """
    A valid former country can be safely created.
    """
    test_db_session.add(valid_former_country)
    test_db_session.commit()
    assert valid_former_country.id is not None


def test_invalid_existing_country(
    test_db_session: Session, invalid_existing_country: db_models.Country
) -> None:
    """
    An active country cannot have an end date.
    """
    test_db_session.add(invalid_existing_country)
    with pytest.raises(IntegrityError) as exc:
        test_db_session.commit()
    assert "chk_country_status" in str(exc.value)


def test_invalid_former_country(
    test_db_session: Session, invalid_former_country: db_models.Country
) -> None:
    """
    A former country needs to have an end_date.
    """
    test_db_session.add(invalid_former_country)
    with pytest.raises(IntegrityError) as exc:
        test_db_session.commit()
    assert "chk_country_status" in str(exc.value)


def test_unique_active_country_name(
    test_db_session: Session, valid_existing_country: db_models.Country
) -> None:
    """
    There can be no two active countries with the same name and the same end date.
    """
    test_db_session.add(valid_existing_country)
    test_db_session.commit()
    assert valid_existing_country.id is not None
    duplicate = db_models.Country(
        name=valid_existing_country.name, still_exists=True, end_date=None
    )
    test_db_session.add(duplicate)
    with pytest.raises(IntegrityError) as exc:
        test_db_session.commit()
    assert "uq_active_country_name" in str(exc.value)


def test_unique_former_country_name(
    test_db_session: Session, valid_former_country: db_models.Country
) -> None:
    """
    There can be no two former countries with the same name.
    """
    test_db_session.add(valid_former_country)
    test_db_session.commit()
    assert valid_former_country.id is not None
    duplicate = db_models.Country(
        name=valid_former_country.name,
        still_exists=False,
        end_date=valid_former_country.end_date,
    )
    test_db_session.add(duplicate)
    with pytest.raises(IntegrityError) as exc:
        test_db_session.commit()
    assert "uq_inactive_country" in str(exc.value)


def test_valid_region_creation(
    test_db_session: Session, valid_country: db_models.Country
) -> None:
    """
    A valid region can be safely created.
    """
    region = db_models.Region(name=valid_country.name, country=valid_country)
    test_db_session.add(region)
    test_db_session.commit()
    assert region.id is not None
    assert region.country.id == valid_country.id


def test_region_unique_constraint(
    test_db_session: Session, valid_country: db_models.Country
) -> None:
    """
    Regions inside of a country should be unique by name.
    """
    region_1 = db_models.Region(name=valid_country.name, country=valid_country)
    test_db_session.add(region_1)
    test_db_session.commit()
    assert region_1.id is not None
    assert region_1.country.id == valid_country.id
    region_2 = db_models.Region(name=valid_country.name, country=valid_country)
    test_db_session.add(region_2)
    with pytest.raises(IntegrityError) as exc:
        test_db_session.commit()
    assert "regions_country_id_name_key" in str(exc.value)


def test_city_check_constraint_nothing(
    test_db_session: Session, valid_country: db_models.Country
) -> None:
    """
    A city must be connected to either a region or a country, it cannot be an orphan.
    """
    city_without_anything = db_models.City(name=valid_country.name)
    test_db_session.add(city_without_anything)
    with pytest.raises(IntegrityError) as exc:
        test_db_session.commit()
    assert "cities_check" in str(exc.value)


def test_city_check_constraint_both(
    test_db_session: Session, valid_country: db_models.Country
) -> None:
    """
    A city cannot be directly inside of a country and a region. It's one or the other.
    """
    valid_country = db_models.Country(name=valid_country.name, still_exists=True)
    region = db_models.Region(name=valid_country.name, country=valid_country)
    city_with_both = db_models.City(
        name=valid_country.name, country=valid_country, region=region
    )
    test_db_session.add(city_with_both)
    with pytest.raises(IntegrityError) as exc:
        test_db_session.commit()
    assert "cities_check" in str(exc.value)


def test_city_uq_city_region(
    test_db_session: Session, valid_country: db_models.Country
) -> None:
    """Test uniqueness constraint of city.name directly inside of region.

    If a city is directly inside of a region,
    then there should be no other city in that region with the same name.
    """
    region = db_models.Region(name=valid_country.name, country=valid_country)
    test_db_session.add(region)
    test_db_session.commit()
    city_1 = db_models.City(name=valid_country.name, region=region)
    city_2 = db_models.City(name=valid_country.name, region=region)
    test_db_session.add(city_1)
    test_db_session.commit()
    test_db_session.add(city_2)
    with pytest.raises(IntegrityError) as exc:
        test_db_session.commit()
    assert "uq_city_region" in str(exc.value)


def test_city_uq_city_country(
    test_db_session: Session, valid_country: db_models.Country
) -> None:
    """Test uniqueness constraint of city.name directly inside of country.

    If a city is not inside of a region but is directly inside of a country,
    then there should be no other city in that country with the same name.
    """
    test_db_session.add(valid_country)
    test_db_session.commit()
    city_1 = db_models.City(name=valid_country.name, country=valid_country)
    city_2 = db_models.City(name=valid_country.name, country=valid_country)
    test_db_session.add(city_1)
    test_db_session.commit()
    test_db_session.add(city_2)
    with pytest.raises(IntegrityError) as exc:
        test_db_session.commit()
    assert "uq_city_country" in str(exc.value)


def test_linked_creation(test_db_session: Session, valid_country: db_models.Country) -> None:
    """This test should verify that commiting just an author linked to other classes creates everything IF EVERYTHING IS CORRECT.

    What this means is that an author born in a city X,
    inside region Y, inside country Z, can be solely added and commited
    without other additions and everything gets created.
    """
    region = db_models.Region(name=valid_country.name, country=valid_country)
    city = db_models.City(name=valid_country.name, region=region)
    author = db_models.Author(name=valid_country.name, birth_city=city)
    test_db_session.add(author)
    test_db_session.commit()
    other_author = db_models.Author(name=f"{valid_country.name}a", birth_city=city)
    test_db_session.add(other_author)
    test_db_session.commit()
    assert author.id is not None
    assert city.id is not None
    assert region.id is not None
    assert valid_country.id is not None
    assert other_author.id is not None

    assert region.country_id == valid_country.id
    assert city.region_id == region.id
    assert author.birth_city_id == city.id
    assert other_author.birth_city_id == city.id
    assert other_author.id != author.id


def test_linked_creation_repeats(
    test_db_session: Session, valid_country: db_models.Country
) -> None:
    """This test should verify that commiting just an author linked to other classes creates everything IF EVERYTHING IS CORRECT.

    What this means is that an author born in a city X,
    inside region Y, inside country Z, can be solely added and commited
    without other additions and everything gets created.
    """
    # todo: This does not pass anymore. Is this a feature or a bug?
    # because if you create a wrong city, everything would fail anyway, but you could catch it early...
    region = db_models.Region(name=valid_country.name, country=valid_country)
    city = db_models.City(name=valid_country.name, region=region)
    author = db_models.Author(name=valid_country.name, birth_city=city)
    test_db_session.add(author)
    test_db_session.commit()
    assert author.id is not None
    assert city.id is not None
    assert region.id is not None
    assert valid_country.id is not None
    duplicate_city = db_models.City(name=valid_country.name, region=region)
    other_author = db_models.Author(
        name=f"{valid_country.name}a", birth_city=duplicate_city
    )
    test_db_session.add(other_author)
    with pytest.raises(IntegrityError):
        test_db_session.commit()
    assert other_author.id is None
    assert duplicate_city.id is None
