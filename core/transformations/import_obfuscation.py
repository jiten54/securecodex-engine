import ast
import random
from core.ast_engine import BaseTransformation

class ImportObfuscationTransformation(BaseTransformation):
    """
    Obfuscates imports using __import__ and dynamic attribute access.
    """
    def __init__(self, context):
        super().__init__(context)

    def visit_Import(self, node):
        # import os -> os = __import__('os')
        new_nodes = []
        for alias in node.names:
            name = alias.name
            asname = alias.asname if alias.asname else name
            
            # asname = __import__('name')
            new_node = ast.Assign(
                targets=[ast.Name(id=asname, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Name(id='__import__', ctx=ast.Load()),
                    args=[ast.Constant(value=name)],
                    keywords=[]
                )
            )
            new_nodes.append(new_node)
        return new_nodes

    def visit_ImportFrom(self, node):
        # from os import path -> path = __import__('os').path
        module = node.module
        new_nodes = []
        for alias in node.names:
            name = alias.name
            asname = alias.asname if alias.asname else name
            
            # asname = getattr(__import__('module'), 'name')
            new_node = ast.Assign(
                targets=[ast.Name(id=asname, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Name(id='getattr', ctx=ast.Load()),
                    args=[
                        ast.Call(
                            func=ast.Name(id='__import__', ctx=ast.Load()),
                            args=[ast.Constant(value=module)],
                            keywords=[]
                        ),
                        ast.Constant(value=name)
                    ],
                    keywords=[]
                )
            )
            new_nodes.append(new_node)
        return new_nodes
