from typing import TypeVar, Generic

from cs5278_assignment_6.live9.expr.context import Context
from cs5278_assignment_6.live9.expr.expression import Expression

T = TypeVar("T")


class AndExpression(Generic[T], Expression[T, bool]):
    def __init__(self):
        self.left_child: Expression[T, bool] = None
        self.right_child: Expression[T, bool] = None

    def get_left_child(self) -> Expression[T, bool]:
        return self.left_child

    def set_left_child(self, left_child: Expression[T, bool]) -> None:
        self.left_child = left_child

    def get_right_child(self) -> Expression[T, bool]:
        return self.right_child

    def set_right_child(self, right_child: Expression[T, bool]) -> None:
        self.right_child = right_child

    def evaluate(self, ctx: Context[T]) -> bool:
        return self.left_child.evaluate(ctx) and self.right_child.evaluate(ctx)

class LExpression(Generic[T], Expression[T, bool]):
    def __init__(self):
        pass

    def evaluate(self, ctx: Context[T]) -> bool:
        pass
