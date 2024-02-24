from goodreads_scraper.scrape import process_profile
from typing import Dict, List
from collections import Counter
from utils import scrape_gr_author


def extract_authors(books: List[Dict[str, str]]) -> Counter:
    author_tuples = [(book["author_id"], book["author_link"]) for book in books]
    author_tuple_counts = Counter(author_tuples)
    return author_tuple_counts


if __name__ == "__main__":
    user_profile = "https://www.goodreads.com/user/show/71341746-tamir-einhorn-salem"
    books = process_profile(user_profile)
    cont = extract_authors(books)
    author_info_dict = {}
    for (author_id, author_link), count in cont.items():
        birthplace = scrape_gr_author(author_link)  # Scrape the birthplace
        author_info_dict[(author_id, author_link)] = {
            "count": count,
            "birthplace": birthplace,
        }
    print(2)
