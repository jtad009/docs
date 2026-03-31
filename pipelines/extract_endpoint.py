import json

# Load the full spec
with open('api-reference/openapi.json', 'r') as f:
    data = json.load(f)

# Create a minimal spec with just the problematic endpoint
minimal_spec = {
    "openapi": "3.0.3",
    "info": {
        "title": "Test API",
        "version": "1.0.0"
    },
    "paths": {
        "/auth/google": data['paths']['/auth/google']
    }
}

# Save it
with open('test-auth-google.json', 'w') as f:
    json.dump(minimal_spec, f, indent=2)

print("Created test-auth-google.json")
