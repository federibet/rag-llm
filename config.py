# config.py

import os

# Load configuration from environment variables or provide default values
COHERE_API_KEY = os.getenv('COHERE_API_KEY', 'insert_your_key')
DOCUMENT_FILE_PATH = os.getenv('DOCUMENT_FILE_PATH', 'documento.docx')
SUPPORTED_LANGUAGES = ['es', 'en', 'pt']
