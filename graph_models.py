from neomodel import (
    StructuredNode,
    StringProperty,
    IntegerProperty,
    UniqueIdProperty,
    RelationshipTo,
)


class Country(StructuredNode):
    name = StringProperty(unique_index=True, required=True)


class Region(StructuredNode):
    name = StringProperty(required=True)
    country = RelationshipTo(Country, "WITHIN")


class City(StructuredNode):
    name = StringProperty(required=True)
    # If a region exists
    region = RelationshipTo(Region, "WITHIN")
    country = RelationshipTo(Country, "WITHIN")


class Author(StructuredNode):
    uid = UniqueIdProperty()
    goodreads_id = StringProperty(unique_index=True)
    name = StringProperty(required=True)
    city = RelationshipTo(City)
