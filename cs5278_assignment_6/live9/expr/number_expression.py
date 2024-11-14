from typing import TypeVar

from cs5278_assignment_6.live9.expr.context import Context
from cs5278_assignment_6.live9.expr.expression import Expression

T = TypeVar("T")


class NumberExpression(Expression[T, float]):
    def __init__(self, number: float):
        self.number = number

    def evaluate(self, obj: Context[T]) -> float:
        return self.number
