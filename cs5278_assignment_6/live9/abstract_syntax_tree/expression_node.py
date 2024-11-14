from typing import List

from cs5278_assignment_6.live9.abstract_syntax_tree.abstract_syntax_tree_visitor import AbstractSyntaxTreeVisitor
from cs5278_assignment_6.live9.abstract_syntax_tree.l_paren_node import LParenNode
from cs5278_assignment_6.live9.abstract_syntax_tree.node import Node
#from cs5278_assignment_6.live9.abstract_syntax_tree.visitor.print_visitor import GenerateVisitor, PrintVisitor
from cs5278_assignment_6.live9.expr.expression import Expression
from cs5278_assignment_6.live9.abstract_syntax_tree.r_paren_node import RParenNode


class ExpressionNode(Node):
    def __init__(self, operation: Node, arguments: List[Node]):
        self.left_parent: Node = LParenNode()
        self.operation: Node = operation
        self.arguments: List[Node] = arguments
        self.right_parent: Node = RParenNode()

    def get_operation(self) -> Node:
        return self.operation

    def set_operation(self, operation: Node) -> None:
        self.operation = operation

    def get_arguments(self) -> List[Node]:
        return self.arguments

    def set_arguments(self, arguments: List[Node]) -> None:
        self.arguments = arguments

    def accept(self, visitor: AbstractSyntaxTreeVisitor) -> None:
        visitor.visit(self)
        self.left_parent.accept(visitor)
        self.operation.accept(visitor)
        for argument in self.arguments:
            argument.accept(visitor)
        self.right_parent.accept(visitor)
