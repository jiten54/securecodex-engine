import sys
import argparse
import json
import os
from pipeline.pipeline_manager import PipelineManager

def main():
    parser = argparse.ArgumentParser(description="SecureCodeX Engine - Advanced Code Obfuscation")
    parser.add_argument("file", help="Python file to protect")
    parser.add_argument("--level", choices=["low", "medium", "high", "extreme"], default="medium", help="Obfuscation level")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--config", help="JSON config file")

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)

    with open(args.file, "r") as f:
        source_code = f.read()

    config = {}
    if args.config:
        with open(args.config, "r") as f:
            config = json.load(f)
    
    config["level"] = args.level

    manager = PipelineManager(config)
    try:
        protected_code = manager.run(source_code)
        
        output_path = args.output if args.output else f"protected_{os.path.basename(args.file)}"
        with open(output_path, "w") as f:
            f.write(protected_code)
            
        print(f"Success: Protected code saved to '{output_path}'")
    except Exception as e:
        print(f"Error during obfuscation: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
