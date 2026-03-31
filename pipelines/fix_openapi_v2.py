import json
import copy
import shutil

def fix_type_null(obj):
    """Convert standalone type: null to type: string with nullable: true"""
    if isinstance(obj, dict):
        # Check if this has type: "null" directly
        if obj.get('type') == 'null':
            # Replace with nullable string
            obj['type'] = 'string'
            obj['nullable'] = True
        
        # Recurse into nested objects
        for key, value in list(obj.items()):
            if isinstance(value, (dict, list)):
                fix_type_null(value)
    
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                fix_type_null(item)
    
    return obj

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

def fix_redundant_allof(obj):
    """
    Fix allOf that just combines same types with different keywords.
    Convert allOf with same types to a merged single schema.
    """
    if isinstance(obj, dict):
        # Check if this is an allOf
        if 'allOf' in obj and isinstance(obj['allOf'], list):
            # Try to merge all schemas in allOf
            merged = {}
            all_same_type = True
            base_type = None
            
            for item in obj['allOf']:
                if isinstance(item, dict):
                    # Check if all have the same type (or no type)
                    if 'type' in item:
                        if base_type is None:
                            base_type = item['type']
                        elif base_type != item['type']:
                            all_same_type = False
                    
                    # Merge all properties
                    for k, v in item.items():
                        if k == 'type':
                            merged['type'] = v
                        elif k not in merged:
                            merged[k] = v
            
            # If all schemas have the same type, we can safely merge
            if all_same_type and base_type and len(merged) > 0:
                obj.clear()
                obj.update(merged)
        
        # Recursively process all values
        for key, value in list(obj.items()):
            if isinstance(value, (dict, list)):
                fix_redundant_allof(value)
    
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                fix_redundant_allof(item)
    
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

# Restore from backup
shutil.copy('api-reference/openapi.json.backup', 'api-reference/openapi.json')
print("Restored from backup")

# Load the OpenAPI file
with open('api-reference/openapi.json', 'r') as f:
    data = json.load(f)

print("Fixing standalone type: null...")
fix_type_null(data)

print("Converting anyOf with null to nullable...")
convert_anyof_null_to_nullable(data)

print("Fixing redundant allOf...")
fix_redundant_allof(data)

print("Fixing empty additionalProperties...")
fix_empty_additional_properties(data)

# Save the fixed OpenAPI file
with open('api-reference/openapi.json', 'w') as f:
    json.dump(data, f, indent=2)

print("\nFixed OpenAPI schema!")
print("  - Fixed standalone type: null")
print("  - Converted anyOf with null type to nullable: true")
print("  - Merged redundant allOf schemas")
print("  - Fixed empty additionalProperties")
