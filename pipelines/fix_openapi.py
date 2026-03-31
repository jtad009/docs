import json
import copy

def fix_empty_schemas(obj, path=''):
    """Recursively fix empty schemas in the OpenAPI document"""
    if isinstance(obj, dict):
        # Fix empty properties object by adding additionalProperties: true
        # This is common for metadata fields
        if 'properties' in obj and obj.get('properties') == {} and obj.get('type') == 'object':
            # Check if this is in a response path
            if '/responses/' in path and '/204/' in path:
                # For 204 responses, they should not have content
                # We'll handle this at the response level
                pass
            else:
                # For other cases like metadata, add additionalProperties
                obj['additionalProperties'] = True
        
        # Recurse into nested objects
        for key, value in list(obj.items()):
            new_path = f"{path}/{key}" if path else key
            fix_empty_schemas(value, new_path)
    
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            fix_empty_schemas(item, f"{path}[{i}]")

def remove_204_content(paths_obj):
    """Remove content from 204 No Content responses"""
    for path_key, path_item in paths_obj.items():
        if isinstance(path_item, dict):
            for method_key, method_item in path_item.items():
                if isinstance(method_item, dict) and 'responses' in method_item:
                    responses = method_item['responses']
                    if '204' in responses and isinstance(responses['204'], dict):
                        # 204 responses should not have content
                        if 'content' in responses['204']:
                            del responses['204']['content']
                        # Keep only description
                        if 'description' not in responses['204']:
                            responses['204']['description'] = 'No Content'

# Load the OpenAPI file
with open('api-reference/openapi.json', 'r') as f:
    data = json.load(f)

# Make a backup
with open('api-reference/openapi.json.backup', 'w') as f:
    json.dump(data, f, indent=2)

print("Created backup: openapi.json.backup")

# Fix empty schemas
fix_empty_schemas(data)

# Remove content from 204 responses
if 'paths' in data:
    remove_204_content(data['paths'])

# Write the fixed file
with open('api-reference/openapi.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Fixed OpenAPI schema!")
print("\nFixed issues:")
print("  - Added additionalProperties: true to empty schema objects")
print("  - Removed content from 204 No Content responses")
