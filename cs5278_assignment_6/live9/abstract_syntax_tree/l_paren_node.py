from cs5278_assignment_6.live9.abstract_syntax_tree.abstract_syntax_tree_visitor import AbstractSyntaxTreeVisitor
from cs5278_assignment_6.live9.abstract_syntax_tree.node import Node


class LParenNode(Node):
    def accept(self, visitor: AbstractSyntaxTreeVisitor) -> None:
        visitor.visit(self)
