from typing import TypeVar, Dict, Any

from pyxtension.streams import stream

from cs5278_assignment_6.live6.data_and_position import DataAndPosition
from cs5278_assignment_6.live9.expr.context import Context
from cs5278_assignment_6.live9.expr.expression import Expression
from cs5278_assignment_6.live9.expr.near_expression import NearExpression
from cs5278_assignment_6.live9.expr.where_expression import WhereExpression

T = TypeVar("T")


class FindExpression(Expression[T, stream[DataAndPosition[T]]]):
    def __init__(self, near: NearExpression, where: WhereExpression):
        self.near: NearExpression = near
        self.where: WhereExpression = where

    def evaluate(self, ctx: Context[T]) -> stream[DataAndPosition[T]]:
        nearby: stream[DataAndPosition[Dict[str, Any]]] = self.near.evaluate(ctx)
        ctx.set_target(nearby)

        return self.where.evaluate(ctx)
