import pytest
from backend import extract_authors, process_birthplace

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
    "birthplace, expected",
    [
        (
            "Limoeiro do Norte, Ceará, Brazil",
            {"country": "Brazil", "region": "Ceará", "city": "Limoeiro do Norte"},
        ),
        ("Rome, Italy", {"country": "Italy", "city": "Rome"}),
        ("", None),
    ],
)
def test_birthplace_processing(birthplace, expected):
    result = process_birthplace(birthplace)
    assert result == expected
