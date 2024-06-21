from neomodel import (
    StructuredNode,
    StringProperty,
    IntegerProperty,
    UniqueIdProperty,
    RelationshipTo,
    One,
    ZeroOrOne,
)


class Country(StructuredNode):
    name = StringProperty(unique_index=True, required=True)


class Region(StructuredNode):
    name = StringProperty(required=True)
    country = RelationshipTo(Country, "WITHIN", cardinality=One)


class City(StructuredNode):
    name = StringProperty(required=True)
    # If a region exists
    region = RelationshipTo(Region, "WITHIN", cardinality=ZeroOrOne)
    country = RelationshipTo(Country, "WITHIN", cardinality=One)


class Author(StructuredNode):
    uid = UniqueIdProperty()
    goodreads_id = StringProperty(unique_index=True)
    name = StringProperty(required=True)
    city = RelationshipTo(City, cardinality=ZeroOrOne)
