"""
Simple test script to verify API endpoints are working.
Run this after starting the server to test basic functionality.
"""

import requests
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


def print_result(endpoint: str, success: bool, response: Dict[Any, Any] = None):
    """Print test result."""
    status = "✓ PASS" if success else "✗ FAIL"
    print(f"{status} - {endpoint}")
    if response and not success:
        print(f"    Error: {response}")
    print()


def test_health_check():
    """Test health check endpoint."""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        success = response.status_code == 200 and response.json().get("status") == "healthy"
        print_result("GET /health", success, response.json())
        return success
    except Exception as e:
        print_result("GET /health", False, {"error": str(e)})
        return False


def test_root():
    """Test root endpoint."""
    print("Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        success = response.status_code == 200
        print_result("GET /", success, response.json())
        return success
    except Exception as e:
        print_result("GET /", False, {"error": str(e)})
        return False


def test_ai_chat():
    """Test AI chat endpoint."""
    print("Testing AI chat...")
    try:
        payload = {
            "message": "What is diabetes?",
            "language": "en",
            "use_medical_mode": True
        }
        response = requests.post(f"{BASE_URL}/api/ai/chat", json=payload)
        result = response.json()
        success = response.status_code == 200 and result.get("success", False)
        print_result("POST /api/ai/chat", success, result)
        if success:
            print(f"    Response: {result.get('message', '')[:100]}...")
            print()
        return success
    except Exception as e:
        print_result("POST /api/ai/chat", False, {"error": str(e)})
        return False


def test_conversation_starters():
    """Test conversation starters endpoint."""
    print("Testing conversation starters...")
    try:
        response = requests.get(f"{BASE_URL}/api/ai/conversation-starters?language=en")
        result = response.json()
        success = response.status_code == 200 and result.get("success", False)
        print_result("GET /api/ai/conversation-starters", success, result)
        return success
    except Exception as e:
        print_result("GET /api/ai/conversation-starters", False, {"error": str(e)})
        return False


def test_health_tips():
    """Test health tips endpoint."""
    print("Testing health tips...")
    try:
        response = requests.get(f"{BASE_URL}/api/health/tips?category=nutrition&language=en")
        result = response.json()
        success = response.status_code == 200 and result.get("success", False)
        print_result("GET /api/health/tips", success, result)
        return success
    except Exception as e:
        print_result("GET /api/health/tips", False, {"error": str(e)})
        return False


def test_health_categories():
    """Test health categories endpoint."""
    print("Testing health categories...")
    try:
        response = requests.get(f"{BASE_URL}/api/health/categories?language=en")
        result = response.json()
        success = response.status_code == 200 and result.get("success", False)
        print_result("GET /api/health/categories", success, result)
        return success
    except Exception as e:
        print_result("GET /api/health/categories", False, {"error": str(e)})
        return False


def test_symptom_analysis():
    """Test symptom analysis endpoint."""
    print("Testing symptom analysis...")
    try:
        payload = {
            "symptoms": ["fever", "cough"],
            "duration": "2 days",
            "severity": "mild",
            "age": 30
        }
        response = requests.post(f"{BASE_URL}/api/health/analyze-symptoms", json=payload)
        result = response.json()
        success = response.status_code == 200 and result.get("success", False)
        print_result("POST /api/health/analyze-symptoms", success, result)
        if success:
            print(f"    Risk Level: {result.get('risk_level', 'N/A')}")
            print()
        return success
    except Exception as e:
        print_result("POST /api/health/analyze-symptoms", False, {"error": str(e)})
        return False


def test_emergency_symptoms():
    """Test emergency symptoms endpoint."""
    print("Testing emergency symptoms...")
    try:
        response = requests.get(f"{BASE_URL}/api/health/emergency-symptoms?language=en")
        result = response.json()
        success = response.status_code == 200 and result.get("success", False)
        print_result("GET /api/health/emergency-symptoms", success, result)
        return success
    except Exception as e:
        print_result("GET /api/health/emergency-symptoms", False, {"error": str(e)})
        return False


def test_medical_term_explanation():
    """Test medical term explanation endpoint."""
    print("Testing medical term explanation...")
    try:
        payload = {
            "term": "hypertension",
            "language": "en",
            "simple_explanation": True
        }
        response = requests.post(f"{BASE_URL}/api/ai/explain-medical-term", json=payload)
        result = response.json()
        success = response.status_code == 200 and result.get("success", False)
        print_result("POST /api/ai/explain-medical-term", success, result)
        if success:
            print(f"    Explanation: {result.get('explanation', '')[:100]}...")
            print()
        return success
    except Exception as e:
        print_result("POST /api/ai/explain-medical-term", False, {"error": str(e)})
        return False


def run_all_tests():
    """Run all API tests."""
    print("=" * 60)
    print("mySahara Health Backend API Tests")
    print("=" * 60)
    print()

    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("❌ Server is not responding correctly!")
            print("Please ensure the server is running: python main.py")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server!")
        print("Please ensure the server is running: python main.py")
        return
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return

    print("✓ Server is running!\n")

    # Run tests
    tests = [
        ("Root Endpoint", test_root),
        ("Health Check", test_health_check),
        ("AI Chat", test_ai_chat),
        ("Conversation Starters", test_conversation_starters),
        ("Health Tips", test_health_tips),
        ("Health Categories", test_health_categories),
        ("Symptom Analysis", test_symptom_analysis),
        ("Emergency Symptoms", test_emergency_symptoms),
        ("Medical Term Explanation", test_medical_term_explanation),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ FAIL - {test_name}: {str(e)}\n")
            results.append((test_name, False))

    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")

    print()
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Your API is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")

    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
