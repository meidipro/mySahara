# Quick Start Guide - mySahara Health Backend

## 1. Install Dependencies

```bash
# Navigate to backend directory
cd E:\mySahara\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Create Logs Directory

```bash
mkdir logs
```

## 3. Verify Environment Variables

Make sure `E:\mySahara\.env` contains:

```env
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
```

## 4. Run the Server

**Option A: Using the startup script (Windows)**
```bash
start.bat
```

**Option B: Direct Python**
```bash
python main.py
```

**Option C: Using Uvicorn**
```bash
uvicorn main:app --reload --port 8000
```

## 5. Test the API

Open your browser and go to:
- http://localhost:8000 - Root endpoint
- http://localhost:8000/docs - Interactive API documentation
- http://localhost:8000/health - Health check

## 6. Test with curl

### Health Check
```bash
curl http://localhost:8000/health
```

### AI Chat
```bash
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are diabetes symptoms?", "language": "en"}'
```

### Get Health Tips
```bash
curl http://localhost:8000/api/health/tips?category=nutrition&language=en
```

## Troubleshooting

### Port already in use?
Change the port in `.env`:
```env
PORT=8001
```

### Import errors?
Make sure virtual environment is activated:
```bash
venv\Scripts\activate
```

### API keys not working?
Check `.env` file exists at `E:\mySahara\.env` (parent directory)

### Google Cloud Vision errors?
1. Verify credentials file exists
2. Check GOOGLE_APPLICATION_CREDENTIALS path in .env
3. Ensure Vision API is enabled in Google Cloud Console

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Explore API endpoints at http://localhost:8000/docs
3. Test OCR with medical document images
4. Integrate with your Flutter frontend

## API Endpoint Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/ocr/process` | POST | Extract text from image |
| `/api/ocr/medical-document` | POST | Extract medical data |
| `/api/ai/chat` | POST | Chat with AI assistant |
| `/api/health/analyze-symptoms` | POST | Analyze symptoms |
| `/api/health/tips` | GET | Get health tips |
| `/api/health/predict` | POST | Predict health risks |

## Production Deployment

For production deployment:

```bash
# Install with production server
pip install gunicorn

# Run with multiple workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

Or use Docker (see README.md for Dockerfile).

---

Happy coding! 🚀
