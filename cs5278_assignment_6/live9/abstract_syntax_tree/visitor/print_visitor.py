from multimethod import multimethod

from cs5278_assignment_6.live9.abstract_syntax_tree.abstract_syntax_tree_visitor import AbstractSyntaxTreeVisitor
from cs5278_assignment_6.live9.abstract_syntax_tree.expression_node import ExpressionNode
from cs5278_assignment_6.live9.abstract_syntax_tree.l_paren_node import LParenNode
from cs5278_assignment_6.live9.abstract_syntax_tree.literal_node import LiteralNode
from cs5278_assignment_6.live9.abstract_syntax_tree.r_paren_node import RParenNode
from cs5278_assignment_6.live9.expr.expression import Expression
from cs5278_assignment_6.live9.expr.attribute_value_expression import AttributeValueExpression
from cs5278_assignment_6.live9.expr.find_expression import FindExpression
from cs5278_assignment_6.live9.expr.and_expression import AndExpression, LExpression
from cs5278_assignment_6.live9.expr.greater_than_expression import GreaterThanExpression
from cs5278_assignment_6.live9.expr.less_than_expression import LessThanExpression
from cs5278_assignment_6.live9.expr.near_expression import NearExpression
from cs5278_assignment_6.live9.expr.number_expression import NumberExpression
from cs5278_assignment_6.live9.expr.where_expression import WhereExpression
from collections import deque


class PrintVisitor(AbstractSyntaxTreeVisitor):
    def __init__(self):
        self.indent: str = ""

    def increase_indent(self) -> None:
        self.indent += "  "

    def decrease_indent(self) -> None:
        self.indent = self.indent[:len(self.indent) - 2]

    @multimethod
    def visit(self, expression_node: ExpressionNode) -> None:
        print(f"{self.indent}ExpressionNode")

    @multimethod
    def visit(self, literal_node: LiteralNode) -> None:
        print(f"{self.indent}LiteralNode {literal_node.get_value()}")

    @multimethod
    def visit(self, l_paren_node: LParenNode) -> None:
        self.increase_indent()
        print(f"{self.indent}LParenNode (")

    @multimethod
    def visit(self, r_paren_node: RParenNode) -> None:
        print(f"{self.indent}RParenNode )")
        self.decrease_indent()

class GenerateVisitor(AbstractSyntaxTreeVisitor):
    def __init__(self):
        self.indent: str = ""
        self.stack = deque()

    def get_final_expression(self) -> Expression:
        # Retrieve the final assembled expression (FindExpression)
        return self.stack.pop() if self.stack else None

    @multimethod
    def visit(self, expression_node: ExpressionNode) -> None:
        print("HERE1")
        pass

    @multimethod
    def visit(self, literal_node: LiteralNode) -> None:
        literal_value = literal_node.get_value()
        print("HERE2")
        print(literal_value)
        
        # Detect keywords to push corresponding expressions, initialize them with None (find only)
        if literal_value == "find":
            self.stack.append(FindExpression(None, None))
            print("actaully put")
        elif literal_value == "near":
            self.stack.append(NearExpression())
        elif literal_value == "where":
            self.stack.append(WhereExpression())
        elif literal_value == "and":
            self.stack.append(AndExpression())
        elif literal_value == ">":
            self.stack.append(GreaterThanExpression())
        elif literal_value == "<":
            self.stack.append(LessThanExpression())
        elif isinstance(literal_value, str) and literal_value.startswith(":"):
            # Attribute reference like `:height`
            attribute = literal_value[1:]  # Remove ':' to get the attribute name
            self.stack.append(AttributeValueExpression(attribute))
        else:
            # Literal numeric values
            self.stack.append(NumberExpression(float(literal_value)))

    @multimethod
    def visit(self, l_paren_node: LParenNode) -> None:
        print("HERE3")
        # Start a new expression, nothing specific to push on '('
        self.stack.append(LExpression())

    @multimethod
    def visit(self, r_paren_node: RParenNode) -> None:
        print("HERE4")
        expr_parts = []
        print("eln stak")
        print(str(len(self.stack)))

        # RParenNode is where we have the undoing of the stack, like in the course ex there was the mult node which popped 2 and then *
        # Here we dont evaluate we just build tree with approprate child fields.
        while self.stack:
            part = self.stack.pop()
            
            # Break if we encounter the start of the LExpression (, which means ()
            if isinstance(part, LExpression):
                break
            expr_parts.append(part)

        # This could also happen at start
        if len(expr_parts) == 0:
            #raise ValueError("Unexpected empty expression; mismatched parentheses or missing components.")
            print("Unexpected empty expression; mismatched parentheses or missing components.")
        else:
            if isinstance(expr_parts[-1], NearExpression) and len(expr_parts) >= 4:
                # Build NearExpression with lat, lon, and precision values
                near_expr = expr_parts.pop()
                near_expr.set_left_child(expr_parts.pop())  # precision
                near_expr.set_middle_child(expr_parts.pop())  # longitude
                near_expr.set_right_child(expr_parts.pop())    # latitude
                print("near children mlg")
                print(near_expr.get_middle_child().number)
                print(near_expr.get_left_child().number)
                print(near_expr.get_right_child().number)
                self.stack.append(near_expr)

            elif isinstance(expr_parts[-1], WhereExpression) and len(expr_parts) >= 2:
                # WhereExpression with filter
                where_expr = expr_parts.pop()
                where_expr.set_filter_expression(expr_parts.pop())  # filter (e.g., GreaterThanExpression)
                print("where exp params")
                print(where_expr.get_filter_expression())
                self.stack.append(where_expr)

            elif isinstance(expr_parts[-1], GreaterThanExpression) and len(expr_parts) >= 3:
                # GreaterThanExpression with two child
                gt_expr = expr_parts.pop()
                gt_expr.set_left_child(expr_parts.pop())
                gt_expr.set_right_child(expr_parts.pop())
                print("gt expre params")
                print(gt_expr.get_right_child())
                print(gt_expr.get_left_child())
                self.stack.append(gt_expr)
            
            elif isinstance(expr_parts[-1], LessThanExpression) and len(expr_parts) >= 3:
                # GreaterThanExpression with two child
                lt_expr = expr_parts.pop()
                lt_expr.set_right_child(expr_parts.pop())
                lt_expr.set_left_child(expr_parts.pop())
                self.stack.append(lt_expr)

            elif isinstance(expr_parts[-1], AndExpression) and len(expr_parts) >= 3:
                # GreaterThanExpression with two child
                and_expr = expr_parts.pop()
                and_expr.set_right_child(expr_parts.pop())
                and_expr.set_left_child(expr_parts.pop())
                self.stack.append(and_expr)

            elif isinstance(expr_parts[-1], FindExpression) and len(expr_parts) >= 3:
                # FindExpression with two fileds where and near
                find_expr = expr_parts.pop()
                #find_expr.where = expr_parts.pop()
                find_expr.near = expr_parts.pop()
                find_expr.where = expr_parts.pop()
                print("confirm find has parameters")
                print(str(find_expr.where.__class__))
                print(str(find_expr.near.__class__))
                self.stack.append(find_expr)

            else:
                print("Problem")