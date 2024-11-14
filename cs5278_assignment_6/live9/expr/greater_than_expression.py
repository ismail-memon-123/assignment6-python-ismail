from typing import TypeVar, cast

from cs5278_assignment_6.live9.expr.context import Context
from cs5278_assignment_6.live9.expr.expression import Expression

T = TypeVar("T")
Number = TypeVar("Number", int, float)


class GreaterThanExpression(Expression[T, bool]):
    def __init__(self):
        self.left_child: Expression = None
        self.right_child: Expression = None

    def get_left_child(self) -> Expression:
        return self.left_child

    def set_left_child(self, left_child: Expression) -> None:
        self.left_child = left_child

    def get_right_child(self) -> Expression:
        return self.right_child

    def set_right_child(self, right_child: Expression) -> None:
        self.right_child = right_child

    def evaluate(self, ctx: Context[T]) -> bool:
        lhs: Number = cast(Number, self.left_child.evaluate(ctx))
        rhs: Number = cast(Number, self.right_child.evaluate(ctx))

        return float(lhs) > float(rhs)
