# PDF to Markdown Service API Documentation

This document provides detailed information about the PDF to Markdown conversion API.

## Base URL

The base URL for all API endpoints depends on your deployment:

- Local development: `http://localhost:3000`
- Production: `https://your-domain.com`

## Endpoints

### Health Check

Check if the service is up and running.

**Request:**
```
GET /health
```

**Response:**
```json
{
  "status": "ok"
}
```

**Status Codes:**
- `200 OK`: Service is running properly

### Single PDF Conversion

Convert a single PDF from a URL to Markdown.

**Request:**
```
GET /convert?url=https://example.com/document.pdf&truncate_to=3000
```

**Parameters:**
- `url` (required): URL of the PDF to convert
- `truncate_to` (optional): Maximum number of words to include in the output
  - Default: 3000
  - Set to 'none' to return the entire document with no truncation
  - Integer values <= 0 will use the default (3000)

**Response:**
Markdown text with Content-Type: text/markdown

If truncated, a note will be added at the end:
```
... (Truncated to 3000 words out of approximately 5000 total words)
```

**Status Codes:**
- `200 OK`: Conversion successful
- `400 Bad Request`: Missing URL parameter
- `500 Internal Server Error`: Error during conversion

### Batch PDF Conversion

Convert multiple PDFs from URLs and combine them into a single Markdown document.

**Request:**
```
POST /convert/batch
Content-Type: application/json

{
  "urls": [
    "https://example.com/document1.pdf",
    "https://example.com/document2.pdf"
  ],
  "truncate_to": 3000
}
```

**Request Body:**
- `urls` (required): Array of PDF URLs to convert
- `truncate_to` (optional): Maximum number of words per document
  - Default: 3000
  - Set to 'none' to return the entire documents with no truncation
  - Integer values <= 0 will use the default (3000)

**Response:**
Combined Markdown text with Content-Type: text/markdown

The response format includes a source header for each document:
```
##############Source URL: https://example.com/document1.pdf

[Markdown content of document1]

##############Source URL: https://example.com/document2.pdf

[Markdown content of document2]
```

**Status Codes:**
- `200 OK`: Conversion successful (even if some PDFs failed, the successful ones will be included)
- `400 Bad Request`: Missing or invalid URLs array
- `500 Internal Server Error`: Error during conversion of all PDFs

## Error Handling

The API handles errors gracefully:

1. For single PDF conversion, if the PDF cannot be processed, an error message is returned.
2. For batch conversion, if a specific PDF fails, an error message is included for that PDF but the process continues with the other PDFs.

Example error in batch conversion:
```
##############Source URL: https://example.com/document1.pdf

Error processing this PDF: Failed to download PDF: 404 Client Error: Not Found for url: https://example.com/document1.pdf
```

## Performance Considerations

- The service processes PDFs one at a time
- Large PDFs may take longer to process
- Temporary files are automatically cleaned up after 1 hour
- The truncation feature can improve performance for very large documents

## Security Considerations

- The service does not store PDFs permanently
- PDFs are downloaded to a temporary directory and deleted after processing
- The service runs as a non-root user in the Docker container