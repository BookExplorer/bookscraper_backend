from neomodel import db, StructuredNode
from graph_models import Author, City, Country, Region
from typing import Dict


# TODO: Can this be a single function/factory? 
def city_region_exists(city_name: str, region_name: str) -> bool:
    query = """
    MATCH (c:City)-[:WITHIN]->(r:Region {name: $region_name})
    WHERE c.name = $city_name
    RETURN c
    """
    results, meta = db.cypher_query(
        query, {"city_name": city_name, "region_name": region_name}
    )
    return len(results) > 0


def city_country_exists(city_name: str, country_name: str) -> bool:
    query = """
    MATCH (c:City)-[:WITHIN]->(r:Country {name: $country_name})
    WHERE c.name = $city_name
    RETURN c
    """
    results, meta = db.cypher_query(
        query, {"city_name": city_name, "country_name": country_name}
    )
    return len(results) > 0


def region_country_exists(region_name: str, country_name: str) -> bool:
    query = """
    MATCH (r:Region)-[:WITHIN]->(c:Country {name: $country_name})
    WHERE r.name = $region_name
    RETURN r
    """
    results, meta = db.cypher_query(
        query, {"country_name": country_name, "region_name": region_name}
    )
    return len(results) > 0


@db.transaction
def create_geo_nodes(geo_dict: Dict[str, str]) -> tuple[City, Country, bool, bool]| None:
    """Main function for all geographical node insertions/retrievals and connections.
    Expects a dictionary of geographical attributes, 
    will fetch/create the respective node as needed and connect them if applicable.
    Should only be used internally, for now

    Args:
        geo_dict (Dict[str, str]): Dictionary of geographical attributes.

    Returns:
        City| None: City node for connection with Author node elsewhere.
    """

    # The first node we should create is country, which already has a uniqueness check. All good on this front then.
    c = Country.get_or_create({"name": geo_dict["country"]})
    country_node = c[0]
    # Then, we create the city node.
    city_node, created_city_node = create_or_get_city(geo_dict)
    city_node.save()
    if "region" in geo_dict:
        region_node, created_region_node = create_or_get_region(geo_dict)
        region_node.save()
        if not region_node.country.is_connected(country_node):
            region_node.country.connect(country_node)
        
        # If there is region, then city connects to region:
        if not city_node.region.is_connected(region_node):
            city_node.region.connect(region_node)
    else:
        # If there is no region, city connects to country:
        if not city_node.country.is_connected(country_node):
            city_node.country.connect(country_node)
    return city_node, country_node, created_city_node, created_region_node



def create_or_get_region(geo_dict: Dict[str, str]) -> tuple[Region, bool]:
    """Creates a Region node if and only if it satisfies the validation criteria.

    Args:
        geo_dict (Dict[str, str]): Geographical information.

    Returns:
        Region: The desired region node.
    """
    # Validate constraints
    created = None
    if not region_country_exists(geo_dict["region"], geo_dict["country"],):
        # If this doesn't exist, we shoud create it. But we will connect and then save!!
        region_node = Region(name = geo_dict["region"])
        created = True
    else:
        print(f"The region {geo_dict['region']} already exists within {geo_dict['country']} so we didn't create it.")
        region_node =  Region.nodes.get(name = geo_dict["region"])
        created = False
    return region_node, created


def create_or_get_city(geo_dict: Dict[str, str]) -> tuple[City, bool]:
    """Creates a City node if and only if it satisfies the validation criteria.

    Args:
        geo_dict (Dict[str, str]): Geographical information.

    Returns:
        City: The desired City node.
    """
    # Validate constraints.
    created = None
    if not city_country_exists(geo_dict["city"], geo_dict["country"]) and not city_region_exists(geo_dict["city"], geo_dict.get("region", "")):
        # If this doesn't exist, we shoud create it. But we will connect and then save!!
        city_node = City(name = geo_dict["city"])
        created = True
    else:
        print("This combination for city already exists, so we didn't create it.")
        city_node =  City.nodes.get(name = geo_dict["city"])
        created = False
    return city_node, created


@db.transaction
def create_author(author_dict: Dict[str, str]) -> Author:
    """Unpacks the author dict and creates the Author node.
    This will only match the existing fields in the Author node to fields in the author_dict.
    This ensures that extra fields in the dict won't break creation.

    Args:
        author_dict (Dict[str, str]): Dictionary with author information.

    Returns:
        Author: Created Author node.
    """
    # An author is unique by goodreads ID and that's it so far.
    a = Author(**author_dict)
    a.save()
    return a


def fetch_author_by_gr_id(goodreads_id: int) -> Author:
    """Gets Author node by goodreads id if applicable.

    Args:
        goodreads_id (int): Goodreads id for a specific author.

    Returns:
        Author: Author node with that Goodreads id.
    """
    return Author.nodes.get_or_none(goodreads_id = goodreads_id)


def insert_everything(author_dict: Dict[str, str], geo_dict: Dict[str, str]| None) -> Country| None:
    """Inserts all necessary nodes according to the information received, both the Author node and the geographical nodes.

    Args:
        author_dict (Dict[str, str]): Dictionary with the author information for node creation.
        geo_dict (Dict[str, str] | None): Dictionary with the geographical information, if it exists, for node creation.

    Returns:
        Country| None: If there is a geographical dictionary, return the created/existing Country node.
    """
    author: Author = create_author(author_dict)
    # Create regions if applicable.:
    if geo_dict:
        city, country, _ = create_geo_nodes(geo_dict)
        if not author.birth_city.is_connected(city):
            author.birth_city.connect(city)
        return country
    return None


def create_constraints():
    """Runs list of cypher queries with simple constraints for uniqueness and the like.
    """
    queries = [
        "CREATE CONSTRAINT country_name FOR (country:Country) REQUIRE country.name IS UNIQUE",
        "CREATE CONSTRAINT author_gr_id FOR (author:Author) REQUIRE author.goodreads_id IS UNIQUE"
    ]
    for query in queries:
        try:
            db.cypher_query(query)
        except Exception as e:
            print(f"Error creating constraint: {e}")


def get_author_place(author: Author, desired_entity: str = "Country") -> StructuredNode | None:
    """From an Author node, via the City he was born in, get the node (Region or Country) where he was born.
    Will execute a Cypher query on that Author, so results are not guaranteed.

    Args:
        author (Author): Author node whose birth place we would like.
        desired_entity (str): Name of the node type which we want. Should be either Region or Country for now.

    Returns:
        StructuredNode | None: Maybe this should return the specific types of nodes we could get or None.
    """
    element_id = author.element_id
    query = f'''
    MATCH (a:Author)-[:BORN_IN]->(c:City)-[:WITHIN*]->(co:{desired_entity}) 
    WHERE elementId(a) = $element_id
    RETURN co;
    '''
    results, meta = db.cypher_query(
        query, {"element_id": element_id}, resolve_objects=True
    )
    if results:
        return results[0][0]
    return None

if __name__ == "__main__":
    create_constraints()
    geo_dict = {
        "country": "Brazil",
        "city": "Rio de Janeiro",
        "region": "Rio de Janeiro",
    }
    create_geo_nodes(geo_dict)
