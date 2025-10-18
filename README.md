# mySahara Health Backend API

FastAPI backend for mySahara health application with OCR, AI chat, and health analysis capabilities.

## Features

- **OCR Processing**: Extract text and structured data from medical documents using Google Cloud Vision
- **AI Chat**: Conversational health assistant with Groq (Llama) and Gemini AI
- **Health Analysis**: Symptom analysis, health tips, and predictive health intelligence
- **Multi-language Support**: English and Bangla
- **Production-ready**: Async/await, error handling, logging, and validation

## Prerequisites

- Python 3.9 or higher
- pip package manager
- Google Cloud Vision API credentials
- Groq API key
- Gemini API key
- Supabase account (optional)

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   cd E:\mySahara\backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:

   The backend looks for a `.env` file in the parent directory (`E:\mySahara\.env`).

   Ensure your `.env` file contains:
   ```env
   # AI Services
   GROQ_API_KEY=your_groq_api_key
   GEMINI_API_KEY=your_gemini_api_key
   GOOGLE_APPLICATION_CREDENTIALS=path/to/google-cloud-credentials.json

   # Supabase (optional)
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   SUPABASE_KEY=your_supabase_service_key

   # Server Configuration
   PORT=8000
   ```

6. **Create logs directory**:
   ```bash
   mkdir logs
   ```

## Running the Server

### Development Mode

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once the server is running, access:

- **Interactive API docs (Swagger)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

## API Endpoints

### OCR Endpoints

- `POST /api/ocr/process` - Process image and extract text
- `POST /api/ocr/process-file` - Process uploaded file
- `POST /api/ocr/medical-document` - Extract structured medical data
- `POST /api/ocr/medical-document-file` - Process medical document file

### AI Chat Endpoints

- `POST /api/ai/chat` - Chat with AI health assistant
- `POST /api/ai/translate` - Translate between English and Bangla
- `POST /api/ai/explain-medical-term` - Explain medical terminology
- `GET /api/ai/conversation-starters` - Get conversation starter suggestions

### Health Analysis Endpoints

- `POST /api/health/analyze-symptoms` - Analyze symptoms
- `GET /api/health/tips` - Get health tips
- `POST /api/health/predict` - Predictive health intelligence
- `GET /api/health/categories` - Get health categories
- `GET /api/health/emergency-symptoms` - Get emergency symptoms list

## Project Structure

```
backend/
├── api/
│   ├── __init__.py
│   ├── ocr.py              # OCR endpoints
│   ├── ai_chat.py          # AI chat endpoints
│   └── health.py           # Health analysis endpoints
├── models/
│   ├── __init__.py
│   ├── requests.py         # Pydantic request models
│   └── responses.py        # Pydantic response models
├── services/
│   ├── __init__.py
│   ├── ocr_service.py      # OCR service layer
│   └── ai_service.py       # AI service layer
├── utils/
│   ├── __init__.py
│   └── helpers.py          # Utility functions
├── logs/                   # Log files
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Example Usage

### OCR Processing

```python
import requests
import base64

# Read image and encode to base64
with open("prescription.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()

# Process medical document
response = requests.post(
    "http://localhost:8000/api/ocr/medical-document",
    data={
        "image_base64": image_base64,
        "document_type": "prescription",
        "language": "en"
    }
)

result = response.json()
print(result["extracted_data"])
```

### AI Chat

```python
import requests

response = requests.post(
    "http://localhost:8000/api/ai/chat",
    json={
        "message": "What are the symptoms of diabetes?",
        "language": "en",
        "use_medical_mode": True
    }
)

result = response.json()
print(result["message"])
```

### Symptom Analysis

```python
import requests

response = requests.post(
    "http://localhost:8000/api/health/analyze-symptoms",
    json={
        "symptoms": ["fever", "cough", "fatigue"],
        "duration": "3 days",
        "severity": "moderate",
        "age": 35
    }
)

result = response.json()
print(result["analysis"])
print(result["recommendations"])
```

## Error Handling

The API uses standard HTTP status codes:

- `200 OK` - Successful request
- `400 Bad Request` - Invalid input
- `500 Internal Server Error` - Server error
- `501 Not Implemented` - Feature not yet implemented
- `503 Service Unavailable` - Service temporarily unavailable

Error responses follow this format:
```json
{
  "success": false,
  "error": "Error message",
  "error_type": "ExceptionType"
}
```

## Logging

Logs are written to:
- Console (INFO level)
- `logs/backend.log` (DEBUG level)

Logs include:
- Request processing
- API calls to external services
- Errors and exceptions
- Performance metrics

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **CORS**: Configure appropriate origins in production
3. **Input Validation**: All inputs are validated with Pydantic
4. **Rate Limiting**: Consider adding rate limiting for production
5. **HTTPS**: Use HTTPS in production

## Performance

- Async/await for non-blocking operations
- Connection pooling for external APIs
- Efficient image processing with PIL
- Caching can be added for frequently accessed data

## Troubleshooting

### Google Cloud Vision not working

1. Verify credentials file path in `.env`
2. Ensure the service account has Vision API permissions
3. Check if Vision API is enabled in Google Cloud Console

### Groq/Gemini API errors

1. Verify API keys in `.env`
2. Check API quota/limits
3. Review logs for specific error messages

### Import errors

1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python version (3.9+)

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black .
```

### Type Checking

```bash
mypy .
```

## Deployment

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

Set these in your production environment:
- `PORT` - Server port
- `GROQ_API_KEY` - Groq API key
- `GEMINI_API_KEY` - Gemini API key
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to credentials

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests
4. Submit a pull request

## License

Proprietary - mySahara Health Application

## Support

For issues or questions, contact the development team.

---

**Version**: 1.0.0
**Last Updated**: 2025-10-12
