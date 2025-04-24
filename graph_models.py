from neomodel import (
    StructuredNode,
    StringProperty,
    FloatProperty,
    RelationshipTo,
    One,
    ZeroOrOne,
)


# TODO: This has no constraints and so we need to deal with them elsewhere.
class Country(StructuredNode): #TODO: Draw out schema and create equivalents in db models

    name = StringProperty(unique_index=True, required=True)
    regions = RelationshipTo("Region", "CONTAINS")
    cities = RelationshipTo("City", "CONTAINS")


class Region(StructuredNode):
    # This is states or counties or whatever.

    name = StringProperty(required=True)
    country = RelationshipTo(Country, "WITHIN", cardinality=One)


class City(StructuredNode):

    name = StringProperty(required=True)
    latitude = FloatProperty()
    longitude = FloatProperty()
    lat_long_string = StringProperty(unique_index = True)
    # If a region exists
    region = RelationshipTo(Region, "WITHIN", cardinality=ZeroOrOne)
    country = RelationshipTo(Country, "WITHIN", cardinality=ZeroOrOne)


class Author(StructuredNode):
    goodreads_id = StringProperty(unique_index=True)
    goodreads_link = StringProperty()
    name = StringProperty(required=True)
    birth_city = RelationshipTo(City, "BORN_IN", cardinality=ZeroOrOne)
    lived_in = RelationshipTo(City, "LIVED_IN")
