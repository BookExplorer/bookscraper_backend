import pytest
from backend import extract_authors, generate_country_count
from collections import Counter
from unittest.mock import patch
from models import Author

# Sample books data
sample_books = [
    {"author_id": "1", "author_link": "link1", "author_name": "Author One"},
    {"author_id": "2", "author_link": "link2", "author_name": "Author Two"},
    {"author_id": "1", "author_link": "link1", "author_name": "Author One"},
]

author_1 = Author()
author_1.id = 1
author_1.birth_place = "USA"
author_1.birth_country = "United States"

author_2 = Author()
author_2.id = 2
author_2.birth_place = "Germany"
author_2.birth_country = "Germany"
# Sample authors data from the database
sample_authors = {
    "1": author_1,
    "2": author_2,
}


def test_author_extraction():
    expected_count = Counter(
        {("1", "link1", "Author One"): 2, ("2", "link2", "Author Two"): 1}
    )
    assert extract_authors(sample_books) == expected_count


# Mock database functions
def mock_fetch_author_by_id(session, author_id):
    return sample_authors.get(author_id)


def mock_scrape_gr_author(author_link):
    # Simulating scraping logic
    if "link1" in author_link:
        return "United States"
    elif "link2" in author_link:
        return "Germany"
    return None


def mock_insert_author(session, author_data):
    # Update or insert mock author data
    sample_authors[author_data["id"]] = {"birth_country": author_data["birth_country"]}


# Testing the `generate_country_count` function
def test_generate_country_count():
    # Counter object from `extract_authors` simulation
    authors_counter = Counter(
        {("1", "link1", "Author One"): 2, ("2", "link2", "Author Two"): 1}
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
        expected_countries = {"United States": 2, "Germany": 1}

        # Assert to check if the results match the expected output
        assert country_count == expected_countries, "Country counts are incorrect"
