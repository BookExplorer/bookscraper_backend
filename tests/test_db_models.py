from hypothesis import strategies as st
from datetime import date
import bookscraper_backend.database.db_models as db_models

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

Base.metadata.create_all(engine)
brasil = Country(name="Brasil")
rio = Region(name="Rio de Janeiro", country=brasil)
tere = City(name="Teresópolis", region=rio)
ni = City(name="Nova Iguacu", region=rio)
a = Author(name="ze", birth_city=ni)
b = Author(name="cuin", birth_city=tere)
c = Author(name="mr", birth_city=ni)
session.add_all([brasil])
session.commit()
print(brasil)
