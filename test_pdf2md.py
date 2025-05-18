import unittest
import os
import tempfile
import shutil
from pdf2md import app, download_pdf, extract_text_from_pdf, pdf_to_markdown

class TestPdf2Markdown(unittest.TestCase):
    def setUp(self):
        # Create a test client
        self.app = app.test_client()
        self.app.testing = True
        
        # Create test temporary directory
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        # Remove test directory
        shutil.rmtree(self.test_dir)
        
    def test_health_endpoint(self):
        # Test the health endpoint
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'status': 'ok'})
        
    def test_convert_endpoint_missing_url(self):
        # Test convert endpoint without URL parameter
        response = self.app.get('/convert')
        self.assertEqual(response.status_code, 400)
        
    def test_batch_endpoint_missing_urls(self):
        # Test batch endpoint without URLs
        response = self.app.post('/convert/batch', json={})
        self.assertEqual(response.status_code, 400)
        
    def test_batch_endpoint_empty_urls(self):
        # Test batch endpoint with empty URLs array
        response = self.app.post('/convert/batch', json={'urls': []})
        self.assertEqual(response.status_code, 400)
        
    def test_batch_endpoint_invalid_json(self):
        # Test batch endpoint with invalid JSON
        response = self.app.post('/convert/batch', data='not json')
        self.assertEqual(response.status_code, 400)
        
    # Note: The following tests require network access and real PDFs
    # They can be enabled for integration testing but are commented out by default
    
    """
    def test_download_pdf(self):
        # Test PDF download function with a real URL
        test_url = "https://library.dbca.wa.gov.au/static/Journals/080052/080052-19.043.pdf"
        output_path = download_pdf(test_url)
        
        # Check if file was downloaded
        self.assertTrue(os.path.exists(output_path))
        self.assertTrue(os.path.getsize(output_path) > 0)
        
        # Clean up
        os.remove(output_path)
        
    def test_extract_text_from_pdf(self):
        # Test text extraction from a downloaded PDF
        test_url = "https://library.dbca.wa.gov.au/static/Journals/080052/080052-19.043.pdf"
        pdf_path = download_pdf(test_url)
        
        # Extract text
        text = extract_text_from_pdf(pdf_path)
        
        # Check if text was extracted
        self.assertTrue(len(text) > 0)
        self.assertIn("Page 1", text)
        
        # Clean up
        os.remove(pdf_path)
        
    def test_convert_endpoint(self):
        # Test the convert endpoint with a real URL
        test_url = "https://library.dbca.wa.gov.au/static/Journals/080052/080052-19.043.pdf"
        response = self.app.get(f'/convert?url={test_url}')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)
        self.assertIn(b"Page 1", response.data)
        
    def test_batch_endpoint(self):
        # Test the batch endpoint with real URLs
        test_urls = [
            "https://library.dbca.wa.gov.au/static/Journals/080052/080052-19.043.pdf",
            "https://library.dbca.wa.gov.au/static/Journals/080052/080052-35.020.pdf"
        ]
        
        response = self.app.post('/convert/batch', json={'urls': test_urls})
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)
        self.assertIn(b"Source URL", response.data)
    """

if __name__ == '__main__':
    unittest.main()