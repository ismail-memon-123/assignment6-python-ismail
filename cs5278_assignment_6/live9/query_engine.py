from typing import TypeVar, Dict, Any

from pyxtension.streams import stream

from cs5278_assignment_6.live6.data_and_position import DataAndPosition
from cs5278_assignment_6.live7.attributes_strategy import AttributesStrategy
from cs5278_assignment_6.live7.proximity_stream_db import ProximityStreamDB
from cs5278_assignment_6.live7.proximity_stream_db_factory import ProximityStreamDBFactory
from cs5278_assignment_6.live9.abstract_syntax_tree.expression_node import ExpressionNode
from cs5278_assignment_6.live9.abstract_syntax_tree.visitor.print_visitor import PrintVisitor, GenerateVisitor
from cs5278_assignment_6.live9.expr.attribute_value_expression import AttributeValueExpression
from cs5278_assignment_6.live9.expr.context import Context
from cs5278_assignment_6.live9.expr.expression import Expression
from cs5278_assignment_6.live9.expr.find_expression import FindExpression
from cs5278_assignment_6.live9.expr.greater_than_expression import GreaterThanExpression
from cs5278_assignment_6.live9.expr.near_expression import NearExpression
from cs5278_assignment_6.live9.expr.number_expression import NumberExpression
from cs5278_assignment_6.live9.expr.where_expression import WhereExpression
from cs5278_assignment_6.live9.map_attributes_strategy import MapAttributesStrategy
from cs5278_assignment_6.live9.map_utils import MapUtils
from cs5278_assignment_6.live9.query_parser import QueryParser

T = TypeVar("T")


class QueryEngine:
    @staticmethod
    def execute(db: ProximityStreamDB[T], attrs: AttributesStrategy[T], query_str: str) -> stream[DataAndPosition[T]]:
        root: Expression[T, stream[DataAndPosition[T]]] = QueryEngine.parse_query(query_str)

        ctx: Context = Context()

        ctx.set_attributes_strategy(attrs)
        ctx.set_db(db)

        return root.evaluate(ctx)

    @staticmethod
    def parse_query(query_str: str) -> Expression[T, stream[DataAndPosition[T]]]:
        """
        @TODO

        Implement an AbstractSyntaxTreeVisitor that builds the correct query expression tree for a given AST

        Use your visitor here to return the root expression for the query.

        The structure of the query language is:

        (find
           (near -45.0 -145.0 2)
           (where
              (> :height 8)
            )
         )

        ALL queries will have find, near, and where expressions.
        For simplicity, only > is supported. You can also have
        "and" combining > expressions:

        (find
           (near -45.0 -145.0 2)
           (where
              (and (> :height 8)
                   (> :age 50)
            )
         )

        The third parameter to "near" is the bits of precision.

        Any terms prefixed with ":" are references to an attribute.

        The main(...) method below shows how to build the first query
        above manually using the expression classes.

        The QueryParser code below produces the abstract syntax tree
        for a query string.

        Your job is to write a visitor that traverses the abstract syntax
        tree and constructs the appropriate expressions to implement the
        query.

        To help you figure out the structure of the abstract syntax tree,
        I would recommend putting in a breakpoint after the "raw"
        ExpressionNode is created so that you can see what the tree
        looks like. You can also use the PrintVisitor to dump the
        abstract syntax tree to the console to figure out its structure.

        The main() method below both prints the abstract syntax tree for a
        query and manually constructs the FindExpression that the abstract
        syntax tree would be translated into by your visitor. That is, if your
        visitor was given the abstract syntax tree printed by the main method,
        it would generate a FindExpression equivalent to what is shown in the
        main method.
        """
        print("For debugging")
        print(query_str)
        raw: ExpressionNode = QueryParser.parse(query_str)
        print(raw)
        print(str(len(raw.get_arguments())))
        visitor = GenerateVisitor()
        raw.accept(visitor)
        raw.accept(PrintVisitor())
        print("filter")
        ans = visitor.get_final_expression()
        print(str(ans.where.__class__))
        print(str(ans.near.__class__))
        print(str(ans.where.get_filter_expression()))
        # supposted to return something of type expression, FindExpression is a potential type
        # the strucutre alreayd allows for a good style to be used all the children made in order, u must translate that
        # to the correct type of value.
        return ans

        """
        This will print out the abstract syntax tree.
        raw.accept(PrintVisitor())

        You have to have a QueryVisitor and use it 
        like this to complete the QueryEngine.
        """

        return None

    @staticmethod
    def data(m: Dict[str, Any]) -> DataAndPosition[Dict[str, Any]]:
        class DataAndPositionExtended(DataAndPosition[Dict[str, Any]]):
            @staticmethod
            def get_data() -> Dict[str, Any]:
                return m

            @staticmethod
            def get_latitude() -> float:
                return float(m.get("lat"))

            @staticmethod
            def get_longitude() -> float:
                return float(m.get("lon"))

        return DataAndPositionExtended()

    @staticmethod
    def main() -> None:
        # This is how the abstract syntax tree is generated:
        expr: ExpressionNode = QueryParser.parse(
            "(find " +
            "     (near -45.0 -145.0 2) " +
            "     (where " +
            "          (> :height 8)" +
            "     )" +
            ")"
        )

        # This will print out the tree structure for you to the console
        expr.accept(PrintVisitor())

        print()

        """
        Your visitor should be able to translate the abstract syntax
        tree that you see printed in the console to the equivalent of
        the hand constructed FindExpression below.

        Here is an example of building a FindExpression (query) manually:
        
        The next part is going to be hand-constructing
        the equivalent of this query:
        
        (find
             (near -45.0 -145.0 2)
             (where
                (> :height 8)
            )
        )
        """

        lat: NumberExpression = NumberExpression(-45.0)
        lon: NumberExpression = NumberExpression(-145.0)
        bits: NumberExpression = NumberExpression(2)

        near: NearExpression = NearExpression()
        near.set_left_child(lat)
        near.set_middle_child(lon)
        near.set_right_child(bits)

        where: WhereExpression = WhereExpression()
        av: AttributeValueExpression = AttributeValueExpression("height")
        val: NumberExpression = NumberExpression(8)
        gt: GreaterThanExpression = GreaterThanExpression()
        gt.set_left_child(av)
        gt.set_right_child(val)

        where.set_filter_expression(gt)

        find: FindExpression = FindExpression(near, where)

        # Now, to evaluate the query against a database, we have
        # to create a database and context to execute the query.
        data: DataAndPosition = QueryEngine.data(MapUtils.of(
            ["height", 10.0,
             "age", 32.0,
             "lat", -90.0,
             "lon", -180.0]
        ))

        data2: DataAndPosition = QueryEngine.data(MapUtils.of(
            ["age", 56.0,
             "height", 8.0,
             "lat", -90.0,
             "lon", -180.0]
        ))

        # Replace with your implementation and using a MapAttributesStrategy.
        db: ProximityStreamDB = ProximityStreamDBFactory.create(MapAttributesStrategy(), bits, None)

        db.insert(data)
        db.insert(data2)
        ctx: Context[Dict[str, Any]] = Context()
        ctx.set_attributes_strategy(MapAttributesStrategy())
        ctx.set_db(db)

        # Finally, we can execute the query with the context.
        result: stream[DataAndPosition[Dict[str, any]]] = find.evaluate(ctx)

        # Print the result of the query
        result.for_each(lambda m: print(f"{m.get_latitude()}, {m.get_longitude()} -- {m.get_data()}"))

        # This should produce the same result as the manually created query above.
        result2: stream[DataAndPosition[Dict[str, any]]] = \
            QueryEngine.execute(
                db,
                MapAttributesStrategy(),
                "(find " +
                "     (near -45.0 -145.0 2) " +
                "     (where " +
                "          (> :height 8)" +
                "     )" +
                ")"
            )

        result2.for_each(lambda m: print(f"{m.get_latitude()}, {m.get_longitude()} -- {m.get_data()}"))


if __name__ == "__main__":
    QueryEngine.main()
