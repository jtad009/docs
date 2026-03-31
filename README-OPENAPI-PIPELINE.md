# OpenAPI Import Pipeline

Automated pipeline to fix and import OpenAPI specifications into Mintlify documentation.

## Quick Start

```bash
# Make the script executable (first time only)
chmod +x scripts/import-openapi.sh

# Run the full pipeline
./scripts/import-openapi.sh
```

## What It Does

The pipeline automatically:

1. **Fixes OpenAPI compatibility issues**:
   - Converts `"type": "null"` to `nullable: true`
   - Simplifies `anyOf` with null types
   - Merges redundant `allOf` schemas
   - Fixes empty `additionalProperties`

2. **Validates the schema** (optional):
   - Runs Redocly linter to check for issues
   - Continues even if validation has warnings

3. **Generates Mintlify docs**:
   - Creates `.mdx` files for each endpoint
   - Outputs navigation structure for `docs.json`

## Usage

### Basic Usage

```bash
# Fix and import default file (./api-reference/openapi.json)
./scripts/import-openapi.sh

# Fix and import custom file
./scripts/import-openapi.sh path/to/custom-openapi.json
```

### Individual Scripts

#### Python Fixer Only

```bash
# Fix default file
python3 fix-openapi-pipeline.py

# Fix custom file
python3 fix-openapi-pipeline.py input.json output.json

# Fix in place
python3 fix-openapi-pipeline.py api-reference/openapi.json
```

#### Manual Steps

```bash
# 1. Fix schema
python3 fix-openapi-pipeline.py ./api-reference/openapi.json

# 2. Validate (optional)
npx @redocly/cli lint api-reference/openapi.json

# 3. Generate docs
npx @mintlify/scraping@latest openapi-file ./api-reference/openapi.json -o ./api-reference
```

## Integration with Your Workflow

### When You Regenerate OpenAPI Spec

Every time your backend generates a new OpenAPI spec:

```bash
# 1. Copy new spec to your docs repo
cp path/to/new/openapi.json api-reference/openapi.json

# 2. Run the pipeline
./scripts/import-openapi.sh

# 3. Review and commit changes
git add .
git commit -m "Update API documentation"
```

### NPM Scripts (Optional)

Add to your `package.json`:

```json
{
  "scripts": {
    "docs:import": "./scripts/import-openapi.sh",
    "docs:fix": "python3 fix-openapi-pipeline.py",
    "docs:dev": "mintlify dev"
  }
}
```

Then run:

```bash
npm run docs:import
```

### Git Hooks (Advanced)

To automatically fix OpenAPI files before committing, add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
if git diff --cached --name-only | grep -q "openapi.json"; then
    python3 fix-openapi-pipeline.py ./api-reference/openapi.json
    git add ./api-reference/openapi.json
fi
```

## Backup

The Python fixer automatically creates a backup file:
- `openapi.json.backup` - Created before each fix

To restore from backup:

```bash
cp api-reference/openapi.json.backup api-reference/openapi.json
```

## Common Issues Fixed

| Issue | Fix |
|-------|-----|
| `"type": "null"` | → `{"type": "string", "nullable": true}` |
| `anyOf: [{type: "string"}, {type: "null"}]` | → `{type: "string", nullable: true}` |
| `allOf: [<single schema>]` | → Merged into parent |
| `additionalProperties: {}` | → `additionalProperties: true` |

## Troubleshooting

### Python not found

```bash
# Install Python 3 (macOS)
brew install python3

# Verify installation
python3 --version
```

### Permission denied

```bash
# Make script executable
chmod +x scripts/import-openapi.sh
chmod +x fix-openapi-pipeline.py
```

### NPX not found

```bash
# Install Node.js and npm
brew install node

# Verify installation
npx --version
```

## Files

- `fix-openapi-pipeline.py` - Python script to fix OpenAPI issues
- `scripts/import-openapi.sh` - Full pipeline script
- `README-OPENAPI-PIPELINE.md` - This documentation

## Support

Common validation errors and how the pipeline handles them:

- ✅ `must have required property '$ref'` - Fixed by converting type:null
- ✅ `anyOf with null type` - Converted to nullable property
- ✅ `redundant allOf` - Merged into parent schema
- ✅ `empty additionalProperties` - Set to true

If you encounter new errors, the Python script can be easily extended to handle them.
