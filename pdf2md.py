#!/usr/bin/env python3
"""
PDF to Markdown API Service

A simple API service to convert PDF to Markdown format.
It provides both single PDF conversion and batch processing capabilities.
"""
from flask import Flask, request, jsonify
import os
import tempfile
import requests
import logging
import time
import re
import uuid
import pypdf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pdf2md.log")
    ]
)
logger = logging.getLogger('pdf2md')

# Initialize Flask app
app = Flask(__name__)

# Create temporary directory for file storage
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'pdf2md')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Clean up old files periodically
def cleanup_old_files():
    now = time.time()
    try:
        for file in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, file)
            if os.path.isfile(file_path) and os.path.getmtime(file_path) < now - 3600:
                try:
                    os.remove(file_path)
                    logger.info(f"Removed old file: {file_path}")
                except Exception as e:
                    logger.error(f"Error removing file {file_path}: {e}")
    except Exception as e:
        logger.error(f"Error cleaning up old files: {e}")

# Download PDF from URL
def download_pdf(url):
    try:
        logger.info(f"Downloading PDF from URL: {url}")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Create a unique filename
        filename = f"{uuid.uuid4()}-{url.split('/')[-1]}"
        output_path = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"PDF saved to: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error downloading PDF: {e}")
        raise

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    try:
        logger.info(f"Extracting text from PDF: {pdf_path}")
        text = ""
        reader = pypdf.PdfReader(pdf_path)
        
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            if page_text.strip():
                text += f"## Page {i+1}\n\n{page_text}\n\n"
        
        return text
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        return ""

# Process text to Markdown
def process_text_to_markdown(text):
    if not text.strip():
        return "No text could be extracted from the PDF."
    
    # Simple processing - just return the extracted text
    return text

# Truncate markdown to specified number of words
def truncate_markdown(markdown, truncate_to=None):
    if truncate_to is None or truncate_to <= 0:
        # Return full markdown if truncate_to is None or invalid
        return markdown
    
    words = markdown.split()
    if len(words) <= truncate_to:
        # No need to truncate
        return markdown
    
    # Truncate to specified number of words
    truncated = ' '.join(words[:truncate_to])
    
    # Add note about truncation
    truncated += f"\n\n... (Truncated to {truncate_to} words out of approximately {len(words)} total words)"
    
    return truncated

# Convert PDF to Markdown
def pdf_to_markdown(pdf_path, truncate_to=3000):
    logger.info(f"Converting PDF to Markdown: {pdf_path}")
    
    # Extract text
    text = extract_text_from_pdf(pdf_path)
    
    if text:
        # Process to markdown
        markdown = process_text_to_markdown(text)
        
        # Truncate if needed (default 3000 words if not specified)
        if truncate_to != 'none':
            markdown = truncate_markdown(markdown, truncate_to)
            
        return markdown
    else:
        logger.error("Failed to extract text from PDF")
        return "Failed to extract text from PDF"

# API Routes

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

# Single PDF conversion endpoint
@app.route('/convert', methods=['GET'])
def convert_url():
    cleanup_old_files()  # Clean up old files
    
    url = request.args.get('url')
    
    if not url:
        return jsonify({'error': 'URL parameter is required'}), 400
    
    # Get truncate_to parameter, default is 3000
    truncate_to_param = request.args.get('truncate_to', '3000')
    
    # Parse truncate_to parameter
    if truncate_to_param.lower() == 'none':
        truncate_to = 'none'  # Special value to indicate no truncation
    else:
        try:
            truncate_to = int(truncate_to_param)
            if truncate_to <= 0:
                truncate_to = 3000  # Default if invalid value
        except ValueError:
            truncate_to = 3000  # Default if not a valid integer
    
    try:
        # Download the PDF
        pdf_path = download_pdf(url)
        
        # Convert to Markdown
        markdown = pdf_to_markdown(pdf_path, truncate_to)
        
        # Clean up
        try:
            os.remove(pdf_path)
        except:
            pass
        
        # Return the markdown
        return markdown, 200, {'Content-Type': 'text/markdown'}
    
    except Exception as e:
        logger.error(f"Error processing URL {url}: {e}")
        return f"Error: {str(e)}", 500, {'Content-Type': 'text/plain'}

# Multiple PDFs conversion endpoint
@app.route('/convert/batch', methods=['POST'])
def convert_batch():
    cleanup_old_files()  # Clean up old files
    
    data = request.json or {}
    urls = data.get('urls', [])
    
    if not urls or not isinstance(urls, list):
        return jsonify({'error': 'Array of URLs is required in the "urls" field'}), 400
    
    # Get truncate_to parameter, default is 3000
    truncate_to_param = data.get('truncate_to', '3000')
    
    # Parse truncate_to parameter
    if truncate_to_param == 'none' or truncate_to_param is None:
        truncate_to = 'none'  # Special value to indicate no truncation
    else:
        try:
            truncate_to = int(truncate_to_param)
            if truncate_to <= 0:
                truncate_to = 3000  # Default if invalid value
        except (ValueError, TypeError):
            truncate_to = 3000  # Default if not a valid integer
    
    combined_markdown = ""
    
    for url in urls:
        if not url or not isinstance(url, str):
            continue
        
        try:
            # Download the PDF
            pdf_path = download_pdf(url)
            
            # Convert to Markdown
            markdown = pdf_to_markdown(pdf_path, truncate_to)
            
            # Clean up
            try:
                os.remove(pdf_path)
            except:
                pass
            
            # Add to combined markdown with source header
            combined_markdown += f"##############Source URL: {url}\n\n{markdown}\n\n"
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            combined_markdown += f"##############Source URL: {url}\n\nError processing this PDF: {str(e)}\n\n"
    
    return combined_markdown, 200, {'Content-Type': 'text/markdown'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', 'False').lower() == 'true')