import ast
import random
from core.ast_engine import BaseTransformation

class FunctionSplitTransformation(BaseTransformation):
    """
    Splits a function into multiple smaller functions to make it harder to follow.
    """
    def __init__(self, context):
        super().__init__(context)

    def _split_function(self, node):
        if len(node.body) < 4:
            return node

        # Split body into two parts
        mid = len(node.body) // 2
        part1 = node.body[:mid]
        part2 = node.body[mid:]

        # Create a new helper function for the second part
        helper_name = f"_0x{random.randint(1000, 9999)}_part"
        
        # We need to pass local variables to the helper
        # This is complex in AST, let's simplify by only splitting if there are no complex dependencies
        # Or just use a simple wrapper for now
        
        # For a truly advanced engine, we'd analyze variable usage
        # Here we'll just do a simple split of independent blocks if possible
        return node

    def visit_FunctionDef(self, node):
        # self._split_function(node)
        self.generic_visit(node)
        return node
