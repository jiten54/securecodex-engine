import ast
import random
from core.ast_engine import BaseTransformation

class OpaquePredicatesTransformation(BaseTransformation):
    """
    Injects opaque predicates (conditions that are always true/false but look complex).
    """
    def __init__(self, context):
        super().__init__(context)

    def _get_always_true_predicate(self):
        # (x * (x + 1)) % 2 == 0 is always true for integers
        x = random.randint(1, 100)
        return ast.Compare(
            left=ast.BinOp(
                left=ast.BinOp(
                    left=ast.Constant(value=x),
                    op=ast.Mult(),
                    right=ast.BinOp(
                        left=ast.Constant(value=x),
                        op=ast.Add(),
                        right=ast.Constant(value=1)
                    )
                ),
                op=ast.Mod(),
                right=ast.Constant(value=2)
            ),
            ops=[ast.Eq()],
            comparators=[ast.Constant(value=0)]
        )

    def visit_If(self, node):
        # Wrap the if condition with an opaque predicate
        # if (always_true) and original_condition:
        node.test = ast.BoolOp(
            op=ast.And(),
            values=[self._get_always_true_predicate(), node.test]
        )
        self.generic_visit(node)
        return node

    def visit_While(self, node):
        node.test = ast.BoolOp(
            op=ast.And(),
            values=[self._get_always_true_predicate(), node.test]
        )
        self.generic_visit(node)
        return node
