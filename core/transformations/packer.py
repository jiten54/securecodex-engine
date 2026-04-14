import ast
import base64
import zlib
import random
import string
from core.ast_engine import BaseTransformation

class Packer(BaseTransformation):
    """
    Code Packing:
    Bundles the entire obfuscated code into an encoded blob and loads it dynamically.
    """
    def __init__(self, context):
        super().__init__(context)

    def transform(self, tree: ast.AST) -> ast.AST:
        source = ast.unparse(tree)
        
        # Multi-layer packing
        compressed = zlib.compress(source.encode())
        encoded = base64.b64encode(compressed).decode()
        
        # Rot13 or simple XOR for extra layer
        def rot13(s):
            return "".join([chr((ord(c) - 97 + 13) % 26 + 97) if 'a' <= c <= 'z' else 
                           chr((ord(c) - 65 + 13) % 26 + 65) if 'A' <= c <= 'Z' else c for c in s])
        
        packed_data = rot13(encoded)
        
        v_data = "_0x" + "".join(random.choice(string.ascii_lowercase) for _ in range(6))
        v_decode = "_0x" + "".join(random.choice(string.ascii_lowercase) for _ in range(6))
        
        loader = f"""
import base64, zlib
{v_data} = "{packed_data}"
def {v_decode}(s):
    return "".join([chr((ord(c) - 97 + 13) % 26 + 97) if 'a' <= c <= 'z' else 
                   chr((ord(c) - 65 + 13) % 26 + 65) if 'A' <= c <= 'Z' else c for c in s])
exec(zlib.decompress(base64.b64decode({v_decode}({v_data}))))
"""
        return ast.parse(loader)
