from goodreads_scraper.scrape import process_profile, scrape_gr_author
from typing import Dict, List
from collections import Counter
import pycountry
from database import (
    fetch_author_by_id,
    insert_authors,
    SessionLocal,
    fetch_authors_by_id,
)
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()


def extract_authors(books: List[Dict[str, str]]) -> Counter:
    """From the books list, generate a Counter object with the number of books per author.
    The author is identified by the tuple of his id in Goodreads, the link to his page and his name.

    Args:
        books (List[Dict[str, str]]): List of books scraped from the GR website.

    Returns:
        Counter: Counter object with the book count per author.
    """
    author_tuples = [
        (book["author_id"], book["author_link"], book["author_name"]) for book in books
    ]
    author_tuple_counts = Counter(author_tuples)
    return author_tuple_counts


def generate_country_count(cont: Counter) -> Dict[str, int]:
    """Optimized version of generating a country count from a counter of books per author.

    Args:
        cont (Counter): Counter object with the book count per author.

    Returns:
        Dict[str, int]: Dictionary with the number of books read per country.
    """
    country_counter = {}
    author_ids = [author_id for (author_id, _, _) in cont.keys()]

    with SessionLocal() as session:
        # Fetch all authors at once and cache them
        authors = fetch_authors_by_id(session, author_ids)
        author_cache = {author.id: author for author in authors}

        # Prepare data for authors not found in the database
        missing_authors = []

        for (author_id, author_link, author_name), count in cont.items():
            if author_id in author_cache:
                author = author_cache[author_id]
                country = author.birth_country
            else:
                # If author not found, scrape and prepare for bulk insert
                birthplace, country = scrape_gr_author(author_link)
                missing_authors.append(
                    {
                        "birth_place": birthplace,
                        "birth_country": country,
                        "id": author_id,
                        "name": author_name,
                        "gr_link": author_link,
                    }
                )

            # Update country counter
            if country:
                country_counter[country] = country_counter.get(country, 0) + count

        # Bulk insert missing authors
        if missing_authors:
            insert_authors(session, missing_authors)

    return country_counter


def process_country_count(country_count: Dict[str, int]) -> List[Dict[str, any]]:
    # Get a list of all country names using pycountry
    all_countries = [country.name for country in pycountry.countries]

    # Prepare a list to store the results
    complete_data = {}

    # Fill in the count for each country or set it to 0 if not present
    for country in all_countries:
        count = country_count.get(country, 0)  # Get the count or default to 0
        complete_data[country] = count

    return complete_data


if __name__ == "__main__":
    user_profile = "https://www.goodreads.com/user/show/60671411-frank-phillips"
    books = process_profile(user_profile)
    cont = extract_authors(books)
    cc = generate_country_count(cont)
    df = process_country_count(cc)
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.dump_stats("./profile/new_profile.prof")
