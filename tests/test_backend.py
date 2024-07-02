import pytest
from backend import extract_authors, generate_country_count, process_birthplace
from goodreads_scraper.scrape import scrape_shelf, create_shelf_url
from collections import Counter
from unittest.mock import patch
from graph_models import Author

# Sample books data

author_1 = Author(
    goodreads_id=696805,
    goodreads_link="https://www.goodreads.com/author/show/696805.Jules_Verne",
    name="Jules Vernes",
)

author_2 = Author(
    goodreads_link="https://www.goodreads.com/author/show/22458.Machado_de_Assis",
    goodreads_id=22458,
    names="Machado de Assis",
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
        {("1", "link1", "Author One"): 2, ("2", "link2", "Author Two"): 1}
    )
    assert extract_authors(sample_books) == expected_count


def mock_fetch_author_by_id(session, author_id):
    return sample_authors.get(author_id)


def mock_scrape_gr_author(author_link):
    if "link1" in author_link:
        return "United States"
    elif "link2" in author_link:
        return "Germany"
    return None


def mock_insert_author(session, author_data):
    sample_authors[author_data["id"]] = {"birth_country": author_data["birth_country"]}


def test_generate_country_count():
    # Counter object from `extract_authors` simulation
    authors_counter = Counter(
        {
            (author_1.goodreads_id, author_1.goodreads_link, author_1.name): 2,
            (author_2.goodreads_id, author_2.goodreads_link, author_2.name): 1,
        }
    )

    # Patching the database session and scraping function
    with patch(
        "backend.fetch_author_by_id", side_effect=mock_fetch_author_by_id
    ), patch("backend.scrape_gr_author", side_effect=mock_scrape_gr_author), patch(
        "backend.insert_author", side_effect=mock_insert_author
    ), patch(
        "backend.SessionLocal"
    ) as mock_session:
        # Run the function with the mocked session and data
        country_count = generate_country_count(authors_counter)

        # Expected results
        expected_countries = {"France": 2, "Brazil": 1}

        # Assert to check if the results match the expected output
        assert country_count == expected_countries, "Country counts are incorrect"


def test_integration():
    authors_counter = extract_authors(sample_books)
    with patch(
        "backend.fetch_author_by_id", side_effect=mock_fetch_author_by_id
    ), patch("backend.scrape_gr_author", side_effect=mock_scrape_gr_author), patch(
        "backend.insert_author", side_effect=mock_insert_author
    ), patch(
        "backend.SessionLocal"
    ) as mock_session:
        # Run the function with the mocked session and data
        country_count = generate_country_count(authors_counter)

        # Expected results
        expected_countries = {"France": 2, "Brazil": 1}

        # Assert to check if the results match the expected output
        assert country_count == expected_countries, "Country counts are incorrect"


def test_real_shelf():
    books = scrape_shelf(
        "https://www.goodreads.com/review/list/66818479-lucas-pavanelli?shelf=read"
    )
    authors = extract_authors(books)
    country_count = generate_country_count(authors)
    assert len(books) >= sum(
        country_count.values()
    ), "Country counts are larger than the number of books."


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
