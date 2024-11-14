from cs5278_assignment_6.live9.abstract_syntax_tree.abstract_syntax_tree_visitor import AbstractSyntaxTreeVisitor
from cs5278_assignment_6.live9.abstract_syntax_tree.node import Node


class LiteralNode(Node):
    def __init__(self, value: str):
        self.value = value

    def get_value(self) -> str:
        return self.value

    def set_value(self, value: str) -> None:
        self.value = value

    def accept(self, visitor: AbstractSyntaxTreeVisitor) -> None:
        visitor.visit(self)
