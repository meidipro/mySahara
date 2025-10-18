"""
OCR API endpoints for text extraction and medical document processing.
"""

import time
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
from loguru import logger

from models.requests import OCRRequest, MedicalDocumentRequest
from models.responses import OCRResponse, MedicalDocumentResponse
from services.ocr_service import OCRService
from utils.helpers import validate_base64_image, create_response

router = APIRouter()
ocr_service = OCRService()


@router.post("/process", response_model=OCRResponse)
async def process_ocr(
    image_base64: Optional[str] = Form(None),
    image_url: Optional[str] = Form(None),
    language: str = Form(default="en"),
    extract_medical_data: bool = Form(default=False)
):
    """
    Process image and extract text using OCR.

    Args:
        image_base64: Base64 encoded image (optional)
        image_url: URL to image (optional)
        language: Language code for OCR (default: en)
        extract_medical_data: Whether to extract structured medical data

    Returns:
        OCRResponse with extracted text and metadata

    Raises:
        HTTPException: If processing fails
    """
    start_time = time.time()

    try:
        logger.info(f"Processing OCR request - Language: {language}")

        # Validate input
        if not image_base64 and not image_url:
            raise HTTPException(
                status_code=400,
                detail="Either image_base64 or image_url must be provided"
            )

        # Process base64 image
        if image_base64:
            # Validate base64
            if not validate_base64_image(image_base64):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid base64 image format"
                )

            result = await ocr_service.process_base64_image(
                image_base64,
                extract_medical=extract_medical_data
            )
        else:
            # Process URL (would need to implement download logic)
            raise HTTPException(
                status_code=501,
                detail="Image URL processing not yet implemented"
            )

        processing_time = time.time() - start_time

        if result["success"]:
            return OCRResponse(
                success=True,
                text=result.get("text"),
                confidence=result.get("confidence", 0.0),
                language=result.get("language", language),
                processing_time=processing_time
            )
        else:
            return OCRResponse(
                success=False,
                error=result.get("error", "OCR processing failed"),
                processing_time=processing_time
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR processing error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {str(e)}"
        )


@router.post("/process-file", response_model=OCRResponse)
async def process_ocr_file(
    file: UploadFile = File(...),
    language: str = Form(default="en"),
    extract_medical_data: bool = Form(default=False)
):
    """
    Process uploaded image file and extract text.

    Args:
        file: Uploaded image file
        language: Language code for OCR
        extract_medical_data: Whether to extract structured medical data

    Returns:
        OCRResponse with extracted text and metadata
    """
    start_time = time.time()

    try:
        logger.info(f"Processing uploaded file: {file.filename}")

        # Read file content
        content = await file.read()

        if not content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        # Process image
        if extract_medical_data:
            result = await ocr_service.extract_medical_document(content)
        else:
            result = await ocr_service.extract_text_from_image(content, language)

        processing_time = time.time() - start_time

        if result["success"]:
            return OCRResponse(
                success=True,
                text=result.get("text"),
                confidence=result.get("confidence", 0.0),
                language=result.get("language", language),
                processing_time=processing_time
            )
        else:
            return OCRResponse(
                success=False,
                error=result.get("error", "OCR processing failed"),
                processing_time=processing_time
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File OCR processing error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"File processing failed: {str(e)}"
        )


@router.post("/medical-document", response_model=MedicalDocumentResponse)
async def process_medical_document(
    image_base64: Optional[str] = Form(None),
    image_url: Optional[str] = Form(None),
    document_type: str = Form(default="prescription"),
    language: str = Form(default="en")
):
    """
    Extract structured data from medical documents.

    Args:
        image_base64: Base64 encoded image
        image_url: URL to image
        document_type: Type of medical document (prescription, lab_report, etc.)
        language: Language code

    Returns:
        MedicalDocumentResponse with structured medical data

    Raises:
        HTTPException: If processing fails
    """
    try:
        logger.info(f"Processing medical document - Type: {document_type}")

        # Validate input
        if not image_base64 and not image_url:
            raise HTTPException(
                status_code=400,
                detail="Either image_base64 or image_url must be provided"
            )

        # Process base64 image
        if image_base64:
            # Validate base64
            if not validate_base64_image(image_base64):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid base64 image format"
                )

            # Remove data URL prefix if present
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]

            import base64
            image_data = base64.b64decode(image_base64)

            result = await ocr_service.extract_medical_document(
                image_data,
                document_type=document_type
            )
        else:
            # Process URL
            raise HTTPException(
                status_code=501,
                detail="Image URL processing not yet implemented"
            )

        if result["success"]:
            return MedicalDocumentResponse(
                success=True,
                document_type=result.get("document_type"),
                extracted_data=result.get("extracted_data"),
                raw_text=result.get("raw_text"),
                confidence=result.get("confidence", 0.0)
            )
        else:
            return MedicalDocumentResponse(
                success=False,
                error=result.get("error", "Medical document processing failed")
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Medical document processing error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Medical document processing failed: {str(e)}"
        )


@router.post("/medical-document-file", response_model=MedicalDocumentResponse)
async def process_medical_document_file(
    file: UploadFile = File(...),
    document_type: str = Form(default="prescription"),
    language: str = Form(default="en")
):
    """
    Extract structured data from uploaded medical document file.

    Args:
        file: Uploaded medical document image
        document_type: Type of document
        language: Language code

    Returns:
        MedicalDocumentResponse with structured data
    """
    try:
        logger.info(f"Processing medical document file: {file.filename}")

        # Read file content
        content = await file.read()

        if not content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        # Process document
        result = await ocr_service.extract_medical_document(
            content,
            document_type=document_type
        )

        if result["success"]:
            return MedicalDocumentResponse(
                success=True,
                document_type=result.get("document_type"),
                extracted_data=result.get("extracted_data"),
                raw_text=result.get("raw_text"),
                confidence=result.get("confidence", 0.0)
            )
        else:
            return MedicalDocumentResponse(
                success=False,
                error=result.get("error", "Processing failed")
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Medical document file processing error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )
