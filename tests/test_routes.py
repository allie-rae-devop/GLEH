"""Quick route accessibility test"""
from src.app import app

def test_routes():
    with app.test_client() as client:
        print("Testing routes with admin user session...")

        # Login as admin first
        response = client.post('/api/login', json={
            'username': 'admin',
            'password': 'Admin123'
        })
        print(f"\n1. Login: {response.status_code} - {response.json if response.status_code == 200 else 'FAILED'}")

        # Test profile page
        response = client.get('/profile')
        print(f"2. GET /profile: {response.status_code} - {'OK' if response.status_code == 200 else 'FAILED'}")

        # Test admin page
        response = client.get('/admin')
        print(f"3. GET /admin: {response.status_code} - {'OK' if response.status_code == 200 else 'FAILED'}")

        # Test profile API
        response = client.get('/api/profile')
        print(f"4. GET /api/profile: {response.status_code} - {'OK' if response.status_code == 200 else 'FAILED'}")

        print("\nIf all show 200, routes are working correctly.")

if __name__ == '__main__':
    test_routes()
