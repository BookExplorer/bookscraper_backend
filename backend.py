import geopy.geocoders
from goodreads_scraper.scrape import process_profile, scrape_gr_author
from typing import Dict, List, Union
from collections import Counter
from graph_db import insert_everything, fetch_author_by_gr_id, get_author_place
import pycountry
import cProfile
import pstats
import geopy

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
    for (author_id, author_link, author_name), count in cont.items():
        author_dict = {
            "name": author_name,
            "goodreads_id": author_id,
            "goodreads_link": author_link,
        }
        author = fetch_author_by_gr_id(author_id)
        if author:
            country = get_author_place(author, "Country")
        else:
            birthplace, _ = scrape_gr_author(author_link)  # Scrape the birthplace
            geo_dict = process_birthplace(birthplace)
            country = insert_everything(author_dict, geo_dict)
        if country and country.name in country_counter:
            country_counter[country.name] += count
        elif country:
            country_counter[country.name] = count
    return country_counter


def process_country_count(country_count: Dict[str, int]) -> List[Dict[str, any]]:
    # TODO: Is this necessary?
    # Get a list of all country names using pycountry
    all_countries = [country.name for country in pycountry.countries]

    # Prepare a list to store the results
    complete_data = {}

    # Fill in the count for each country or set it to 0 if not present
    for country in all_countries:
        count = country_count.get(country, 0)  # Get the count or default to 0
        complete_data[country] = count

    return complete_data


def process_birthplace(birthplace: str | None) -> Dict[str, Union[str, int]] | None:
    """Processes the birthplac string from Goodreads if it exists and returns a dictionary with attributes.

    Args:
        birthplace (str | None): String with geographical attributes separated by comma.

    Returns:
        Dict[str, str] | None: Dictionary with at least country and city geographical attributes.
    """
    if birthplace:
        latitude, longitude = get_lat_long_place(birthplace)
        split_birthplace = birthplace.split(",")
        geo_dict = {}
        geo_dict["city"] = split_birthplace[0].strip()
        geo_dict["country"] = split_birthplace[-1].strip()
        if len(split_birthplace) > 2:
            geo_dict["region"] = split_birthplace[1].strip()
        geo_dict["latitude"] = latitude
        geo_dict["longitude"] = longitude
        return geo_dict


def get_lat_long_place(place: str) -> tuple[int, int]:
    geolocator = geopy.geocoders.Nominatim(user_agent="book_explorer")
    location = geolocator.geocode(place, exactly_one= True)
    if location:
        latitude = location.latitude
        longitude = location.longitude
        return latitude, longitude

#TODO: Heres the issue in a nutshell: some birthplaces dont get any response from the above function.
# A few are for stupid reasons, like adding a mandatory palestine to jerusalem, so maybe we could try something like 
# using just city, country if there is a region in the middle but nothing is robust enough
# the question then is what to return as lat long bcuz a default value will mix cities up 
# given latitude and longitude are floats with a lot of precision, we might just go overkill on those and clean up l8r



if __name__ == "__main__":
    user_profile = "https://www.goodreads.com/user/show/71341746-tamir-einhorn-salem"
    books = process_profile(user_profile)
    cont = extract_authors(books)
    cc = generate_country_count(cont)
    df = process_country_count(cc)
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.dump_stats("./profile/my_profile.prof")
