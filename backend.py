from goodreads_scraper.scrape import process_profile, scrape_shelf
from typing import Dict, List
from collections import Counter
from utils import scrape_gr_author, cleanup_birthplace
from graphs import generate_graph
import pandas as pd
from database import fetch_author_by_id, insert_author, SessionLocal


def extract_authors(books: List[Dict[str, str]]) -> Counter:
    author_tuples = [(book["author_id"], book["author_link"]) for book in books]
    author_tuple_counts = Counter(author_tuples)
    return author_tuple_counts


def generate_country_count(cont: Counter):
    author_info_dict = {}
    country_counter = {}
    with SessionLocal() as session:
        for (author_id, author_link), count in cont.items():
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
                        "gr_link": author_link,
                    },
                )
            author_info_dict[author_id] = {
                "link": author_link,
                "count": count,
                "birthplace": birthplace,
                "country": country,
            }
            if country and country in country_counter:
                country_counter[country] += 1
            elif country:
                country_counter[country] = 1
    return country_counter


if __name__ == "__main__":
    # user_profile = "https://www.goodreads.com/user/show/71341746-tamir-einhorn-salem"
    books = scrape_shelf(
        "https://www.goodreads.com/review/list/71341746-tamir-einhorn-salem?ref=nav_mybooks&shelf=israel-2"
    )
    cont = extract_authors(books)
    cc = generate_country_count(cont)
    df = pd.DataFrame(list(cc.items()), columns=["country", "count"])
    generate_graph(df)
