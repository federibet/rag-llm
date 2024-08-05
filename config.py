# config.py

import os

# Load configuration from environment variables or provide default values
COHERE_API_KEY = os.getenv('COHERE_API_KEY', 'pfK329FllWHqYXfGP0mwHi79OQEU1ehVMJV6PvPH')
DOCUMENT_FILE_PATH = os.getenv('DOCUMENT_FILE_PATH', 'documento.docx')
SUPPORTED_LANGUAGES = ['es', 'en', 'pt']