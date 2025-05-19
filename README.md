# PDF to Markdown API Service

A simple REST API service that converts PDFs to Markdown format. It supports both single PDF conversion and batch processing of multiple PDFs.

## Features

- Convert PDF from URL to Markdown text
- Batch convert multiple PDFs and combine them into a single Markdown document
- Truncate output to a specific number of words (customizable)
- Clean, simple API designed for easy integration
- Docker support for easy deployment
- Designed to be reliable and maintainable

## API Endpoints

### Health Check
```
GET /health
```
Response:
```json
{
  "status": "ok"
}
```

### Single PDF Conversion
```
GET /convert?url=https://example.com/document.pdf&truncate_to=3000
```
Parameters:
- `url` (required): URL of the PDF to convert
- `truncate_to` (optional): Maximum number of words to include (default: 3000, use 'none' for entire document)

Response: Plain Markdown text

### Batch PDF Conversion
```
POST /convert/batch
Content-Type: application/json

{
  "urls": [
    "https://example.com/document1.pdf",
    "https://example.com/document2.pdf"
  ],
  "truncate_to": "none"
}
```
Parameters:
- `urls` (required): Array of PDF URLs to convert
- `truncate_to` (optional): Maximum number of words per document (default: 3000, use 'none' for entire documents)

Response: Combined Markdown text with source URL headers

## Deployment

### Using Docker

1. Build the Docker image:
```bash
docker build -t pdf2markdown .
```

2. Run the container:
```bash
docker run -p 3000:3000 pdf2markdown
```

### Using EasyPanel

1. Add a new service in EasyPanel
2. Choose "Docker" as the deployment method
3. Configure the service with:
   - Repository URL: Your GitHub repository URL
   - Dockerfile path: `Dockerfile`
   - Port: 3000
   - Environment variables:
     - `DEBUG`: Set to "True" for development, "False" for production

## Usage Examples

### cURL Examples

1. Convert a single PDF:
```bash
curl "http://localhost:3000/convert?url=https://example.com/document.pdf"
```

2. Convert a single PDF with custom truncation:
```bash
curl "http://localhost:3000/convert?url=https://example.com/document.pdf&truncate_to=500"
```

3. Convert a single PDF with no truncation:
```bash
curl "http://localhost:3000/convert?url=https://example.com/document.pdf&truncate_to=none"
```

4. Batch convert multiple PDFs:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"urls":["https://example.com/document1.pdf","https://example.com/document2.pdf"],"truncate_to":1000}' http://localhost:3000/convert/batch
```

### Integration with n8n

For the batch endpoint in n8n:

1. Set up an HTTP Request node:
   - Method: POST
   - URL: http://your-server:3000/convert/batch
   - Body: JSON
   - JSON content:
   ```json
   {
     "urls": {{$json.output.pdf_results.map(item => item.url)}},
     "truncate_to": 2000
   }
   ```

## Environment Variables

- `PORT`: The port the server will listen on (default: 3000)
- `DEBUG`: Set to "True" to enable debug mode (default: False)

## Limitations

- Only processes PDFs accessible via URL
- Text extraction quality depends on the PDF structure and content
- Large PDFs may take longer to process

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Peter Tam <pt@petertam.pro>