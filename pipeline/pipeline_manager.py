from core.ast_engine import ASTEngine, ObfuscationContext
from core.transformations.rename import RenameTransformation
from core.transformations.string_encrypt import StringEncryptTransformation
from core.transformations.control_flow import ControlFlowTransformation
from core.transformations.opaque_predicates import OpaquePredicatesTransformation
from core.transformations.anti_debug import AntiDebugTransformation
from core.transformations.dead_code import DeadCodeTransformation
from core.transformations.function_split import FunctionSplitTransformation
from core.transformations.import_obfuscation import ImportObfuscationTransformation
from core.transformations.bytecode_engine import BytecodeObfuscator
from core.transformations.virtualizer import Virtualizer
from core.transformations.runtime_guard import RuntimeGuard
from core.transformations.packer import Packer

class PipelineManager:
    TRANSFORMATION_MAP = {
        "rename": RenameTransformation,
        "string_encrypt": StringEncryptTransformation,
        "control_flow": ControlFlowTransformation,
        "opaque_predicates": OpaquePredicatesTransformation,
        "anti_debug": AntiDebugTransformation,
        "dead_code": DeadCodeTransformation,
        "function_split": FunctionSplitTransformation,
        "import_obfuscation": ImportObfuscationTransformation,
        "bytecode": BytecodeObfuscator,
        "virtualizer": Virtualizer,
        "runtime_guard": RuntimeGuard,
        "packer": Packer,
    }

    LEVEL_CONFIGS = {
        "low": ["rename"],
        "medium": ["rename", "string_encrypt", "import_obfuscation"],
        "high": ["rename", "string_encrypt", "import_obfuscation", "control_flow", "opaque_predicates", "dead_code"],
        "extreme": [
            "rename", 
            "string_encrypt", 
            "import_obfuscation", 
            "control_flow", 
            "opaque_predicates", 
            "dead_code", 
            "anti_debug", 
            "function_split",
            "runtime_guard",
            "virtualizer",
            "bytecode",
            "packer"
        ],
    }

    def __init__(self, config: dict):
        self.config = config
        self.level = config.get("level", "medium")
        self.steps = config.get("steps", self.LEVEL_CONFIGS.get(self.level, ["rename"]))

    def run(self, source_code: str) -> str:
        context = ObfuscationContext(self.config)
        engine = ASTEngine(context)

        for step in self.steps:
            if step in self.TRANSFORMATION_MAP:
                engine.add_transformation(self.TRANSFORMATION_MAP[step])
            else:
                print(f"Warning: Transformation '{step}' not found.")

        return engine.process(source_code)
