# mySahara Health Backend - Architecture Documentation

## Overview

The mySahara Health Backend is a FastAPI-based microservice that provides OCR, AI chat, and health analysis capabilities for the mySahara health application.

## Technology Stack

### Core Framework
- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **Pydantic**: Data validation and settings management

### AI & ML Services
- **Google Cloud Vision API**: OCR and text extraction
- **Groq API**: Primary AI chat service (Llama models)
- **Google Gemini API**: Fallback AI service
- **Pillow**: Image processing

### Database & Storage
- **Supabase**: PostgreSQL database (optional)
- **Redis**: Caching and task queue (optional)

### Utilities
- **python-dotenv**: Environment variable management
- **loguru**: Advanced logging
- **requests/httpx**: HTTP client

## Architecture Pattern

The backend follows a **layered architecture** pattern:

```
┌─────────────────────────────────────────┐
│           FastAPI Router Layer          │
│  (api/ocr.py, api/ai_chat.py, etc.)   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│          Service Layer                  │
│  (services/ocr_service.py, etc.)       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│       External APIs & Resources         │
│  (Google Cloud, Groq, Gemini, etc.)    │
└─────────────────────────────────────────┘
```

## Directory Structure

```
backend/
├── api/                    # API endpoints (Router layer)
│   ├── __init__.py
│   ├── ocr.py             # OCR endpoints
│   ├── ai_chat.py         # AI chat endpoints
│   └── health.py          # Health analysis endpoints
│
├── services/              # Business logic (Service layer)
│   ├── __init__.py
│   ├── ocr_service.py     # OCR processing logic
│   └── ai_service.py      # AI chat logic
│
├── models/                # Data models
│   ├── __init__.py
│   ├── requests.py        # Request models (Pydantic)
│   └── responses.py       # Response models (Pydantic)
│
├── utils/                 # Utility functions
│   ├── __init__.py
│   └── helpers.py         # Helper functions
│
├── logs/                  # Log files (gitignored)
│
├── main.py               # Application entry point
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore rules
├── start.bat            # Windows startup script
├── start.sh             # Linux/Mac startup script
├── test_api.py          # API test script
├── README.md            # Main documentation
├── QUICKSTART.md        # Quick start guide
└── ARCHITECTURE.md      # This file
```

## Core Components

### 1. Main Application (main.py)

Entry point that:
- Loads environment variables from parent directory
- Configures CORS middleware
- Registers API routers
- Sets up error handling
- Configures logging

### 2. API Layer (api/)

**Responsibilities:**
- Handle HTTP requests/responses
- Validate input using Pydantic models
- Call service layer
- Format responses
- Handle errors

**Endpoints:**

#### OCR API (api/ocr.py)
- `POST /api/ocr/process` - Extract text from base64 image
- `POST /api/ocr/process-file` - Extract text from uploaded file
- `POST /api/ocr/medical-document` - Extract structured medical data
- `POST /api/ocr/medical-document-file` - Process medical document file

#### AI Chat API (api/ai_chat.py)
- `POST /api/ai/chat` - Chat with AI assistant
- `POST /api/ai/translate` - Translate text
- `POST /api/ai/explain-medical-term` - Explain medical terms
- `GET /api/ai/conversation-starters` - Get conversation starters

#### Health Analysis API (api/health.py)
- `POST /api/health/analyze-symptoms` - Analyze symptoms
- `GET /api/health/tips` - Get health tips
- `POST /api/health/predict` - Predict health risks
- `GET /api/health/categories` - Get health categories
- `GET /api/health/emergency-symptoms` - Get emergency symptoms

### 3. Service Layer (services/)

**OCRService (services/ocr_service.py)**
- Initialize Google Cloud Vision client
- Extract text from images
- Parse medical documents
- Extract structured data (prescriptions, lab reports)

**AIService (services/ai_service.py)**
- Manage Groq and Gemini API clients
- Handle chat conversations
- Analyze symptoms
- Generate health tips
- Predict health risks
- Language detection

### 4. Data Models (models/)

**Request Models (models/requests.py)**
- `OCRRequest` - OCR processing request
- `MedicalDocumentRequest` - Medical document request
- `ChatRequest` - AI chat request
- `SymptomAnalysisRequest` - Symptom analysis request
- `HealthTipsRequest` - Health tips request
- `PredictiveHealthRequest` - Health prediction request

**Response Models (models/responses.py)**
- `OCRResponse` - OCR result
- `MedicalDocumentResponse` - Medical document result
- `ChatResponse` - AI chat response
- `HealthAnalysisResponse` - Health analysis result
- `HealthTipsResponse` - Health tips result
- `PredictiveHealthResponse` - Health prediction result

### 5. Utilities (utils/)

Helper functions:
- Language detection
- Date parsing
- Image processing (resize, compress)
- Base64 validation
- Text sanitization
- Error formatting

## Data Flow

### OCR Processing Flow

```
1. Client sends image (base64 or file)
   ↓
2. API endpoint validates input (api/ocr.py)
   ↓
3. OCRService processes image (services/ocr_service.py)
   ↓
4. Google Cloud Vision API extracts text
   ↓
5. Text is parsed for medical data
   ↓
6. Structured data is returned to client
```

### AI Chat Flow

```
1. Client sends message + conversation history
   ↓
2. API endpoint validates request (api/ai_chat.py)
   ↓
3. AIService processes message (services/ai_service.py)
   ↓
4. Language is detected
   ↓
5. System prompt is prepared
   ↓
6. Groq API is called (Llama model)
   ↓ (if fails)
7. Gemini API is called (fallback)
   ↓
8. Response is returned to client
```

### Health Analysis Flow

```
1. Client sends symptoms + patient info
   ↓
2. API endpoint validates request (api/health.py)
   ↓
3. AIService analyzes symptoms (services/ai_service.py)
   ↓
4. AI generates analysis
   ↓
5. Risk level is determined
   ↓
6. Recommendations are generated
   ↓
7. Structured response is returned
```

## Error Handling

### Error Flow
1. Exception occurs in service layer
2. Error is logged with loguru
3. HTTP exception is raised
4. FastAPI catches exception
5. Global exception handler formats error
6. Error response returned to client

### Error Response Format
```json
{
  "success": false,
  "error": "Error message",
  "error_type": "ExceptionType"
}
```

## Logging

### Log Levels
- **DEBUG**: Detailed debugging information
- **INFO**: General information (default)
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical errors

### Log Destinations
1. **Console**: INFO level and above
2. **File**: DEBUG level and above (`logs/backend.log`)

### Log Rotation
- Files rotate at 500 MB
- Keep 10 days of logs

## Security Considerations

### API Keys
- Stored in `.env` file (not committed)
- Loaded via python-dotenv
- Accessed via environment variables

### CORS
- Configured for specific origins
- Wildcard (`*`) only for development
- Should be restricted in production

### Input Validation
- All inputs validated with Pydantic
- Type checking enforced
- Field constraints applied

### Rate Limiting
- Recommended for production
- Can use FastAPI rate limiter middleware

## Performance Optimization

### Async/Await
- All endpoints are async
- Non-blocking I/O operations
- Better concurrency

### Caching (Future)
- Redis for response caching
- Cache AI responses
- Cache OCR results

### Image Processing
- Resize large images
- Compress before processing
- Reduce API costs

## Testing

### Manual Testing
```bash
python test_api.py
```

### Unit Tests (Future)
```bash
pytest tests/
```

## Deployment

### Development
```bash
uvicorn main:app --reload --port 8000
```

### Production
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker
```bash
docker build -t mysahara-backend .
docker run -p 8000:8000 mysahara-backend
```

## Monitoring

### Health Check
- Endpoint: `GET /health`
- Returns service status
- Checks environment variables

### Logs
- Monitor `logs/backend.log`
- Check for errors and warnings

### Metrics (Future)
- Request count
- Response times
- Error rates
- API usage

## Future Enhancements

1. **Database Integration**
   - Store user data in Supabase
   - Cache OCR results
   - Store conversation history

2. **Authentication**
   - JWT token authentication
   - User management
   - Role-based access control

3. **Rate Limiting**
   - Prevent API abuse
   - User-based limits

4. **Webhooks**
   - Async processing notifications
   - Integration with frontend

5. **Analytics**
   - Usage tracking
   - Performance monitoring
   - User insights

6. **Advanced OCR**
   - Multiple language support
   - Better medical term extraction
   - Handwriting recognition

7. **Enhanced AI**
   - Fine-tuned models
   - Better context understanding
   - Multi-turn conversations

8. **Testing**
   - Unit tests
   - Integration tests
   - Load testing

## API Versioning

Currently: v1 (implicit)

Future versions should use:
- URL versioning: `/api/v2/ocr/process`
- Header versioning: `X-API-Version: 2`

## Dependencies Management

### Update Dependencies
```bash
pip list --outdated
pip install --upgrade package_name
```

### Security Audit
```bash
pip install safety
safety check
```

## Contributing

1. Follow PEP 8 style guide
2. Add type hints
3. Write docstrings
4. Add tests
5. Update documentation

## Support

For questions or issues:
1. Check documentation
2. Review logs
3. Test with `test_api.py`
4. Contact development team

---

**Last Updated**: 2025-10-12
**Version**: 1.0.0
