from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cs5278_assignment_6.live9.abstract_syntax_tree.expression_node import ExpressionNode
    from cs5278_assignment_6.live9.abstract_syntax_tree.literal_node import LiteralNode
    from cs5278_assignment_6.live9.abstract_syntax_tree.l_paren_node import LParenNode
    from cs5278_assignment_6.live9.abstract_syntax_tree.r_paren_node import RParenNode


from abc import ABC, abstractmethod

from multimethod import multimethod


class AbstractSyntaxTreeVisitor(ABC):
    @abstractmethod
    @multimethod
    def visit(self, expression_node: "ExpressionNode") -> None:
        raise NotImplementedError

    @abstractmethod
    @multimethod
    def visit(self, literal_node: "LiteralNode") -> None:
        raise NotImplementedError

    @abstractmethod
    @multimethod
    def visit(self, l_paren_node: "LParenNode") -> None:
        raise NotImplementedError

    @abstractmethod
    @multimethod
    def visit(self, r_paren_node: "RParenNode") -> None:
        raise NotImplementedError
