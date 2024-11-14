from abc import ABC, abstractmethod

from cs5278_assignment_6.live9.abstract_syntax_tree.abstract_syntax_tree_visitor import AbstractSyntaxTreeVisitor


class Node(ABC):
    @abstractmethod
    def accept(self, visitor: AbstractSyntaxTreeVisitor) -> None:
        raise NotImplementedError
