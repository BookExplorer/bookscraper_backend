from hypothesis import given, assume, strategies as st
import string
import pytest
from sqlalchemy.exc import IntegrityError
from bookscraper_backend.database import db_models
from bookscraper_backend.database.setup import db_session

naming_strategy = st.text(alphabet=string.ascii_letters + " -", min_size=1)



@st.composite
def valid_existing_country(draw):
    name = draw(naming_strategy)
    return db_models.Country(name=name, still_exists=True, end_date = None)

@st.composite
def invalid_existing_country(draw):
    name = draw(naming_strategy)
    return db_models.Country(name=name, still_exists=True, end_date = draw(st.dates()))

@st.composite
def valid_former_country(draw):
    name = draw(naming_strategy)
    return db_models.Country(name=name, still_exists=False, end_date = draw(st.dates()))

@st.composite
def invalid_former_country(draw):
    name = draw(naming_strategy)
    return db_models.Country(name=name, still_exists=False, end_date = None)
