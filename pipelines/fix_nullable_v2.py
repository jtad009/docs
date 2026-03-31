import json
import copy

def convert_anyof_null_to_nullable(obj):
    """
    Recursively convert anyOf with null type to nullable property.
    
    Handles two cases:
    1. anyOf with exactly 2 items where one is null -> convert to nullable
    2. anyOf with multiple types including null -> remove null and add nullable
    """
    if isinstance(obj, dict):
        # Check if this is an anyOf
        if 'anyOf' in obj and isinstance(obj['anyOf'], list):
            null_index = None
            non_null_schemas = []
            
            # Find null type and collect others
            for i, item in enumerate(obj['anyOf']):
                if isinstance(item, dict):
                    if item.get('type') == 'null' and len(item) == 1:
                        null_index = i
                    else:
                        non_null_schemas.append(copy.deepcopy(item))
            
            # If we found a null type
            if null_index is not None:
                if len(non_null_schemas) == 1:
                    # Case 1: Only one other type, convert to nullable type
                    obj.clear()
                    obj.update(non_null_schemas[0])
                    obj['nullable'] = True
                elif len(non_null_schemas) > 1:
                    # Case 2: Multiple types, keep anyOf but remove null and add nullable
                    obj['anyOf'] = non_null_schemas
                    obj['nullable'] = True
        
        # Recursively process all values
        for key, value in list(obj.items()):
            if isinstance(value, (dict, list)):
                convert_anyof_null_to_nullable(value)
    
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                convert_anyof_null_to_nullable(item)
    
    return obj

def fix_empty_additional_properties(obj):
    """Convert empty additionalProperties to true"""
    if isinstance(obj, dict):
        if 'additionalProperties' in obj and obj['additionalProperties'] == {}:
            obj['additionalProperties'] = True
        
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                fix_empty_additional_properties(value)
    
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                fix_empty_additional_properties(item)

# Restore from backup and try again
import shutil
shutil.copy('api-reference/openapi.json.backup', 'api-reference/openapi.json')
print("Restored from backup")

# Load the OpenAPI file
with open('api-reference/openapi.json', 'r') as f:
    data = json.load(f)

print("Converting anyOf with null to nullable...")
convert_anyof_null_to_nullable(data)

print("Fixing empty additionalProperties...")
fix_empty_additional_properties(data)

# Write the fixed file
with open('api-reference/openapi.json', 'w') as f:
    json.dump(data, f, indent=2)

print("\nFixed OpenAPI schema!")
print("  - Converted anyOf with null type to nullable: true")
print("  - Fixed empty additionalProperties")
