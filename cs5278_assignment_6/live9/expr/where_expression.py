from typing import TypeVar, cast

from pyxtension.streams import stream

from cs5278_assignment_6.live6.data_and_position import DataAndPosition
from cs5278_assignment_6.live9.expr.context import Context
from cs5278_assignment_6.live9.expr.expression import Expression

T = TypeVar("T")


class WhereExpression(Expression[T, stream[DataAndPosition[T]]]):
    def __init__(self):
        self.filter_expression: Expression[T, bool] = None

    def get_filter_expression(self) -> Expression[T, bool]:
        return self.filter_expression

    def set_filter_expression(self, filter_expression: Expression[T, bool]) -> None:
        self.filter_expression = filter_expression

    def evaluate(self, ctx: Context[T]) -> stream[DataAndPosition[T]]:
        target: stream[DataAndPosition[T]] = cast(stream[DataAndPosition[T]], ctx.get_target())

        # Python doesn't have *real* support for multi-statement lambdas, so this is used instead.
        def extracted_lambda(e):
            ctx.set_target(e)

            return self.filter_expression.evaluate(ctx)

        return target.filter(lambda e: extracted_lambda(e))
