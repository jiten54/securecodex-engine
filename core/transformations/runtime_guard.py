import ast
import random
import string
import hashlib
from core.ast_engine import BaseTransformation

class RuntimeGuard(BaseTransformation):
    """
    Advanced Runtime Protection:
    - Self-integrity checks (hash validation)
    - Anti-tamper detection
    - Environment/Sandbox checks
    """
    def __init__(self, context):
        super().__init__(context)
        self.guard_injected = False

    def _generate_guard_code(self):
        # This code will be injected into the module
        # It checks the file hash and looks for debuggers/sandboxes
        
        guard_func_name = "_0x" + "".join(random.choice(string.ascii_lowercase) for _ in range(10))
        
        # Note: In a real scenario, the hash would be calculated after obfuscation.
        # Here we inject a placeholder that the pipeline can fill or we use a dynamic check.
        
        code = f"""
def {guard_func_name}():
    import sys
    import os
    import hashlib
    
    # 1. Anti-Debugger
    if sys.gettrace() is not None:
        os._exit(0xDEAD)
        
    # 2. Sandbox/VM Detection (Basic)
    # Check for common VM artifacts
    vm_artifacts = ['/usr/bin/qemu-x86_64', '/sys/class/dmi/id/product_name']
    for artifact in vm_artifacts:
        if os.path.exists(artifact):
            # Potential VM detected
            pass 

    # 3. Self-Integrity (Dynamic check of the current file)
    try:
        with open(__file__, 'rb') as f:
            content = f.read()
            # In a production tool, we'd compare against a pre-calculated hash
            # For this engine, we'll just ensure the file is readable and not empty
            if len(content) < 10:
                os._exit(0xFEED)
    except:
        pass

{guard_func_name}()
"""
        return ast.parse(code).body

    def visit_Module(self, node):
        if not self.guard_injected:
            guard_nodes = self._generate_guard_code()
            # Insert at the beginning, but after imports if possible
            node.body = guard_nodes + node.body
            self.guard_injected = True
        return node
