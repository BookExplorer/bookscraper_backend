from hypothesis import strategies as st
from datetime import date
from src.database.setup import db_session
import src.database.db_models as db_models

def countries():
    return st.builds(
        db_models.Country,
        name=st.text(min_size=2, max_size=50),
        still_exists=st.booleans(),
        end_date=st.dates() | st.none()
    )

def valid_countries():
    return st.one_of(
        st.builds(
            db_models.Country,
            name=st.text(min_size=2, max_size=50),
            still_exists=st.just(True),
            end_date=st.none()
        ),
        st.builds(
            db_models.Country,
            name=st.text(min_size=2, max_size=50),
            still_exists=st.just(False),
            end_date=st.dates(min_value=date(1900, 1, 1))
        )
    )

brasil = db_models.Country(name="Brasil")
rio = db_models.Region(name="Rio de Janeiro", country=brasil)
tere = db_models.City(name="Teresópolis", region=rio)
ni = db_models.City(name="Nova Iguacu", region=rio)
a = db_models.Author(name="ze", birth_city=ni)
b = db_models.Author(name="cuin", birth_city=tere)
c = db_models.Author(name="mr", birth_city=ni)
db_session.add_all([brasil])
db_session.commit()
print(brasil)
