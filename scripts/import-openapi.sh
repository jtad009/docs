#!/bin/bash
# OpenAPI Import Pipeline
# Fixes and imports OpenAPI spec into Mintlify docs

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

OPENAPI_FILE="${1:-./api-reference/openapi.json}"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   OpenAPI Import Pipeline for Mintlify${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Step 1: Fix OpenAPI schema
echo -e "${YELLOW}Step 1/3:${NC} Fixing OpenAPI schema compatibility..."
python3 fix-openapi-pipeline.py "$OPENAPI_FILE"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to fix OpenAPI schema${NC}"
    exit 1
fi

# Step 2: Validate with Redocly (optional, skip if fails)
echo -e "\n${YELLOW}Step 2/3:${NC} Validating OpenAPI schema (optional)..."
if command -v npx &> /dev/null; then
    npx @redocly/cli lint "$OPENAPI_FILE" || echo -e "${YELLOW}⚠️  Validation warnings (continuing anyway)${NC}"
else
    echo -e "${YELLOW}⚠️  npx not found, skipping validation${NC}"
fi

# Step 3: Generate Mintlify docs
echo -e "\n${YELLOW}Step 3/3:${NC} Generating Mintlify documentation..."
npx @mintlify/scraping@latest openapi-file "$OPENAPI_FILE" -o ./api-reference

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ OpenAPI import completed successfully!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
    echo -e "📝 Next steps:"
    echo -e "   1. Review generated .mdx files in ./api-reference"
    echo -e "   2. Update docs.json with new navigation (see console output above)"
    echo -e "   3. Run 'mintlify dev' to preview changes\n"
else
    echo -e "\n${RED}❌ Failed to generate Mintlify docs${NC}"
    exit 1
fi
