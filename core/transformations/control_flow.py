import ast
import random
from core.ast_engine import BaseTransformation

class ControlFlowTransformation(BaseTransformation):
    """
    Control flow flattening using a state machine.
    Converts a block of code into a while loop with a switch-case (if-elif) structure.
    """
    def __init__(self, context):
        super().__init__(context)

    def _flatten_body(self, body):
        if len(body) <= 1:
            return body

        # Assign a state to each statement
        states = list(range(len(body)))
        random.shuffle(states)
        
        # Mapping from original index to state
        idx_to_state = {i: states[i] for i in range(len(body))}
        
        # State variable name
        state_var = f"_0x{random.randint(1000, 9999)}_state"
        
        new_body = []
        # Initial state
        new_body.append(ast.Assign(
            targets=[ast.Name(id=state_var, ctx=ast.Store())],
            value=ast.Constant(value=idx_to_state[0])
        ))
        
        # While loop
        # while state_var != -1:
        loop_body = []
        
        for i, stmt in enumerate(body):
            next_state = idx_to_state[i+1] if i+1 < len(body) else -1
            
            # Update state at the end of the statement
            if isinstance(stmt, (ast.Return, ast.Break, ast.Continue)):
                # These already break control flow, but we might need to handle them
                # For simplicity, we keep them as is
                pass
            else:
                # Add state update to the statement if it's a block, or append it
                state_update = ast.Assign(
                    targets=[ast.Name(id=state_var, ctx=ast.Store())],
                    value=ast.Constant(value=next_state)
                )
                if hasattr(stmt, 'body') and isinstance(stmt.body, list):
                    # This is tricky for nested structures, let's just append for now
                    pass
                
            # Create if state_var == current_state: stmt; state = next_state
            if_stmt = ast.If(
                test=ast.Compare(
                    left=ast.Name(id=state_var, ctx=ast.Load()),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=idx_to_state[i])]
                ),
                body=[stmt, ast.Assign(
                    targets=[ast.Name(id=state_var, ctx=ast.Store())],
                    value=ast.Constant(value=next_state)
                )],
                orelse=[]
            )
            loop_body.append(if_stmt)

        while_loop = ast.While(
            test=ast.Compare(
                left=ast.Name(id=state_var, ctx=ast.Load()),
                ops=[ast.NotEq()],
                comparators=[ast.Constant(value=-1)]
            ),
            body=loop_body,
            orelse=[]
        )
        
        new_body.append(while_loop)
        return new_body

    def visit_FunctionDef(self, node):
        node.body = self._flatten_body(node.body)
        self.generic_visit(node)
        return node

    def visit_Module(self, node):
        # Flattening module level code can be dangerous if there are imports/defs
        # We only flatten functions for now to ensure safety
        self.generic_visit(node)
        return node
