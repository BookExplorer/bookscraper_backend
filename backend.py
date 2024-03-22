from goodreads_scraper.scrape import process_profile, scrape_shelf
from typing import Dict, List
from collections import Counter
from utils import scrape_gr_author, cleanup_birthplace
import pandas as pd
import pycountry
from database import fetch_author_by_id, insert_author, SessionLocal


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
    """From a counter of books per author, generate a similar one of country: books read from that country.


    Args:
        cont (Counter): Counter object with the book count per author.

    Returns:
        Dict[str, int]: Dictionary with the number of books read per country.
    """
    country_counter = {}
    with SessionLocal() as session:
        for (author_id, author_link, author_name), count in cont.items():
            author = fetch_author_by_id(session, author_id)
            if author:
                country = author.birth_country
            else:
                birthplace = scrape_gr_author(author_link)  # Scrape the birthplace
                country = cleanup_birthplace(birthplace)
                insert_author(
                    session,
                    {
                        "birth_place": birthplace,
                        "birth_country": country,
                        "id": author_id,
                        "name": author_name,
                        "gr_link": author_link,
                    },
                )
            if country and country in country_counter:
                country_counter[country] += count
            elif country:
                country_counter[country] = count
    return country_counter


def process_country_count(country_count: Dict[str, int]) -> pd.DataFrame:
    initial_df = pd.DataFrame(list(country_count.items()), columns=["country", "count"])
    country_names = {"country": [country.name for country in pycountry.countries]}

    all_countries = pd.DataFrame(country_names)

    complete_data = all_countries.merge(initial_df, on="country", how="left").fillna(0)

    return complete_data


if __name__ == "__main__":
    user_profile = "https://www.goodreads.com/user/show/71341746-tamir-einhorn-salem"
    books = process_profile(user_profile)
    cont = extract_authors(books)
    cc = generate_country_count(cont)
    df = process_country_count(cc)
