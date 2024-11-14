from abc import ABC, abstractmethod

from cs5278_assignment_6.live6.iterable_geo_hash import IterableGeoHash
from cs5278_assignment_6.live6.iterable_geo_hash import IterableGeoHashImplementation
from cs5278_assignment_6.live6.geo_hash import GeoHash


class IterableGeoHashFactory(ABC):
    """
    @TODO

    You will need to create an implementation of this
    interface that knows how to create your new GeoHash objects.
    """

    @staticmethod
    @abstractmethod
    def with_coordinates(lat: float, lon: float, bits_of_precision: int) -> IterableGeoHash:
        # first calculate geo hash and then put in this
        raise NotImplementedError

class IterableGeoHashConcreteFactory(IterableGeoHashFactory):
    def create(self, bits) -> IterableGeoHash:
        return IterableGeoHashImplementation(bits)
    def with_coordinates(self, lat: float, lon: float, bits_of_precision: int) -> IterableGeoHash:
        igh = self.create(GeoHash.geo_hash(lat, lon, bits_of_precision))
        return igh
