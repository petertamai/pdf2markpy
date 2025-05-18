#!/bin/bash
# This script tests the API endpoints

# Set the base URL
BASE_URL=${1:-"http://localhost:3000"}

echo "Testing PDF to Markdown API at $BASE_URL"
echo "----------------------------------------"

# Test health endpoint
echo "Testing /health endpoint..."
HEALTH_RESPONSE=$(curl -s "$BASE_URL/health")
if [[ $HEALTH_RESPONSE == *"ok"* ]]; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    echo "$HEALTH_RESPONSE"
    exit 1
fi

# Test single PDF conversion
echo "Testing /convert endpoint..."
TEST_PDF_URL="https://library.dbca.wa.gov.au/static/Journals/080052/080052-19.043.pdf"
CONVERT_RESPONSE=$(curl -s "$BASE_URL/convert?url=$TEST_PDF_URL" -o /tmp/convert_output.md -w "%{http_code}")
if [[ $CONVERT_RESPONSE == "200" ]]; then
    echo "✅ Single PDF conversion passed"
    echo "  Output saved to /tmp/convert_output.md"
    echo "  First few lines:"
    head -n 5 /tmp/convert_output.md
else
    echo "❌ Single PDF conversion failed with code: $CONVERT_RESPONSE"
    cat /tmp/convert_output.md
fi

# Test batch PDF conversion
echo "Testing /convert/batch endpoint..."
BATCH_JSON='{
  "urls": [
    "https://library.dbca.wa.gov.au/static/Journals/080052/080052-19.043.pdf",
    "https://library.dbca.wa.gov.au/static/Journals/080052/080052-35.020.pdf"
  ]
}'
BATCH_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d "$BATCH_JSON" "$BASE_URL/convert/batch" -o /tmp/batch_output.md -w "%{http_code}")
if [[ $BATCH_RESPONSE == "200" ]]; then
    echo "✅ Batch PDF conversion passed"
    echo "  Output saved to /tmp/batch_output.md"
    echo "  First few lines:"
    head -n 5 /tmp/batch_output.md
else
    echo "❌ Batch PDF conversion failed with code: $BATCH_RESPONSE"
    cat /tmp/batch_output.md
fi

echo "----------------------------------------"
echo "Tests completed!"