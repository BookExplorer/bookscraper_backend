from neomodel import (
    StructuredNode,
    StringProperty,
    IntegerProperty,
    UniqueIdProperty,
    RelationshipTo,
    One,
    ZeroOrOne,
)


# TODO: This has no constraints and so we need to deal with them elsewhere.
class Country(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)
    regions = RelationshipTo("Region", "CONTAINS")
    cities = RelationshipTo("City", "CONTAINS")


class Region(StructuredNode):
    # This is states or counties or whatever.
    uid = UniqueIdProperty()
    name = StringProperty(required=True)
    country = RelationshipTo(Country, "WITHIN", cardinality=One)


class City(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(required=True)
    # If a region exists
    region = RelationshipTo(Region, "WITHIN", cardinality=ZeroOrOne)
    country = RelationshipTo(Country, "WITHIN", cardinality=ZeroOrOne)


class Author(StructuredNode):
    uid = UniqueIdProperty()
    goodreads_id = StringProperty(unique_index=True)
    goodreads_link = StringProperty()
    name = StringProperty(required=True)
    birth_city = RelationshipTo(City, "BORN_IN", cardinality=ZeroOrOne)
    lived_in = RelationshipTo(City, "LIVED_IN")
