import ast
import marshal
import base64
import zlib
import random
import string
from core.ast_engine import BaseTransformation

class BytecodeObfuscator(BaseTransformation):
    """
    Extreme-level Bytecode Obfuscation.
    Compiles the AST into a code object, serializes, compresses, 
    and wraps it in a multi-stage loader.
    """
    def __init__(self, context):
        super().__init__(context)

    def transform(self, tree: ast.AST) -> ast.AST:
        # 1. Convert AST to source and then to a code object
        # We use 'exec' mode for the whole module
        source = ast.unparse(tree)
        try:
            code_obj = compile(source, '<obfuscated>', 'exec')
        except Exception as e:
            # Fallback or error handling
            return tree

        # 2. Serialize the code object
        serialized = marshal.dumps(code_obj)
        
        # 3. Apply a layer of encryption/obfuscation to the bytes
        key = random.randint(1, 255)
        obfuscated_bytes = bytes([b ^ key for b in serialized])
        
        # 4. Compress
        compressed = zlib.compress(obfuscated_bytes)
        
        # 5. Base64 encode
        encoded = base64.b64encode(compressed).decode()

        # 6. Generate a polymorphic loader
        # We randomize the variable names in the loader itself
        v_marshal = self._rand_name()
        v_base64 = self._rand_name()
        v_zlib = self._rand_name()
        v_data = self._rand_name()
        v_key = self._rand_name()
        v_decoded = self._rand_name()

        loader_code = f"""
import marshal as {v_marshal}, base64 as {v_base64}, zlib as {v_zlib}
{v_data} = "{encoded}"
{v_key} = {key}
{v_decoded} = {v_marshal}.loads(bytes([_b ^ {v_key} for _b in {v_zlib}.decompress({v_base64}.b64decode({v_data}))]))
exec({v_decoded})
"""
        return ast.parse(loader_code)

    def _rand_name(self):
        return "_0x" + "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
