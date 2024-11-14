from typing import Collection, cast

from pyxtension.streams import stream

from cs5278_assignment_6.live6.data_and_position import DataAndPosition
from cs5278_assignment_6.live7.attribute import Attribute
from cs5278_assignment_6.live9.expr.context import Context
from cs5278_assignment_6.live9.expr.expression import Expression


class AttributeValueExpression(Expression):
    def __init__(self, attribute: str):
        self.attribute = attribute

    def evaluate(self, ctx: Context) -> object:
        data: object = cast(DataAndPosition, ctx.get_target()).get_data()

        attrs: Collection[Attribute] = ctx.get_attributes_strategy().get_attributes(data)

        value_list = stream(attrs).filter(
            lambda a: a.get_name() == self.attribute
        ).map(lambda a: a.get_value()).to_list()

        return value_list[0] if value_list else None
