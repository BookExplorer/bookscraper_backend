import pytest
from backend import extract_authors, process_birthplace, get_lat_long_place

from collections import Counter
from graph_models import Author

# Sample books data

author_1 = Author(
    goodreads_id=696805,
    goodreads_link="https://www.goodreads.com/author/show/696805.Jules_Verne",
    name="Jules Vernes",
    country = "France"
)

author_2 = Author(
    goodreads_link="https://www.goodreads.com/author/show/22458.Machado_de_Assis",
    goodreads_id=22458,
    name="Machado de Assis",
    country = "Brazil"
)

sample_authors = {696805: author_1, 22458: author_2}
sample_books = [
    {
        "author_id": author_1.goodreads_id,
        "author_link": author_1.goodreads_link,
        "author_name": author_1.name,
    },
    {
        "author_id": author_2.goodreads_id,
        "author_link": author_2.goodreads_link,
        "author_name": author_2.name,
    },
    {
        "author_id": author_1.goodreads_id,
        "author_link": author_1.goodreads_link,
        "author_name": author_1.name,
    },
]


def test_author_extraction():
    expected_count = Counter(
        {(author_1.goodreads_id, author_1.goodreads_link, author_1.name): 2, (author_2.goodreads_id, author_2.goodreads_link, author_2.name): 1}
    )
    assert extract_authors(sample_books) == expected_count

@pytest.mark.parametrize(
        "place, expected",
                             [
        (
            "Limoeiro do Norte, Ceará, Brazil",
           (-5.1455607, -38.0984936),
        ),
        ("Rome, Italy", (41.8933203,12.4829321)),
        ("", None)
    ],
)
def test_get_lat_long_place(place, expected) -> None:
    lat_long =  get_lat_long_place(place)
    assert lat_long == expected

@pytest.mark.parametrize(
    "birthplace, expected",
    [
        (
            "Limoeiro do Norte, Ceará, Brazil",
            {"country": "Brazil", "region": "Ceará", "city": "Limoeiro do Norte", "latitude": -5.1455607, "longitude": -38.0984936},
        ),
        ("Rome, Italy", {"country": "Italy", "city": "Rome", "latitude": 41.8933203, "longitude": 12.4829321}),
        ("", None)
    ],
)
def test_birthplace_processing(birthplace, expected):
    result = process_birthplace(birthplace)
    assert result == expected
