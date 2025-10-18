"""
OCR Service using Google Cloud Vision API.
Handles text extraction and medical document parsing.
"""

import os
import base64
import io
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from google.cloud import vision
from google.oauth2 import service_account
from PIL import Image
from loguru import logger


class OCRService:
    """
    Service for OCR processing using Google Cloud Vision API.
    """

    def __init__(self):
        """
        Initialize OCR service with Google Cloud Vision credentials.
        """
        self.credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        if not self.credentials_path or not os.path.exists(self.credentials_path):
            logger.warning(
                f"Google Cloud Vision credentials not found at: {self.credentials_path}"
            )
            self.client = None
        else:
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                self.client = vision.ImageAnnotatorClient(credentials=credentials)
                logger.info("Google Cloud Vision client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Vision client: {str(e)}")
                self.client = None

    async def extract_text_from_image(
        self, image_data: bytes, language: str = "en"
    ) -> Dict[str, Any]:
        """
        Extract text from image using Google Cloud Vision API.

        Args:
            image_data: Image data in bytes
            language: Language code for text detection

        Returns:
            Dict containing extracted text and metadata
        """
        if not self.client:
            raise Exception("Google Cloud Vision client not initialized")

        try:
            # Create vision image object
            image = vision.Image(content=image_data)

            # Set language hints
            language_hints = []
            if language == "bn":
                language_hints = ["bn", "bn-BD"]
            else:
                language_hints = ["en"]

            image_context = vision.ImageContext(language_hints=language_hints)

            # Perform text detection
            response = self.client.text_detection(image=image, image_context=image_context)

            if response.error.message:
                raise Exception(f"Vision API error: {response.error.message}")

            texts = response.text_annotations

            if not texts:
                return {
                    "success": False,
                    "text": "",
                    "confidence": 0.0,
                    "language": language,
                    "error": "No text detected in image"
                }

            # First annotation contains the full text
            full_text = texts[0].description

            # Calculate average confidence
            total_confidence = sum([text.confidence for text in texts if hasattr(text, 'confidence')])
            avg_confidence = total_confidence / len(texts) if texts else 0.0

            logger.info(f"Text extracted successfully. Length: {len(full_text)}")

            return {
                "success": True,
                "text": full_text,
                "confidence": avg_confidence,
                "language": language,
                "word_count": len(full_text.split())
            }

        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return {
                "success": False,
                "text": "",
                "confidence": 0.0,
                "language": language,
                "error": str(e)
            }

    async def extract_medical_document(
        self, image_data: bytes, document_type: str = "prescription"
    ) -> Dict[str, Any]:
        """
        Extract structured data from medical documents.

        Args:
            image_data: Image data in bytes
            document_type: Type of medical document

        Returns:
            Dict containing structured medical data
        """
        # First extract raw text
        ocr_result = await self.extract_text_from_image(image_data)

        if not ocr_result["success"]:
            return {
                "success": False,
                "error": ocr_result.get("error", "Text extraction failed")
            }

        raw_text = ocr_result["text"]

        # Parse medical data based on document type
        if document_type == "prescription":
            extracted_data = self._parse_prescription(raw_text)
        elif document_type == "lab_report":
            extracted_data = self._parse_lab_report(raw_text)
        elif document_type == "medical_certificate":
            extracted_data = self._parse_medical_certificate(raw_text)
        else:
            extracted_data = {"raw_text": raw_text}

        return {
            "success": True,
            "document_type": document_type,
            "extracted_data": extracted_data,
            "raw_text": raw_text,
            "confidence": ocr_result.get("confidence", 0.0)
        }

    def _parse_prescription(self, text: str) -> Dict[str, Any]:
        """
        Parse prescription document and extract structured data.

        Args:
            text: Raw text from OCR

        Returns:
            Dict containing structured prescription data
        """
        data = {
            "doctor_name": None,
            "hospital": None,
            "date": None,
            "patient_name": None,
            "medications": [],
            "diagnosis": None,
            "instructions": None
        }

        try:
            lines = text.split('\n')

            # Extract doctor name (usually contains Dr. or Doctor)
            for line in lines:
                if re.search(r'\b(Dr\.|Doctor|Dr)\s+([A-Za-z\s.]+)', line, re.IGNORECASE):
                    match = re.search(r'\b(Dr\.|Doctor|Dr)\s+([A-Za-z\s.]+)', line, re.IGNORECASE)
                    if match:
                        data["doctor_name"] = match.group(0).strip()
                        break

            # Extract date
            date_patterns = [
                r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
                r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',
                r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}'
            ]
            for pattern in date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    data["date"] = match.group(0)
                    break

            # Extract patient name (usually after "Patient:", "Name:", etc.)
            patient_patterns = [
                r'Patient\s*[:\-]\s*([A-Za-z\s]+)',
                r'Name\s*[:\-]\s*([A-Za-z\s]+)',
                r'Patient Name\s*[:\-]\s*([A-Za-z\s]+)'
            ]
            for pattern in patient_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    data["patient_name"] = match.group(1).strip()
                    break

            # Extract medications (simplified pattern)
            medication_keywords = ['tab', 'cap', 'syrup', 'injection', 'mg', 'ml']
            for line in lines:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in medication_keywords):
                    # Try to parse medication details
                    med_info = {
                        "name": line.strip(),
                        "dosage": None,
                        "frequency": None,
                        "duration": None
                    }

                    # Extract dosage
                    dosage_match = re.search(r'(\d+\s*(?:mg|ml|g))', line, re.IGNORECASE)
                    if dosage_match:
                        med_info["dosage"] = dosage_match.group(1)

                    # Extract frequency
                    freq_patterns = [
                        r'(\d+\s*(?:times?|x)\s*(?:daily|per day|a day))',
                        r'(once|twice|thrice)\s*(?:daily|per day|a day)',
                        r'(\d+-\d+-\d+)'
                    ]
                    for pattern in freq_patterns:
                        freq_match = re.search(pattern, line, re.IGNORECASE)
                        if freq_match:
                            med_info["frequency"] = freq_match.group(1)
                            break

                    # Extract duration
                    duration_match = re.search(
                        r'(?:for\s+)?(\d+\s*(?:days?|weeks?|months?))',
                        line,
                        re.IGNORECASE
                    )
                    if duration_match:
                        med_info["duration"] = duration_match.group(1)

                    data["medications"].append(med_info)

            # Extract diagnosis (usually after "Diagnosis:", "Dx:", etc.)
            diagnosis_patterns = [
                r'Diagnosis\s*[:\-]\s*([^\n]+)',
                r'Dx\s*[:\-]\s*([^\n]+)',
                r'Impression\s*[:\-]\s*([^\n]+)'
            ]
            for pattern in diagnosis_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    data["diagnosis"] = match.group(1).strip()
                    break

        except Exception as e:
            logger.error(f"Error parsing prescription: {str(e)}")

        return data

    def _parse_lab_report(self, text: str) -> Dict[str, Any]:
        """
        Parse lab report and extract test results.

        Args:
            text: Raw text from OCR

        Returns:
            Dict containing structured lab report data
        """
        data = {
            "patient_name": None,
            "date": None,
            "tests": []
        }

        # Basic parsing - can be enhanced based on specific lab report formats
        lines = text.split('\n')

        for line in lines:
            # Look for test results (typically: Test Name: Value Unit)
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    test_name = parts[0].strip()
                    result = parts[1].strip()
                    data["tests"].append({
                        "name": test_name,
                        "result": result
                    })

        return data

    def _parse_medical_certificate(self, text: str) -> Dict[str, Any]:
        """
        Parse medical certificate.

        Args:
            text: Raw text from OCR

        Returns:
            Dict containing structured certificate data
        """
        data = {
            "doctor_name": None,
            "patient_name": None,
            "date": None,
            "diagnosis": None,
            "recommendations": None
        }

        # Similar parsing logic as prescription
        # This is a simplified version

        return data

    async def process_base64_image(
        self, base64_string: str, extract_medical: bool = False
    ) -> Dict[str, Any]:
        """
        Process base64 encoded image.

        Args:
            base64_string: Base64 encoded image
            extract_medical: Whether to extract medical data

        Returns:
            Dict containing processing results
        """
        try:
            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]

            # Decode base64 to bytes
            image_data = base64.b64decode(base64_string)

            if extract_medical:
                return await self.extract_medical_document(image_data)
            else:
                return await self.extract_text_from_image(image_data)

        except Exception as e:
            logger.error(f"Failed to process base64 image: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to process image: {str(e)}"
            }
