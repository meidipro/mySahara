# Installation Checklist - mySahara Health Backend

## Pre-Installation

- [ ] Python 3.9 or higher installed
- [ ] pip package manager installed
- [ ] Git installed (optional)
- [ ] Text editor or IDE (VS Code, PyCharm, etc.)

## Step 1: Environment Setup

- [ ] Navigate to backend directory: `cd E:\mySahara\backend`
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate virtual environment:
  - Windows: `venv\Scripts\activate`
  - Linux/Mac: `source venv/bin/activate`
- [ ] Verify activation (prompt should show `(venv)`)

## Step 2: Install Dependencies

- [ ] Install all packages: `pip install -r requirements.txt`
- [ ] Wait for installation to complete (may take 2-5 minutes)
- [ ] Verify installation: `pip list` (should show all packages)

## Step 3: Configure Environment Variables

Check that `E:\mySahara\.env` file exists with:

- [ ] `GROQ_API_KEY` - Groq API key (required for AI chat)
- [ ] `GEMINI_API_KEY` - Gemini API key (fallback for AI)
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` - Path to Google Cloud credentials JSON
- [ ] `SUPABASE_URL` - Supabase database URL (optional)
- [ ] `SUPABASE_ANON_KEY` - Supabase anonymous key (optional)
- [ ] `SUPABASE_KEY` - Supabase service key (optional)

## Step 4: Verify Google Cloud Setup

- [ ] Google Cloud project created
- [ ] Vision API enabled in Google Cloud Console
- [ ] Service account created with Vision API permissions
- [ ] Credentials JSON file downloaded
- [ ] Path in `.env` matches actual file location
- [ ] File path uses absolute path (e.g., `D:\Projects\...`)

## Step 5: Create Required Directories

- [ ] Create logs directory: `mkdir logs`
- [ ] Verify directory exists: `dir logs` (Windows) or `ls logs` (Linux/Mac)

## Step 6: Verify Configuration

- [ ] Run config check: `python config.py`
- [ ] Review output for any issues or warnings
- [ ] Resolve any critical issues before proceeding

## Step 7: Start the Server

Choose one method:

**Method A: Using startup script (Windows)**
- [ ] Run: `start.bat`
- [ ] Wait for "Application startup complete"

**Method B: Using Python directly**
- [ ] Run: `python main.py`
- [ ] Wait for "Application startup complete"

**Method C: Using Uvicorn**
- [ ] Run: `uvicorn main:app --reload --port 8000`
- [ ] Wait for "Application startup complete"

## Step 8: Verify Server is Running

- [ ] Server shows "Application startup complete" message
- [ ] No error messages in console
- [ ] Port 8000 is not already in use

## Step 9: Test API Endpoints

### Manual Browser Tests

Open browser and test these URLs:

- [ ] http://localhost:8000 (should show welcome message)
- [ ] http://localhost:8000/health (should show "healthy" status)
- [ ] http://localhost:8000/docs (should show Swagger UI documentation)
- [ ] http://localhost:8000/redoc (should show ReDoc documentation)

### Automated Tests

- [ ] Open new terminal/command prompt
- [ ] Activate virtual environment
- [ ] Run: `python test_api.py`
- [ ] Review test results
- [ ] All or most tests should pass

## Step 10: Test Individual Features

### Test AI Chat

```bash
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Hello\", \"language\": \"en\"}"
```

- [ ] Returns success response
- [ ] Response includes AI message

### Test Health Tips

```bash
curl http://localhost:8000/api/health/tips?language=en
```

- [ ] Returns success response
- [ ] Response includes health tips

### Test OCR (requires image)

- [ ] Prepare test image (prescription, lab report, etc.)
- [ ] Use Swagger UI at http://localhost:8000/docs
- [ ] Navigate to `/api/ocr/process-file` endpoint
- [ ] Click "Try it out"
- [ ] Upload image file
- [ ] Click "Execute"
- [ ] Verify text extraction works

## Step 11: Review Logs

- [ ] Check console output for any errors
- [ ] Check `logs/backend.log` file exists
- [ ] Review log file for any warnings or errors
- [ ] Verify logging is working correctly

## Step 12: Common Issues Troubleshooting

### Issue: Port already in use
- [ ] Check if another service is using port 8000
- [ ] Change port in `.env` file: `PORT=8001`
- [ ] Restart server

### Issue: Module not found errors
- [ ] Verify virtual environment is activated
- [ ] Reinstall dependencies: `pip install -r requirements.txt`
- [ ] Check Python version: `python --version`

### Issue: Google Cloud Vision errors
- [ ] Verify credentials file exists at specified path
- [ ] Check file permissions (readable)
- [ ] Verify Vision API is enabled in Google Cloud Console
- [ ] Check service account has correct permissions

### Issue: API key errors (Groq/Gemini)
- [ ] Verify API keys are correct in `.env`
- [ ] Check API key validity (not expired)
- [ ] Test API keys with curl or API testing tool
- [ ] Check API quota/limits

### Issue: Import errors
- [ ] Check all `__init__.py` files exist
- [ ] Verify directory structure matches expected layout
- [ ] Restart Python interpreter
- [ ] Clear Python cache: delete `__pycache__` folders

## Step 13: Production Readiness (Optional)

For production deployment:

- [ ] Set `DEBUG=False` in environment
- [ ] Configure proper CORS origins (remove `*`)
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure proper logging levels
- [ ] Set up monitoring and alerts
- [ ] Configure rate limiting
- [ ] Set up backup and recovery
- [ ] Document deployment procedures
- [ ] Set up CI/CD pipeline

## Step 14: Documentation Review

Read through documentation:

- [ ] README.md - Main documentation
- [ ] QUICKSTART.md - Quick start guide
- [ ] ARCHITECTURE.md - Architecture overview
- [ ] This checklist - Installation steps

## Final Verification

- [ ] Server starts without errors
- [ ] Health check endpoint works
- [ ] API documentation accessible
- [ ] Test script passes most tests
- [ ] Logs are being written
- [ ] Can test with real requests

## Post-Installation

- [ ] Bookmark API documentation URL
- [ ] Save useful curl commands
- [ ] Set up development workflow
- [ ] Configure IDE/editor for Python
- [ ] Review API endpoints for integration
- [ ] Plan frontend integration

## Getting Help

If you encounter issues:

1. [ ] Check error messages in console
2. [ ] Review log files in `logs/` directory
3. [ ] Run `python config.py` to check configuration
4. [ ] Run `python test_api.py` to test endpoints
5. [ ] Review documentation for similar issues
6. [ ] Check Google Cloud Console for Vision API status
7. [ ] Verify API keys are valid and active
8. [ ] Contact development team if issues persist

---

## Success Criteria

You're ready to proceed when:

✓ Server starts without errors
✓ Health check returns healthy status
✓ API documentation is accessible
✓ Test script shows passing tests
✓ Can make successful API calls
✓ Logs are being written correctly

---

**Congratulations!** If all items are checked, your mySahara Health Backend is successfully installed and ready for development or production use.

For next steps, see the QUICKSTART.md or README.md files.

---

**Last Updated**: 2025-10-12
**Version**: 1.0.0
