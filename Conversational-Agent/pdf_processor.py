import PyPDF2
import pdfplumber
import io
from typing import Dict, List, Optional
import streamlit as st

class PDFProcessor:
    """Utility class for processing PDF files and extracting content."""
    
    @staticmethod
    def extract_text_from_pdf(pdf_file) -> Dict[str, any]:
        """
        Extract text content and metadata from a PDF file.
        
        Args:
            pdf_file: StreamlitUploadedFile object
            
        Returns:
            Dictionary containing extracted text, metadata, and page count
        """
        try:
            # Read the PDF file
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
            
            # Extract metadata
            metadata = {
                'title': pdf_reader.metadata.get('/Title', 'Unknown'),
                'author': pdf_reader.metadata.get('/Author', 'Unknown'),
                'subject': pdf_reader.metadata.get('/Subject', ''),
                'creator': pdf_reader.metadata.get('/Creator', ''),
                'producer': pdf_reader.metadata.get('/Producer', ''),
                'creation_date': pdf_reader.metadata.get('/CreationDate', ''),
                'modification_date': pdf_reader.metadata.get('/ModDate', ''),
                'page_count': len(pdf_reader.pages)
            }
            
            # Extract text from each page
            text_content = []
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_content.append({
                            'page': page_num + 1,
                            'text': page_text.strip()
                        })
                except Exception as e:
                    st.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
            
            # Try pdfplumber for better text extraction if PyPDF2 didn't work well
            if not text_content:
                pdf_file.seek(0)  # Reset file pointer
                with pdfplumber.open(io.BytesIO(pdf_file.read())) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text_content.append({
                                'page': page_num + 1,
                                'text': page_text.strip()
                            })
            
            return {
                'metadata': metadata,
                'text_content': text_content,
                'total_pages': metadata['page_count'],
                'extracted_text': '\n\n'.join([f"Page {item['page']}:\n{item['text']}" for item in text_content]),
                'filename': pdf_file.name,
                'file_size': len(pdf_file.getvalue())
            }
            
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return None
    
    @staticmethod
    def extract_key_information(text_content: str) -> Dict[str, any]:
        """
        Extract key information from PDF text content.
        This is a basic implementation that can be enhanced with NLP.
        
        Args:
            text_content: Extracted text from PDF
            
        Returns:
            Dictionary containing key information
        """
        # Basic information extraction (can be enhanced with NLP)
        lines = text_content.split('\n')
        
        # Look for common patterns
        key_info = {
            'document_type': 'PDF Document',
            'main_topics': [],
            'key_phrases': [],
            'estimated_word_count': len(text_content.split()),
            'has_tables': 'table' in text_content.lower() or '|' in text_content,
            'has_numbers': any(char.isdigit() for char in text_content),
            'language': 'English'  # Basic assumption, can be enhanced
        }
        
        # Extract potential topics from lines that might be headers
        for line in lines:
            line = line.strip()
            if line and len(line) < 100 and line.isupper():
                key_info['main_topics'].append(line)
            elif line and len(line) < 50 and line.endswith(':'):
                key_info['key_phrases'].append(line)
        
        return key_info 