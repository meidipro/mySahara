# Deploy Notification System to Render

## Quick Deployment Steps

### 1. Prepare Firebase Service Account for Render

You have two options:

#### Option A: Store JSON as Environment Variable (Recommended)
```bash
# Read the JSON file and copy its contents
cat mysahara-ff72c-firebase-adminsdk-fbsvc-3a7e58d258.json
```

Copy the entire JSON content. You'll paste this into Render.

#### Option B: Upload JSON File to Render
Upload the file directly via Render's file upload feature.

---

### 2. Update Backend Code for Render

The code is already configured to work with both local and Render environments.

The `api/notifications.py` file will:
1. First try to load from `FIREBASE_SERVICE_ACCOUNT_PATH` (file path)
2. If that fails, it will try to load from `FIREBASE_SERVICE_ACCOUNT_JSON` (JSON string)

---

### 3. Configure Render Environment Variables

Go to your Render dashboard → Your backend service → Environment

Add these variables:

#### Method A: Using JSON String (Easier)
```
FIREBASE_SERVICE_ACCOUNT_JSON=<paste entire JSON content here>
```

**OR**

#### Method B: Using File Path
```
FIREBASE_SERVICE_ACCOUNT_PATH=/etc/secrets/firebase-adminsdk.json
```

Then upload the JSON file using Render's "Add Secret File" feature:
- Secret File Path: `/etc/secrets/firebase-adminsdk.json`
- Contents: Paste your JSON file contents

---

### 4. Verify requirements.txt

Make sure `requirements.txt` includes:
```
firebase-admin>=6.5.0
```

✅ Already added!

---

### 5. Deploy to Render

#### Option 1: Auto-deploy from Git
```bash
cd backend
git add .
git commit -m "Add Firebase notification system"
git push origin main
```

Render will automatically detect changes and redeploy.

#### Option 2: Manual Deploy
Go to Render dashboard → Click "Manual Deploy" → Select branch

---

### 6. Verify Deployment

After deployment completes:

1. **Check Logs**
   ```
   Go to Render → Your Service → Logs
   ```

   Look for:
   ```
   ✓ Firebase Admin SDK initialized successfully
   ```

2. **Test API**
   ```
   Visit: https://your-app.onrender.com/docs
   ```

3. **Test Notification Endpoint**
   ```bash
   curl -X POST https://your-app.onrender.com/api/notifications/test \
     -H "Content-Type: application/json" \
     -d '{"token":"YOUR_FCM_TOKEN"}'
   ```

---

### 7. Update Flutter App Backend URL

Update your Flutter app to use the new Render URL:

```dart
// In your app config
const BACKEND_URL = 'https://your-app.onrender.com';
```

---

## Environment Variables Summary

Here are ALL the environment variables your backend needs on Render:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_KEY=your-service-role-key

# AI Services
GROQ_API_KEY=your-groq-key
GEMINI_API_KEY=your-gemini-key

# Firebase (Choose ONE method)
# Method A: JSON String
FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}

# OR Method B: File Path
FIREBASE_SERVICE_ACCOUNT_PATH=/etc/secrets/firebase-adminsdk.json

# Optional
PORT=8000
LOG_LEVEL=INFO
```

---

## Troubleshooting

### Issue: "Firebase Admin SDK not available"

**Solution:**
- Check that `firebase-admin>=6.5.0` is in requirements.txt
- Check Render build logs for installation errors
- Try manual deploy

### Issue: "Service account file not found"

**Solution (Method A - JSON String):**
1. Copy entire JSON file contents
2. Add as `FIREBASE_SERVICE_ACCOUNT_JSON` environment variable in Render
3. Update code to use JSON string (see code update below)

**Solution (Method B - File Path):**
1. Use Render's "Add Secret File" feature
2. Path: `/etc/secrets/firebase-adminsdk.json`
3. Set `FIREBASE_SERVICE_ACCOUNT_PATH=/etc/secrets/firebase-adminsdk.json`

### Issue: "Firebase initialization failed"

**Check:**
1. JSON is valid (no missing quotes, commas)
2. Environment variable is set correctly
3. No extra spaces or newlines in JSON
4. Restart the Render service after adding variables

---

## Code Update for JSON String Support

Update `backend/api/notifications.py` to support both methods:

```python
# Initialize Firebase Admin SDK
if FIREBASE_AVAILABLE and not firebase_admin._apps:
    try:
        # Method 1: Try loading from file path
        cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized from file")
        else:
            # Method 2: Try loading from JSON string (for Render)
            cred_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
            if cred_json:
                import json
                cred_dict = json.loads(cred_json)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized from JSON string")
            else:
                logger.warning("Firebase service account not configured")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
```

---

## Testing After Deployment

### 1. Test Basic Health
```bash
curl https://your-app.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "mySahara Health API is running"
}
```

### 2. Test Notification System
```bash
curl https://your-app.onrender.com/api/notifications/test \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"token":"YOUR_FCM_TOKEN_FROM_APP"}'
```

Expected response:
```json
{
  "success": true,
  "message_id": "..."
}
```

### 3. Test Family Daily Summary
```bash
curl https://your-app.onrender.com/api/notifications/family-daily-summary/USER_ID \
  -X POST
```

---

## Security Notes

### ⚠️ Important for Production

1. **Never commit Firebase JSON to Git**
   - Already in `.gitignore`
   - Only store in Render environment variables

2. **Use Render Secret Files**
   - More secure than environment variables
   - Automatically encrypted

3. **Rotate Keys Regularly**
   - Generate new service account keys every 90 days
   - Update in Render environment

4. **Use Service Role Key**
   - Don't use anon key for backend
   - Use service role key for Supabase

---

## Git Commands

```bash
# Navigate to backend directory
cd E:/mySahara/backend

# Check current status
git status

# Add all changes
git add .

# Commit with message
git commit -m "Add Firebase Cloud Messaging notification system

- Add firebase-admin to requirements.txt
- Add notification API endpoints for medications and vaccines
- Add family daily summary notification
- Add Supabase client service
- Update .env.example with Firebase configuration
"

# Push to remote
git push origin main

# If you need to set remote
git remote add origin https://github.com/your-username/your-repo.git
```

---

## Post-Deployment Checklist

- [ ] Firebase Admin SDK initializes successfully (check logs)
- [ ] Test notification endpoint works
- [ ] Family daily summary endpoint works
- [ ] Medication reminder endpoint works
- [ ] Vaccine reminder endpoint works
- [ ] Flutter app can reach backend
- [ ] Notifications arrive on device
- [ ] All environment variables are set
- [ ] No sensitive data in Git logs

---

## Support

If you encounter issues:
1. Check Render logs for errors
2. Verify environment variables are set
3. Test endpoints using Swagger UI at `/docs`
4. Check Firebase Console for any project issues

---

**Status: Ready for Deployment** ✅

Follow the steps above to deploy your notification system to Render!
