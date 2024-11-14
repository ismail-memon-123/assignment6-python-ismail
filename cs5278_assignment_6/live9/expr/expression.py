from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from cs5278_assignment_6.live9.expr.context import Context

T = TypeVar("T")
R = TypeVar("R")


class Expression(ABC, Generic[T, R]):
    @staticmethod
    @abstractmethod
    def evaluate(ctx: Context[T]) -> R:
        raise NotImplementedError
