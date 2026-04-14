import ast
import random
from core.ast_engine import BaseTransformation

class AntiDebugTransformation(BaseTransformation):
    """
    Injects anti-debugging and anti-tampering checks.
    """
    def __init__(self, context):
        super().__init__(context)

    def _inject_checks(self, node):
        # Check for debugger using sys.gettrace()
        check_code = """
def _0x_check_env():
    import sys
    if sys.gettrace() is not None:
        # Debugger detected!
        # We can exit or behave differently
        import os
        os._exit(1)
"""
        check_ast = ast.parse(check_code).body[0]
        # Rename the check function
        check_ast.name = f"_0x{random.randint(1000, 9999)}_verify"
        
        if isinstance(node, ast.Module):
            node.body.insert(0, check_ast)
            # Call the check at the start
            node.body.insert(1, ast.Expr(value=ast.Call(
                func=ast.Name(id=check_ast.name, ctx=ast.Load()),
                args=[],
                keywords=[]
            )))
        return node

    def visit_Module(self, node):
        self.generic_visit(node)
        return self._inject_checks(node)
