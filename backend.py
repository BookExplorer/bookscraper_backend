from goodreads_scraper.scrape import process_profile, scrape_gr_author
from typing import Dict, List
from collections import Counter
from graph_models import Country, Region, Author, City
from graph_db import geo_nodes
import pycountry
from database import fetch_author_by_id, insert_author, SessionLocal
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
                birthplace, country = scrape_gr_author(
                    author_link
                )  # Scrape the birthplace
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


def process_birthplace(birthplace: str | None) -> Dict[str, str] | None:
    if birthplace:
        split_birthplace = birthplace.split(",")
        geo_dict = {}
        geo_dict["city"] = split_birthplace[0].strip()
        geo_dict["country"] = split_birthplace[-1].strip()
        if len(split_birthplace) > 2:
            geo_dict["region"] = split_birthplace[1].strip()
        geo_nodes(geo_dict)
        return geo_dict


if __name__ == "__main__":
    user_profile = "https://www.goodreads.com/user/show/71341746-tamir-einhorn-salem"
    books = process_profile(user_profile)
    cont = extract_authors(books)
    cc = generate_country_count(cont)
    df = process_country_count(cc)
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.dump_stats("./profile/my_profile.prof")
