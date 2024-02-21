import httpx
import pytest

@pytest.mark.asyncio
async def test_default_refresh_token_async():
    async with httpx.AsyncClient() as client:
        login_url = "http://127.0.0.1:8000/login"
        login_data = {"username": "default", "password": "default"}
        response = await client.post(login_url, data=login_data)

        assert response.status_code == 200
        assert "access_token" in response.json()

        token = response.json().get("access_token")
        cookies = response.cookies.get("refresh_token")

        url = "http://127.0.0.1:8000/key"
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get(url, headers=headers, cookies={"refresh_token": cookies})
        
        assert response.status_code == 200

        url = "http://127.0.0.1:8000/token/refresh"  
        # Set the Authorization header with the access token
        headers = {"Authorization": f"Bearer {token}"}
        # Prepare the request with both headers and cookies
        response = await client.post(url, headers=headers, cookies={"refresh_token": cookies})
        
        assert response.status_code == 200
        assert "access_token" in response.json()
        
        token = response.json().get("access_token")
        cookies = response.cookies.get("refresh_token")

        url = "http://127.0.0.1:8000/logout"
        # Set the Authorization header with the access token
        headers = {"Authorization": f"Bearer {token}"}
        # Include the httponly cookie in the request
        response = await client.post(url, headers=headers, cookies={"refresh_token": cookies})
        
        assert response.status_code == 200

        url = "http://127.0.0.1:8000/token/refresh"
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(url, headers=headers, cookies={"refresh_token": cookies})
        
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_admin_refresh_token_async():
    async with httpx.AsyncClient() as client:
        login_url = "http://127.0.0.1:8000/login"
        login_data = {"username": "admin", "password": "default_admin"}
        response = await client.post(login_url, data=login_data)

        assert response.status_code == 200
        assert "access_token" in response.json()

        token = response.json().get("access_token")
        cookies = response.cookies.get("refresh_token")

        url = "http://127.0.0.1:8000/manage/scopes"
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get(url, headers=headers, cookies={"refresh_token": cookies})
        
        assert response.status_code == 200

        url = "http://127.0.0.1:8000/token/refresh"  
        # Set the Authorization header with the access token
        headers = {"Authorization": f"Bearer {token}"}
        # Prepare the request with both headers and cookies
        response = await client.post(url, headers=headers, cookies={"refresh_token": cookies})
        
        assert response.status_code == 200
        assert "access_token" in response.json()
        
        token = response.json().get("access_token")
        cookies = response.cookies.get("refresh_token")

        url = "http://127.0.0.1:8000/logout"
        # Set the Authorization header with the access token
        headers = {"Authorization": f"Bearer {token}"}
        # Include the httponly cookie in the request
        response = await client.post(url, headers=headers, cookies={"refresh_token": cookies})
        
        assert response.status_code == 200

        url = "http://127.0.0.1:8000/token/refresh"
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(url, headers=headers, cookies={"refresh_token": cookies})
        
        assert response.status_code == 401
