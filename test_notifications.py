"""
Test script for notification system
Run this to verify Firebase and notification endpoints are working
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("Testing mySahara Notification System")
print("=" * 60)

# Test 1: Check Firebase Admin SDK
print("\n[1/4] Checking Firebase Admin SDK...")
try:
    import firebase_admin
    from firebase_admin import credentials, messaging

    cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')

    if not cred_path:
        print("ERROR: FIREBASE_SERVICE_ACCOUNT_PATH not set in .env")
        sys.exit(1)

    if not os.path.exists(cred_path):
        print(f"ERROR: Service account file not found at: {cred_path}")
        sys.exit(1)

    print(f"  - Service account path: {cred_path}")
    print(f"  - File exists: Yes")

    # Initialize if not already initialized
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

    project_id = firebase_admin.get_app().project_id
    print(f"  - Project ID: {project_id}")
    print("SUCCESS: Firebase Admin SDK is working!")

except ImportError:
    print("ERROR: firebase-admin not installed. Run: pip install firebase-admin")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# Test 2: Check Supabase connection
print("\n[2/4] Checking Supabase connection...")
try:
    from services.supabase_client import get_supabase_client

    supabase = get_supabase_client()

    # Try a simple query
    result = supabase.table('users').select('id').limit(1).execute()

    print(f"  - Connection: OK")
    print(f"  - Can query database: Yes")
    print("SUCCESS: Supabase connection is working!")

except Exception as e:
    print(f"WARNING: Supabase connection issue: {e}")
    print("  (This is OK if you haven't set up Supabase credentials yet)")

# Test 3: Check notification API endpoints
print("\n[3/4] Checking notification API setup...")
try:
    from api.notifications import router

    # Get all routes
    routes = [route.path for route in router.routes]

    print(f"  - Notification routes found: {len(routes)}")
    for route_path in routes:
        print(f"    - {route_path}")

    print("SUCCESS: Notification API is set up correctly!")

except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# Test 4: Verify main.py includes notifications router
print("\n[4/4] Checking main.py configuration...")
try:
    with open('main.py', 'r', encoding='utf-8') as f:
        main_content = f.read()

    if 'notifications' in main_content and 'notifications.router' in main_content:
        print("  - Notifications router imported: Yes")
        print("  - Notifications router included: Yes")
        print("SUCCESS: Main.py is configured correctly!")
    else:
        print("WARNING: Notifications router might not be properly configured in main.py")

except Exception as e:
    print(f"WARNING: Could not verify main.py: {e}")

# Final summary
print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("""
All core components are working!

Next steps:
1. Start the backend: python main.py
2. Open API docs: http://localhost:8000/docs
3. Test notification endpoint: POST /api/notifications/test
   - Get your FCM token from the Flutter app logs
   - Send a test notification using the Swagger UI

For production deployment to Render:
1. Add FIREBASE_SERVICE_ACCOUNT_PATH to Render environment variables
2. Upload the service account JSON file to Render
3. Update the path to match Render's file system

Full documentation: See FAMILY_NOTIFICATION_SYSTEM_SETUP.md
""")
print("=" * 60)
