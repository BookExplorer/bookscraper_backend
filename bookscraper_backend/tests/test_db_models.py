from hypothesis import given, assume, strategies as st
import string
import pytest
from sqlalchemy.exc import IntegrityError
from bookscraper_backend.database import db_models
from bookscraper_backend.database.setup import db_session

#TODO: Maybe define from this invalid countries and valid countries and all that.
@given(
    name=st.text(alphabet=string.ascii_letters + " -", min_size=1, max_size=50),
    still_exists=st.booleans(),
    end_date=st.one_of(st.none(), st.dates())
)
def test_country_constraints(name, still_exists, end_date):
    c = db_models.Country(name=name, still_exists=still_exists, end_date=end_date)
    db_session.add(c)
    should_fail = (still_exists and end_date is not None) or (not still_exists and end_date is None)

    try:
        db_session.commit()
    except IntegrityError:
        db_session.rollback()
        assert should_fail, f"Expected the bad combo ({still_exists=}, {end_date=}) to fail"
    else:
        assert not should_fail, f"Expected the good combo ({still_exists=}, {end_date=}) to pass"