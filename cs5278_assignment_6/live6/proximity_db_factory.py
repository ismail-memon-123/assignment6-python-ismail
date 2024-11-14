from typing import TypeVar, Generic

from cs5278_assignment_6.live6.proximity_db import ProximityDB, ProximityDBImplementation

T = TypeVar("T")


class ProximityDBFactory(Generic[T]):
    @staticmethod
    def create(bits: int) -> ProximityDB[T]:
        """
        @TODO

        Fill this in to create one of your implementations
        """

        return ProximityDBImplementation(bits)
