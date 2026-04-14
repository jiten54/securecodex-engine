import ast
import random
from core.ast_engine import BaseTransformation

class DeadCodeTransformation(BaseTransformation):
    """
    Injects dead code (code that never executes).
    """
    def __init__(self, context):
        super().__init__(context)

    def _get_dead_code(self):
        # if False: ...
        # or if 1 == 0: ...
        dead_stmt = ast.If(
            test=ast.Compare(
                left=ast.Constant(value=1),
                ops=[ast.Eq()],
                comparators=[ast.Constant(value=0)]
            ),
            body=[
                ast.Assign(
                    targets=[ast.Name(id=f"_0x{random.randint(1000, 9999)}_dead", ctx=ast.Store())],
                    value=ast.Constant(value=random.randint(1, 1000))
                )
            ],
            orelse=[]
        )
        return dead_stmt

    def visit_FunctionDef(self, node):
        if len(node.body) > 0:
            # Inject dead code at a random position
            pos = random.randint(0, len(node.body))
            node.body.insert(pos, self._get_dead_code())
        self.generic_visit(node)
        return node
