import json

def find_schemas_without_type(obj, path=''):
    """Find schema objects that don't have a 'type' or '$ref' property"""
    issues = []
    if isinstance(obj, dict):
        # Check if this looks like a schema object (has properties or other schema keywords)
        # but doesn't have 'type' or '$ref'
        schema_keywords = ['properties', 'anyOf', 'allOf', 'oneOf', 'items', 'additionalProperties']
        has_schema_keyword = any(k in obj for k in schema_keywords)
        has_type_or_ref = 'type' in obj or '$ref' in obj
        
        # Special check: if it's in a schema context and has schema keywords but no type/$ref
        if 'schema' in path and has_schema_keyword and not has_type_or_ref:
            # Exclude cases where it's just a wrapper with only $ref or only type
            if obj.keys() - {'description', 'default', 'example', 'enum', 'format', 'pattern', 
                            'minLength', 'maxLength', 'minimum', 'maximum', 'required',
                            'nullable', 'deprecated'}:
                issues.append(path)
        
        # Recurse
        for key, value in obj.items():
            new_path = f"{path}/{key}" if path else key
            issues.extend(find_schemas_without_type(value, new_path))
    
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            issues.extend(find_schemas_without_type(item, f"{path}[{i}]"))
    
    return issues

with open('api-reference/openapi.json', 'r') as f:
    data = json.load(f)

issues = find_schemas_without_type(data)
print(f"Found {len(issues)} potential schema issues:")
for issue in issues[:30]:
    print(f"  - {issue}")
