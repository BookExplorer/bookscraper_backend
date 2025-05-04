from hypothesis import strategies as st
from datetime import date
from db_models import Country, Region, City

def countries():
    return st.builds(
        Country,
        name=st.text(min_size=2, max_size=50),
        still_exists=st.booleans(),
        end_date=st.dates() | st.none()
    )

def valid_countries():
    return st.one_of(
        st.builds(
            Country,
            name=st.text(min_size=2, max_size=50),
            still_exists=st.just(True),
            end_date=st.none()
        ),
        st.builds(
            Country,
            name=st.text(min_size=2, max_size=50),
            still_exists=st.just(False),
            end_date=st.dates(min_value=date(1900, 1, 1))
        )
    )