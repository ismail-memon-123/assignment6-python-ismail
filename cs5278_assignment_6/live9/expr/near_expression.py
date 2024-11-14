from typing import TypeVar

from pyxtension.streams import stream

from cs5278_assignment_6.live6.data_and_position import DataAndPosition
from cs5278_assignment_6.live6.position import Position
from cs5278_assignment_6.live9.expr.context import Context
from cs5278_assignment_6.live9.expr.expression import Expression

T = TypeVar("T")


class NearExpression(Expression[T, stream[DataAndPosition[T]]]):
    def __init__(self):
        self.left_child: Expression[T, float] = None
        self.middle_child: Expression[T, float] = None
        self.right_child: Expression[T, float] = None

    def get_left_child(self) -> Expression[T, float]:
        return self.left_child

    def set_left_child(self, left_child: Expression[T, float]) -> None:
        self.left_child = left_child

    def get_middle_child(self) -> Expression[T, float]:
        return self.middle_child

    def set_middle_child(self, middle_child: Expression[T, float]) -> None:
        self.middle_child = middle_child

    def get_right_child(self) -> Expression[T, float]:
        return self.right_child

    def set_right_child(self, right_child: Expression[T, float]) -> None:
        self.right_child = right_child

    def evaluate(self, ctx: Context[T]) -> stream[DataAndPosition[T]]:
        return stream(ctx.get_db().nearby(Position.with_coordinates(
            self.left_child.evaluate(ctx), self.middle_child.evaluate(ctx)
        ), int(self.right_child.evaluate(ctx))))
