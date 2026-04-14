import ast
import base64
import random
import string
from core.ast_engine import BaseTransformation

class StringEncryptTransformation(BaseTransformation):
    """
    Multi-layer string encryption (XOR + Base64).
    Injects a dynamic decoder function into the AST.
    """
    def __init__(self, context):
        super().__init__(context)
        self.key = ''.join(random.choice(string.ascii_letters) for _ in range(16))
        self.decoder_name = f"_0x{random.randint(1000, 9999)}_decode"
        self.decoder_injected = False

    def _xor_encrypt(self, data: str, key: str) -> str:
        return "".join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))

    def _inject_decoder(self, node):
        # Create a decoder function:
        # def decoder(data, key):
        #     import base64
        #     decoded = base64.b64decode(data).decode()
        #     return "".join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(decoded))
        
        decoder_code = f"""
def {self.decoder_name}(data, key):
    import base64
    d = base64.b64decode(data).decode()
    return "".join(chr(ord(c) ^ ord(key[i % len(d)])) for i, c in enumerate(d))
"""
        decoder_ast = ast.parse(decoder_code).body[0]
        if isinstance(node, ast.Module):
            node.body.insert(0, decoder_ast)
            self.decoder_injected = True
        return node

    def visit_Module(self, node):
        self.generic_visit(node)
        return self._inject_decoder(node)

    def visit_Constant(self, node):
        if isinstance(node.value, str) and len(node.value) > 0:
            # Skip docstrings (simplified check)
            encrypted = self._xor_encrypt(node.value, self.key)
            b64_encrypted = base64.b64encode(encrypted.encode()).decode()
            
            # Replace string with a call to the decoder
            # decoder_name(b64_encrypted, key)
            new_node = ast.Call(
                func=ast.Name(id=self.decoder_name, ctx=ast.Load()),
                args=[
                    ast.Constant(value=b64_encrypted),
                    ast.Constant(value=self.key)
                ],
                keywords=[]
            )
            return new_node
        return node
