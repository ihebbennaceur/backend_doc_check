"""
PDF Analysis Service using OpenRouter + Google Gemini
Handles reading, scanning, and analyzing PDFs with AI reasoning
"""
import requests
import json
import logging
import base64
from pathlib import Path
from typing import Optional, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)

class PDFAnalyzer:
    """Analyze PDFs using OpenRouter's Google Gemini model with reasoning"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "~google/gemini-flash-latest"
        
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY not configured")
    
    def read_pdf_as_base64(self, file_path: str) -> str:
        """Read PDF file and convert to base64 for API"""
        try:
            with open(file_path, 'rb') as f:
                pdf_data = f.read()
            return base64.standard_b64encode(pdf_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {str(e)}")
            raise
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF using Google Gemini vision capabilities
        """
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not configured")
        
        try:
            # Read PDF
            pdf_base64 = self.read_pdf_as_base64(file_path)
            
            # Prepare request with vision capabilities
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://doc-check.app",
                "X-Title": "DocCheck PDF Analyzer"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please extract and transcribe ALL text content from this PDF document. Include headers, footers, tables, and any visible text. Format the output clearly."
                            },
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_base64
                                }
                            }
                        ]
                    }
                ],
                "temperature": 0.3,  # Lower temperature for more consistent extraction
                "max_tokens": 4000
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                raise ValueError("No response from API")
                
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise
    
    def analyze_pdf_with_reasoning(self, file_path: str, analysis_prompt: str) -> Dict[str, Any]:
        """
        Analyze PDF with advanced reasoning capabilities
        Returns both content and reasoning_details
        """
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not configured")
        
        try:
            pdf_base64 = self.read_pdf_as_base64(file_path)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://doc-check.app",
                "X-Title": "DocCheck PDF Analyzer"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": analysis_prompt or "Analyze this PDF document and provide detailed insights about its content, structure, and key information."
                            },
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_base64
                                }
                            }
                        ]
                    }
                ],
                "reasoning": {
                    "enabled": True,
                    "type": "enabled"  # Explicit reasoning
                },
                "temperature": 1,
                "max_tokens": 8000
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0]['message']
                return {
                    "analysis": message.get('content'),
                    "reasoning": message.get('reasoning_details'),
                    "model": result.get('model'),
                    "usage": result.get('usage')
                }
            else:
                raise ValueError("No response from API")
                
        except Exception as e:
            logger.error(f"Error analyzing PDF with reasoning: {str(e)}")
            raise
    
    def detect_document_type(self, file_path: str) -> Dict[str, Any]:
        """
        Detect document type and extract key metadata
        """
        analysis_prompt = """Analyze this PDF document and provide:
1. Document Type (invoice, contract, report, form, etc.)
2. Document Title/Subject
3. Date (if present)
4. Key stakeholders/parties involved
5. Main purpose or summary
6. Any important dates or deadlines
7. Confidence level (0-100%)

Format as JSON."""
        
        return self.analyze_pdf_with_reasoning(file_path, analysis_prompt)
    
    def extract_structured_data(self, file_path: str, fields: list) -> Dict[str, Any]:
        """
        Extract specific structured data from PDF
        
        Args:
            file_path: Path to PDF file
            fields: List of fields to extract (e.g., ["invoice_number", "total_amount", "due_date"])
        """
        fields_str = ", ".join(fields)
        analysis_prompt = f"""Extract the following structured data from this PDF document:
        
Fields to extract: {fields_str}

For each field found, provide:
- Field name
- Value
- Confidence level (0-100%)
- Location in document (page number, section)

Format as JSON."""
        
        return self.analyze_pdf_with_reasoning(file_path, analysis_prompt)


# Initialize the analyzer
pdf_analyzer = PDFAnalyzer()
