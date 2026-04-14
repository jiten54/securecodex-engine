import ast
import os
from typing import List

class ObfuscationContext:
    def __init__(self, config: dict):
        self.config = config
        self.renames = {}
        self.strings = {}
        self.metadata = {}

class BaseTransformation(ast.NodeTransformer):
    def __init__(self, context: ObfuscationContext):
        self.context = context

    def transform(self, tree: ast.AST) -> ast.AST:
        return self.visit(tree)

class ASTEngine:
    def __init__(self, context: ObfuscationContext):
        self.context = context
        self.transformations: List[BaseTransformation] = []

    def add_transformation(self, transformation_cls):
        self.transformations.append(transformation_cls(self.context))

    def process(self, source_code: str) -> str:
        tree = ast.parse(source_code)
        
        for transformation in self.transformations:
            tree = transformation.transform(tree)
            ast.fix_missing_locations(tree)
            
        return ast.unparse(tree)
