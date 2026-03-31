import json
import copy

def convert_anyof_null_to_nullable(obj):
    """
    Recursively convert anyOf with null type to nullable property.
    
    Converts:
    {
      "anyOf": [
        {"type": "string"},
        {"type": "null"}
      ]
    }
    
    To:
    {
      "type": "string",
      "nullable": true
    }
    """
    if isinstance(obj, dict):
        # Check if this is an anyOf with exactly 2 items where one is {"type": "null"}
        if 'anyOf' in obj and isinstance(obj['anyOf'], list) and len(obj['anyOf']) == 2:
            types = []
            null_found = False
            other_schema = None
            
            for item in obj['anyOf']:
                if isinstance(item, dict):
                    if item.get('type') == 'null' and len(item) == 1:
                        null_found = True
                    elif 'type' in item:
                        other_schema = copy.deepcopy(item)
            
            # If we found exactly one null and one other type, convert it
            if null_found and other_schema:
                # Replace the anyOf with the actual type + nullable
                obj.clear()
                obj.update(other_schema)
                obj['nullable'] = True
                return obj
        
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
