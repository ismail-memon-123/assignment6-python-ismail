from typing import TypeVar, Generic

from cs5278_assignment_6.live7.attributes_strategy import AttributesStrategy
from cs5278_assignment_6.live7.proximity_stream_db import ProximityStreamDB

T = TypeVar("T")


class Context(Generic[T]):
    def __init__(self):
        self.target: object = None
        self.db: ProximityStreamDB[T] = None
        self.attributes_strategy: AttributesStrategy = None

    def get_target(self) -> object:
        return self.target

    def set_target(self, target: object) -> None:
        self.target = target

    def get_db(self) -> ProximityStreamDB[T]:
        return self.db

    def set_db(self, db: ProximityStreamDB[T]) -> None:
        self.db = db

    def get_attributes_strategy(self) -> AttributesStrategy:
        return self.attributes_strategy

    def set_attributes_strategy(self, attributes_strategy: AttributesStrategy) -> None:
        self.attributes_strategy = attributes_strategy
