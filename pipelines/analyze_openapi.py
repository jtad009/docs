import json

def find_empty_schemas(obj, path=''):
    issues = []
    if isinstance(obj, dict):
        # Check if this is a schema with empty properties
        if 'properties' in obj and obj.get('properties') == {} and obj.get('type') == 'object':
            issues.append(path)
        # Recurse
        for key, value in obj.items():
            issues.extend(find_empty_schemas(value, f"{path}/{key}" if path else key))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            issues.extend(find_empty_schemas(item, f"{path}[{i}]"))
    return issues

with open('api-reference/openapi.json', 'r') as f:
    data = json.load(f)

issues = find_empty_schemas(data)
print(f"Found {len(issues)} schemas with empty properties:")
for issue in issues[:30]:  # Show first 30
    print(f"  - {issue}")
