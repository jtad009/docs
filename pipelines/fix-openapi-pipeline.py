#!/usr/bin/env python3
"""
OpenAPI Schema Fixer Pipeline
Automatically fixes common OpenAPI 3.0.x compatibility issues for Mintlify imports.

Usage:
    python fix-openapi-pipeline.py [input_file] [output_file]
    python fix-openapi-pipeline.py  # Uses default: ./api-reference/openapi.json
"""

import json
import sys
import os
from typing import Any, Dict, List

class OpenAPIFixer:
    def __init__(self):
        self.changes_made = []
    
    def fix_schema(self, obj: Any, path: str = "root") -> Any:
        """Recursively fix OpenAPI schema issues."""
        if isinstance(obj, dict):
            obj = self.fix_type_null(obj, path)
            obj = self.fix_anyof_null(obj, path)
            obj = self.fix_allof_redundant(obj, path)
            obj = self.fix_empty_additional_properties(obj, path)
            
            # Recursively process nested objects
            for key, value in obj.items():
                obj[key] = self.fix_schema(value, f"{path}.{key}")
        
        elif isinstance(obj, list):
            return [self.fix_schema(item, f"{path}[{i}]") for i, item in enumerate(obj)]
        
        return obj
    
    def fix_type_null(self, obj: Dict, path: str) -> Dict:
        """Fix standalone 'type': 'null' - convert to nullable string."""
        if obj.get("type") == "null":
            self.changes_made.append(f"Fixed standalone type:null at {path}")
            return {"type": "string", "nullable": True}
        return obj
    
    def fix_anyof_null(self, obj: Dict, path: str) -> Dict:
        """Convert anyOf with null type to nullable property."""
        if "anyOf" in obj:
            any_of = obj["anyOf"]
            
            # Check if anyOf contains a null type
            has_null = any(
                schema.get("type") == "null" or 
                (schema.get("type") == "string" and schema.get("nullable") is True)
                for schema in any_of
            )
            
            if has_null:
                # Filter out null schemas
                non_null_schemas = [
                    schema for schema in any_of 
                    if schema.get("type") != "null" and 
                    not (schema.get("type") == "string" and schema.get("nullable") is True)
                ]
                
                if len(non_null_schemas) == 1:
                    # Replace anyOf with the single non-null schema and add nullable
                    result = non_null_schemas[0].copy()
                    result["nullable"] = True
                    
                    # Preserve other properties from original object
                    for key in obj:
                        if key != "anyOf":
                            result[key] = obj[key]
                    
                    self.changes_made.append(f"Converted anyOf with null to nullable at {path}")
                    return result
        
        return obj
    
    def fix_allof_redundant(self, obj: Dict, path: str) -> Dict:
        """Merge redundant allOf with single schema."""
        if "allOf" in obj and len(obj["allOf"]) == 1:
            # Merge the allOf single schema with parent properties
            all_of_schema = obj["allOf"][0]
            result = all_of_schema.copy()
            
            # Preserve other properties from original object
            for key in obj:
                if key != "allOf":
                    if key in result:
                        # Merge properties if both have them
                        if key == "properties" and isinstance(result[key], dict):
                            result[key] = {**result[key], **obj[key]}
                        elif key == "required" and isinstance(result[key], list):
                            result[key] = list(set(result[key] + obj[key]))
                    else:
                        result[key] = obj[key]
            
            self.changes_made.append(f"Merged redundant allOf at {path}")
            return result
        
        return obj
    
    def fix_empty_additional_properties(self, obj: Dict, path: str) -> Dict:
        """Fix empty additionalProperties objects."""
        if "additionalProperties" in obj:
            if obj["additionalProperties"] == {}:
                obj["additionalProperties"] = True
                self.changes_made.append(f"Fixed empty additionalProperties at {path}")
        
        return obj
    
    def process_file(self, input_file: str, output_file: str) -> bool:
        """Process OpenAPI file and fix all issues."""
        try:
            # Read input file
            print(f"📖 Reading {input_file}...")
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Fix the schema
            print("🔧 Fixing OpenAPI schema issues...")
            fixed_data = self.fix_schema(data)
            
            # Write output file
            print(f"💾 Writing to {output_file}...")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(fixed_data, f, indent=2, ensure_ascii=False)
            
            # Report changes
            print(f"\n✅ Done! Made {len(self.changes_made)} fixes:")
            
            # Group changes by type
            change_types = {}
            for change in self.changes_made:
                change_type = change.split(" at ")[0]
                change_types[change_type] = change_types.get(change_type, 0) + 1
            
            for change_type, count in change_types.items():
                print(f"   • {change_type}: {count}")
            
            return True
            
        except FileNotFoundError:
            print(f"❌ Error: File '{input_file}' not found")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON in '{input_file}': {e}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


def main():
    # Default paths
    default_input = "./api-reference/openapi.json"
    default_output = "./api-reference/openapi.json"
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else input_file
    else:
        input_file = default_input
        output_file = default_output
    
    # Confirm overwrite if same file
    if input_file == output_file:
        print(f"⚠️  Will overwrite {input_file}")
    
    # Create backup
    if os.path.exists(input_file):
        backup_file = f"{input_file}.backup"
        print(f"💾 Creating backup at {backup_file}")
        with open(input_file, 'r') as src, open(backup_file, 'w') as dst:
            dst.write(src.read())
    
    # Process file
    fixer = OpenAPIFixer()
    success = fixer.process_file(input_file, output_file)
    
    if success:
        print(f"\n🎉 OpenAPI file fixed successfully!")
        print(f"\nNext steps:")
        print(f"   npx @mintlify/scraping@latest openapi-file {output_file} -o ./api-reference")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
