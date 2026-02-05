#!/usr/bin/env python3
"""
Quick verification script for DMT API after deployment
Run this to test if your Vercel deployment is working correctly
"""

import requests
import json
import sys

# Change this to your Vercel deployment URL
BASE_URL = input("Enter your Vercel deployment URL (e.g., https://dmt.vercel.app): ").strip()
if not BASE_URL:
    print("❌ No URL provided")
    sys.exit(1)

if not BASE_URL.startswith("http"):
    BASE_URL = "https://" + BASE_URL

print(f"\n🔍 Testing API at: {BASE_URL}\n")

def test_endpoint(method, path, data=None, name=""):
    """Test an API endpoint"""
    try:
        url = f"{BASE_URL}{path}"
        if method == "GET":
            resp = requests.get(url, timeout=10)
        elif method == "POST":
            resp = requests.post(url, json=data, timeout=10)
        
        if resp.status_code in [200, 201, 400, 401]:
            print(f"✅ {name}: {resp.status_code}")
            return True
        else:
            print(f"❌ {name}: {resp.status_code} - {resp.text[:100]}")
            return False
    except Exception as e:
        print(f"❌ {name}: {str(e)[:100]}")
        return False

# Test 1: Frontend accessibility
print("📋 Frontend Tests:")
test_endpoint("GET", "/", name="Home page")
test_endpoint("GET", "/dashboard.html", name="Dashboard")
test_endpoint("GET", "/admin.html", name="Admin panel")
test_endpoint("GET", "/analytics.html", name="Analytics")

# Test 2: API endpoints
print("\n🔌 API Tests:")
test_endpoint("GET", "/programmes/", name="Get programmes")

# Test 3: Authentication
print("\n🔐 Auth Tests:")
test_endpoint("POST", "/auth/request-otp", 
              data={"email": "test@example.com"},
              name="Request OTP")

# Test 4: Reports
print("\n📊 Report Tests:")
test_endpoint("GET", "/reports/", name="Get reports (requires auth)")

print("\n" + "="*50)
print("💡 Tips:")
print("  - If 'Get reports' fails, that's OK - it requires authentication")
print("  - Check Vercel logs for detailed errors: vercel.com/dashboard")
print("  - Test login functionality in browser")
print("  - Try submitting a report and check if admin gets email")
print("="*50 + "\n")
