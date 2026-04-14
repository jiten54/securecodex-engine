import ast
import random
import string
from core.ast_engine import BaseTransformation

class RenameTransformation(BaseTransformation):
    """
    AST-based scoped renaming of variables, functions, and classes.
    """
    def __init__(self, context):
        super().__init__(context)
        self.mapping = {}
        self.excluded_names = {'self', 'cls', '__init__', '__main__', 'main'}
        # Add built-ins and common library names to excluded if needed
        
    def _generate_random_name(self, length=12):
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))

    def _get_new_name(self, old_name):
        if old_name in self.excluded_names or old_name.startswith('__'):
            return old_name
        
        if old_name not in self.mapping:
            new_name = f"_0x{self._generate_random_name(8)}"
            self.mapping[old_name] = new_name
            self.context.renames[old_name] = new_name
            
        return self.mapping[old_name]

    def visit_FunctionDef(self, node):
        node.name = self._get_new_name(node.name)
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node):
        node.name = self._get_new_name(node.name)
        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Load, ast.Param)):
            node.id = self._get_new_name(node.id)
        return node

    def visit_arg(self, node):
        node.arg = self._get_new_name(node.arg)
        return node

    def visit_Attribute(self, node):
        # We only rename attributes if they are part of the current scope or we have a way to track them
        # For now, let's be conservative with attributes to avoid breaking external library calls
        self.generic_visit(node)
        return node
