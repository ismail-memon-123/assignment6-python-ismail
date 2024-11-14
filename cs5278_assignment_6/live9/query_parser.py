import re
from typing import List, Iterator

from pyxtension.streams import stream

from cs5278_assignment_6.live9.abstract_syntax_tree.expression_node import ExpressionNode
from cs5278_assignment_6.live9.abstract_syntax_tree.literal_node import LiteralNode
from cs5278_assignment_6.live9.abstract_syntax_tree.node import Node
from cs5278_assignment_6.live9.abstract_syntax_tree.r_paren_node import RParenNode
from cs5278_assignment_6.live9.abstract_syntax_tree.visitor.print_visitor import PrintVisitor


class QueryParser:
    class UnexpectedTokenError(RuntimeError):
        def __init__(self, token: str):
            self.token = token

        def get_token(self) -> str:
            return self.token

    @staticmethod
    def tokenize(input_string: str) -> List[str]:
        return stream(
            re.split("(\\s|(?<=\\))|(?=\\))|(?<=\\()|(?=\\())", input_string)
        ).filter(lambda e: bool(len(e.strip()))).to_list()

    @staticmethod
    def parse_node(tokens: Iterator[str]) -> Node:
        next_token: str = next(tokens)

        if next_token == "(":
            return QueryParser.parse_expression(tokens)
        elif not next_token == ")":
            return LiteralNode(next_token)
        else:
            return RParenNode()

    @staticmethod
    def parse_expression(tokens: Iterator[str]) -> ExpressionNode:
        op: Node = QueryParser.parse_node(tokens)

        arguments: List[Node] = []
        try:
            while True:
                arg: Node = QueryParser.parse_node(tokens)

                if isinstance(arg, RParenNode):
                    break
                else:
                    arguments.append(arg)
        except StopIteration:
            pass

        return ExpressionNode(op, arguments)

    @staticmethod
    def parse(query: str) -> ExpressionNode:
        tokens: Iterator[str] = iter(QueryParser.tokenize(query))

        next(tokens)

        return QueryParser.parse_expression(tokens)

    @staticmethod
    def main() -> None:
        QueryParser.parse("(find (near 90.0 90.0 3) (where (> :height 20))").accept(PrintVisitor())

        print()

        QueryParser.parse(
            "(find " +
            "     (near -45.0 -145.0 2) " +
            "     (where " +
            "          (> :height 8)" +
            "     )" +
            ")"
        ).accept(PrintVisitor())


if __name__ == "__main__":
    QueryParser.main()
