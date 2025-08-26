"""
Simple test script to verify authentication API
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_simple_registration():
    """Test simple user registration"""
    print("=== Oddiy ro'yxatdan o'tishni test qilish ===")
    
    data = {
        "username": "test_user_123",
        "password": "test123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/simple/", json=data)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 201:
        return response.json()
    return None

def test_login(username, password):
    """Test user login"""
    print("\n=== Tizimga kirishni test qilish ===")
    
    data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=data)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        return response.json()
    return None

def test_profile(access_token):
    """Test profile access"""
    print("\n=== Profilni olishni test qilish ===")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_auth_status(access_token):
    """Test auth status"""
    print("\n=== Autentifikatsiya holatini test qilish ===")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(f"{BASE_URL}/auth/status/", headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def main():
    """Run all tests"""
    try:
        # Test registration
        registration_response = test_simple_registration()
        
        if registration_response:
            access_token = registration_response['tokens']['access']
            username = registration_response['user']['username']
            
            # Test login
            login_response = test_login(username, "test123")
            
            # Test profile
            test_profile(access_token)
            
            # Test auth status
            test_auth_status(access_token)
            
            print("\n=== Barcha testlar muvaffaqiyatli o'tdi! ===")
        else:
            print("Ro'yxatdan o'tishda xato!")
            
    except requests.exceptions.ConnectionError:
        print("Xato: Server ishlamayapti. Avval 'python manage.py runserver' ni ishga tushiring.")
    except Exception as e:
        print(f"Xato: {e}")

if __name__ == "__main__":
    main()
