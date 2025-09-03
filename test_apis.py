"""
Simple API test script to verify all endpoints are working
"""
import requests
import json

# Base URL for your API
BASE_URL = "http://localhost:8000/api"

def test_api_endpoints():
    """Test various API endpoints"""
    
    print("🚀 Testing Organic Green API endpoints...\n")
    
    # Test products endpoint
    print("1. Testing Products API...")
    try:
        response = requests.get(f"{BASE_URL}/products/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Products API working - Found {data.get('count', 0)} products")
        else:
            print(f"   ❌ Products API failed - Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Products API error: {e}")
    
    # Test categories endpoint
    print("\n2. Testing Categories API...")
    try:
        response = requests.get(f"{BASE_URL}/products/categories/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Categories API working - Found {len(data)} categories")
        else:
            print(f"   ❌ Categories API failed - Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Categories API error: {e}")
    
    # Test cart endpoints (anonymous)
    print("\n3. Testing Cart API (Anonymous)...")
    session_key = "test_session_123"
    headers = {"X-Session-Key": session_key}
    
    try:
        # Get cart
        response = requests.get(f"{BASE_URL}/cart/", headers=headers)
        if response.status_code == 200:
            print("   ✅ Cart GET working")
        else:
            print(f"   ❌ Cart GET failed - Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Cart API error: {e}")
    
    # Test orders endpoints
    print("\n4. Testing Orders API...")
    try:
        response = requests.get(f"{BASE_URL}/orders/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Orders API working - Found {data.get('count', 0)} orders")
        else:
            print(f"   ❌ Orders API failed - Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Orders API error: {e}")
    
    # Test orders info endpoint
    print("\n5. Testing Orders Info API...")
    try:
        response = requests.get(f"{BASE_URL}/orders/info/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Orders Info API working - {data.get('message', 'No message')}")
        else:
            print(f"   ❌ Orders Info API failed - Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Orders Info API error: {e}")
    
    # Test favorites endpoint
    print("\n6. Testing Favorites API...")
    try:
        response = requests.get(f"{BASE_URL}/favorites/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Favorites API working - Found {data.get('count', 0)} favorites")
        else:
            print(f"   ❌ Favorites API failed - Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Favorites API error: {e}")
    
    print("\n🎉 API testing completed!")
    print("\nNext steps:")
    print("1. Test with a frontend application")
    print("2. Add more products via admin interface")
    print("3. Test order creation flow")
    print("4. Test authentication endpoints")

if __name__ == "__main__":
    test_api_endpoints()
