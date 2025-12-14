"""
End-to-End tests for Sock Graveyard API

Tests cover:
- User registration and login
- Sock upload
- Similarity search
- Match confirmation
- Sock deletion

Run with: pytest tests/test_e2e.py -v
"""

import pytest
import requests
import os
from io import BytesIO
from PIL import Image


# Test configuration
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:80")
API_URL = f"{BASE_URL}/api"


class TestE2EWorkflow:
    """End-to-end workflow tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data"""
        self.test_user = {
            "email": f"test_{os.urandom(4).hex()}@example.com",
            "username": f"testuser_{os.urandom(4).hex()}",
            "password": "testpassword123"
        }
        self.token = None
        self.sock_ids = []
    
    def create_test_image(self, color=(255, 0, 0), size=(500, 500)) -> BytesIO:
        """Create a test image"""
        image = Image.new('RGB', size, color)
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        return img_byte_arr
    
    def test_01_health_check(self):
        """Test health check endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✓ Health check passed: {data['version']}")
    
    def test_02_user_registration(self):
        """Test user registration"""
        response = requests.post(
            f"{API_URL}/auth/register",
            json=self.test_user
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == self.test_user["email"]
        assert data["username"] == self.test_user["username"]
        assert "hashed_password" not in data
        print(f"✓ User registered: {data['username']}")
    
    def test_03_user_login(self):
        """Test user login"""
        # First register
        requests.post(f"{API_URL}/auth/register", json=self.test_user)
        
        # Then login
        response = requests.post(
            f"{API_URL}/auth/login",
            data={
                "username": self.test_user["username"],
                "password": self.test_user["password"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        self.token = data["access_token"]
        print(f"✓ User logged in, token received")
    
    def test_04_get_current_user(self):
        """Test getting current user info"""
        # Register and login
        requests.post(f"{API_URL}/auth/register", json=self.test_user)
        login_response = requests.post(
            f"{API_URL}/auth/login",
            data={
                "username": self.test_user["username"],
                "password": self.test_user["password"]
            }
        )
        token = login_response.json()["access_token"]
        
        # Get user info
        response = requests.get(
            f"{API_URL}/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == self.test_user["username"]
        print(f"✓ Current user retrieved: {data['username']}")
    
    def test_05_upload_sock(self):
        """Test sock upload"""
        # Register and login
        requests.post(f"{API_URL}/auth/register", json=self.test_user)
        login_response = requests.post(
            f"{API_URL}/auth/login",
            data={
                "username": self.test_user["username"],
                "password": self.test_user["password"]
            }
        )
        token = login_response.json()["access_token"]
        
        # Upload sock
        test_image = self.create_test_image(color=(255, 0, 0))
        files = {"file": ("test_sock.jpg", test_image, "image/jpeg")}
        data = {"description": "Red test sock"}
        
        response = requests.post(
            f"{API_URL}/socks/",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        sock_data = response.json()
        assert "id" in sock_data
        assert sock_data["description"] == "Red test sock"
        print(f"✓ Sock uploaded: ID {sock_data['id']}")
    
    def test_06_list_socks(self):
        """Test listing socks"""
        # Register and login
        requests.post(f"{API_URL}/auth/register", json=self.test_user)
        login_response = requests.post(
            f"{API_URL}/auth/login",
            data={
                "username": self.test_user["username"],
                "password": self.test_user["password"]
            }
        )
        token = login_response.json()["access_token"]
        
        # Upload a sock
        test_image = self.create_test_image()
        files = {"file": ("test_sock.jpg", test_image, "image/jpeg")}
        requests.post(
            f"{API_URL}/socks/",
            files=files,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # List socks
        response = requests.get(
            f"{API_URL}/socks/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        socks = response.json()
        assert len(socks) > 0
        print(f"✓ Listed {len(socks)} sock(s)")
    
    def test_07_search_similar_socks(self):
        """Test similarity search"""
        # Register and login
        requests.post(f"{API_URL}/auth/register", json=self.test_user)
        login_response = requests.post(
            f"{API_URL}/auth/login",
            data={
                "username": self.test_user["username"],
                "password": self.test_user["password"]
            }
        )
        token = login_response.json()["access_token"]
        
        # Upload two similar socks
        headers = {"Authorization": f"Bearer {token}"}
        
        sock1_image = self.create_test_image(color=(255, 0, 0))
        files1 = {"file": ("sock1.jpg", sock1_image, "image/jpeg")}
        response1 = requests.post(f"{API_URL}/socks/", files=files1, headers=headers)
        sock1_id = response1.json()["id"]
        
        sock2_image = self.create_test_image(color=(255, 10, 10))
        files2 = {"file": ("sock2.jpg", sock2_image, "image/jpeg")}
        response2 = requests.post(f"{API_URL}/socks/", files=files2, headers=headers)
        
        # Search for matches
        response = requests.post(
            f"{API_URL}/socks/search",
            params={"sock_id": sock1_id, "threshold": 0.5},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        print(f"✓ Found {data['total']} match(es)")
    
    def test_08_confirm_match(self):
        """Test match confirmation"""
        # Register and login
        requests.post(f"{API_URL}/auth/register", json=self.test_user)
        login_response = requests.post(
            f"{API_URL}/auth/login",
            data={
                "username": self.test_user["username"],
                "password": self.test_user["password"]
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Upload two socks
        sock1_image = self.create_test_image(color=(0, 255, 0))
        files1 = {"file": ("sock1.jpg", sock1_image, "image/jpeg")}
        response1 = requests.post(f"{API_URL}/socks/", files=files1, headers=headers)
        sock1_id = response1.json()["id"]
        
        sock2_image = self.create_test_image(color=(0, 255, 0))
        files2 = {"file": ("sock2.jpg", sock2_image, "image/jpeg")}
        response2 = requests.post(f"{API_URL}/socks/", files=files2, headers=headers)
        sock2_id = response2.json()["id"]
        
        # Confirm match
        response = requests.post(
            f"{API_URL}/socks/match",
            json={"sock_id_1": sock1_id, "sock_id_2": sock2_id},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ Match confirmed: {sock1_id} <-> {sock2_id}")
    
    def test_09_delete_sock(self):
        """Test sock deletion"""
        # Register and login
        requests.post(f"{API_URL}/auth/register", json=self.test_user)
        login_response = requests.post(
            f"{API_URL}/auth/login",
            data={
                "username": self.test_user["username"],
                "password": self.test_user["password"]
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Upload a sock
        test_image = self.create_test_image()
        files = {"file": ("test_sock.jpg", test_image, "image/jpeg")}
        upload_response = requests.post(f"{API_URL}/socks/", files=files, headers=headers)
        sock_id = upload_response.json()["id"]
        
        # Delete sock
        response = requests.delete(
            f"{API_URL}/socks/{sock_id}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sock_id"] == sock_id
        print(f"✓ Sock deleted: ID {sock_id}")
    
    def test_10_unauthorized_access(self):
        """Test that endpoints require authentication"""
        # Try to list socks without token
        response = requests.get(f"{API_URL}/socks/")
        assert response.status_code == 401
        print("✓ Unauthorized access properly rejected")
    
    def test_11_duplicate_registration(self):
        """Test that duplicate registration is rejected"""
        # Register user
        requests.post(f"{API_URL}/auth/register", json=self.test_user)
        
        # Try to register again
        response = requests.post(f"{API_URL}/auth/register", json=self.test_user)
        assert response.status_code == 400
        print("✓ Duplicate registration properly rejected")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
