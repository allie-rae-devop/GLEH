"""
Phase 1 P4: Comprehensive Rate Limiting Test Suite
Tests rate limiting on authentication endpoints (login, register).
"""
import pytest
import time
from datetime import datetime, timedelta
from src.app import auth_attempts
from src.models import User


class TestRateLimitingLogin:
    """Test rate limiting on login endpoint."""

    def test_rate_limit_login_enforcement(self, client, app, csrf_token):
        """Test that login rate limit (5 per minute) is enforced."""
        # Create a test user first
        with app.app_context():
            user = User(username='ratelimituser')
            user.set_password('Password123')
            from src.app import db
            db.session.add(user)
            db.session.commit()

        # Clear any existing rate limit data
        auth_attempts.clear()

        # Make 5 login attempts (should all be allowed, though fail auth)
        for i in range(5):
            response = client.post('/api/login',
                                  json={'username': 'ratelimituser', 'password': 'WrongPassword'},
                                  headers={'X-CSRFToken': csrf_token})
            # Should return 401 (Unauthorized) but not 429 (rate limited)
            assert response.status_code == 401, f"Attempt {i+1} was rate limited prematurely"

        # 6th attempt should be rate limited
        response = client.post('/api/login',
                              json={'username': 'ratelimituser', 'password': 'WrongPassword'},
                              headers={'X-CSRFToken': csrf_token})

        assert response.status_code == 429, "Rate limit not enforced after 5 attempts"
        data = response.get_json()
        assert 'error' in data
        assert 'too many' in data['error'].lower()

    def test_rate_limit_login_successful_attempts(self, client, app, csrf_token):
        """Test that successful login attempts are also rate limited."""
        # Create a test user
        with app.app_context():
            user = User(username='successuser')
            user.set_password('Password123')
            from src.app import db
            db.session.add(user)
            db.session.commit()

        # Clear rate limit data
        auth_attempts.clear()

        # Make 5 successful login attempts
        for i in range(5):
            response = client.post('/api/login',
                                  json={'username': 'successuser', 'password': 'Password123'},
                                  headers={'X-CSRFToken': csrf_token})
            assert response.status_code == 200, f"Successful login {i+1} failed"

        # 6th attempt should be rate limited
        response = client.post('/api/login',
                              json={'username': 'successuser', 'password': 'Password123'},
                              headers={'X-CSRFToken': csrf_token})

        assert response.status_code == 429, "Rate limit not enforced on successful logins"

    def test_rate_limit_login_mixed_credentials(self, client, app, csrf_token):
        """Test rate limiting with mixed valid/invalid credentials."""
        # Create users
        with app.app_context():
            from src.app import db
            user1 = User(username='mixeduser1')
            user1.set_password('Password123')
            user2 = User(username='mixeduser2')
            user2.set_password('Password123')
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()

        # Clear rate limit data
        auth_attempts.clear()

        # Make mixed attempts (all from same IP)
        attempts = [
            ('mixeduser1', 'Password123'),  # Valid
            ('mixeduser1', 'WrongPassword'),  # Invalid
            ('mixeduser2', 'Password123'),  # Valid, different user
            ('nonexistent', 'Password123'),  # Non-existent user
            ('mixeduser2', 'WrongPassword'),  # Invalid
        ]

        for username, password in attempts:
            response = client.post('/api/login',
                                  json={'username': username, 'password': password},
                                  headers={'X-CSRFToken': csrf_token})
            assert response.status_code in [200, 401], "Unexpected status in mixed attempts"

        # 6th attempt should be rate limited
        response = client.post('/api/login',
                              json={'username': 'mixeduser1', 'password': 'Password123'},
                              headers={'X-CSRFToken': csrf_token})

        assert response.status_code == 429


class TestRateLimitingRegister:
    """Test rate limiting on register endpoint."""

    def test_rate_limit_register_enforcement(self, client, csrf_token):
        """Test that register rate limit (5 per minute) is enforced."""
        # Clear rate limit data
        auth_attempts.clear()

        # Make 5 registration attempts
        for i in range(5):
            response = client.post('/api/register',
                                  json={'username': f'newuser{i}', 'password': 'Password123'},
                                  headers={'X-CSRFToken': csrf_token})
            # Should succeed (201 Created)
            assert response.status_code == 201, f"Registration {i+1} failed unexpectedly"

        # 6th attempt should be rate limited
        response = client.post('/api/register',
                              json={'username': 'newuser6', 'password': 'Password123'},
                              headers={'X-CSRFToken': csrf_token})

        assert response.status_code == 429, "Rate limit not enforced on register"
        data = response.get_json()
        assert 'error' in data
        assert 'too many' in data['error'].lower()

    def test_rate_limit_register_invalid_data(self, client, csrf_token):
        """Test that invalid registration attempts count toward rate limit."""
        # Clear rate limit data
        auth_attempts.clear()

        # Make 5 invalid registration attempts
        for i in range(5):
            response = client.post('/api/register',
                                  json={'username': 'ab', 'password': '123'},  # Too short
                                  headers={'X-CSRFToken': csrf_token})
            # Should fail validation (400 Bad Request) but still count toward rate limit
            assert response.status_code == 400

        # 6th attempt should be rate limited
        response = client.post('/api/register',
                              json={'username': 'validuser', 'password': 'Password123'},
                              headers={'X-CSRFToken': csrf_token})

        assert response.status_code == 429, "Invalid attempts didn't count toward rate limit"


class TestRateLimitReset:
    """Test rate limit reset and timeout behavior."""

    def test_rate_limit_resets_after_timeout(self, client, app, csrf_token):
        """Test that rate limit resets after 1 minute timeout."""
        # This test would take 60+ seconds to run, so we'll simulate it
        # by manipulating the auth_attempts data structure

        from datetime import datetime, timedelta
        from src.app import auth_attempts

        # Clear rate limit data
        auth_attempts.clear()

        # Create a test user
        with app.app_context():
            user = User(username='timeoutuser')
            user.set_password('Password123')
            from src.app import db
            db.session.add(user)
            db.session.commit()

        # Simulate 5 old attempts (older than 1 minute)
        old_time = datetime.utcnow() - timedelta(minutes=2)
        test_ip = '127.0.0.1'
        auth_attempts[test_ip] = [old_time] * 5

        # New attempt should succeed because old attempts expired
        response = client.post('/api/login',
                              json={'username': 'timeoutuser', 'password': 'Password123'},
                              headers={'X-CSRFToken': csrf_token})

        # Should succeed (not rate limited)
        assert response.status_code == 200, "Rate limit didn't reset after timeout"

    def test_rate_limit_cleanup_removes_old_attempts(self, client, csrf_token):
        """Test that rate limit tracking removes old attempts."""
        from datetime import datetime, timedelta

        # Clear and setup test data
        auth_attempts.clear()
        test_ip = '127.0.0.1'

        # Add old attempts
        old_time = datetime.utcnow() - timedelta(minutes=2)
        auth_attempts[test_ip] = [old_time] * 3

        # Make a new request (should trigger cleanup)
        response = client.post('/api/register',
                              json={'username': 'cleanuptest', 'password': 'Password123'},
                              headers={'X-CSRFToken': csrf_token})

        # Should succeed
        assert response.status_code == 201

        # Old attempts should be cleaned up
        # New tracking should only have 1 attempt
        assert len(auth_attempts[test_ip]) == 1


class TestRateLimitHeaders:
    """Test rate limit response headers."""

    def test_rate_limit_error_message(self, client, csrf_token):
        """Test that rate limit error returns clear message."""
        # Clear rate limit data
        auth_attempts.clear()

        # Exhaust rate limit
        for i in range(5):
            client.post('/api/login',
                       json={'username': 'test', 'password': 'test'},
                       headers={'X-CSRFToken': csrf_token})

        # Get rate limit response
        response = client.post('/api/login',
                              json={'username': 'test', 'password': 'test'},
                              headers={'X-CSRFToken': csrf_token})

        assert response.status_code == 429
        data = response.get_json()
        assert 'error' in data

        # Error message should be user-friendly
        error_msg = data['error'].lower()
        assert 'too many' in error_msg or 'rate limit' in error_msg
        assert 'minute' in error_msg or 'try again' in error_msg


class TestRateLimitMultipleIPs:
    """Test rate limiting behavior with multiple IP addresses."""

    def test_rate_limit_per_ip_isolation(self, client, app, csrf_token):
        """Test that rate limits are tracked per IP address."""
        # This test is limited by test client IP simulation
        # In a real scenario, different IPs should have separate limits

        # Create test user
        with app.app_context():
            user = User(username='multiipuser')
            user.set_password('Password123')
            from src.app import db
            db.session.add(user)
            db.session.commit()

        # Clear rate limit data and import
        from src.app import auth_attempts, check_rate_limit
        from datetime import datetime
        auth_attempts.clear()

        # Simulate different IPs by manually manipulating auth_attempts
        # IP 1: Exhaust rate limit
        ip1 = '192.168.1.1'
        now = datetime.utcnow()
        auth_attempts[ip1] = [now] * 5

        # IP 2: Should still be able to make requests
        ip2 = '192.168.1.2'
        auth_attempts[ip2] = [now] * 2

        # Verify IP 1 is blocked (within app context)
        with app.app_context():
            is_allowed, error = check_rate_limit(ip1)
            assert not is_allowed, "IP 1 should be rate limited"

            # Verify IP 2 is allowed
            is_allowed, error = check_rate_limit(ip2)
            assert is_allowed, "IP 2 should not be rate limited"


class TestRateLimitEdgeCases:
    """Test edge cases and corner scenarios for rate limiting."""

    def test_rate_limit_rapid_fire_requests(self, client, csrf_token):
        """Test rate limiting with rapid sequential requests."""
        # Clear rate limit data
        auth_attempts.clear()

        # Make rapid requests in quick succession
        responses = []
        for i in range(7):
            response = client.post('/api/register',
                                  json={'username': f'rapiduser{i}', 'password': 'Password123'},
                                  headers={'X-CSRFToken': csrf_token})
            responses.append(response.status_code)

        # First 5 should succeed (201)
        assert all(status == 201 for status in responses[:5]), "First 5 requests should succeed"

        # 6th and 7th should be rate limited (429)
        assert responses[5] == 429, "6th request should be rate limited"
        assert responses[6] == 429, "7th request should be rate limited"

    def test_rate_limit_boundary_condition(self, client, app, csrf_token):
        """Test rate limiting at exact boundary (5 attempts)."""
        # Clear rate limit data
        auth_attempts.clear()

        # Make exactly 5 requests
        for i in range(5):
            response = client.post('/api/register',
                                  json={'username': f'boundaryuser{i}', 'password': 'Password123'},
                                  headers={'X-CSRFToken': csrf_token})
            assert response.status_code == 201, f"Request {i+1} should succeed"

        # Verify that we're at the limit (must be done within app context)
        from src.app import check_rate_limit
        with app.app_context():
            is_allowed, _ = check_rate_limit('127.0.0.1')
            assert not is_allowed, "Should be at rate limit after 5 requests"

    def test_rate_limit_concurrent_requests_tracking(self, client, csrf_token):
        """Test that concurrent requests are tracked correctly."""
        # Clear rate limit data and import
        from src.app import auth_attempts
        auth_attempts.clear()

        # Make multiple requests that should all be tracked
        for i in range(3):
            response = client.post('/api/register',
                                  json={'username': f'concurrentuser{i}', 'password': 'Password123'},
                                  headers={'X-CSRFToken': csrf_token})
            assert response.status_code == 201

        # Verify tracking count
        test_ip = '127.0.0.1'
        assert test_ip in auth_attempts
        assert len(auth_attempts[test_ip]) == 3, "Should have 3 tracked attempts"

    def test_rate_limit_does_not_affect_get_requests(self, client):
        """Test that rate limiting doesn't affect GET requests."""
        # Clear rate limit data
        auth_attempts.clear()

        # Make many GET requests (should not be rate limited)
        for i in range(20):
            response = client.get('/')
            assert response.status_code == 200, f"GET request {i+1} should succeed"

        response = client.get('/api/content')
        assert response.status_code == 200, "GET to API should succeed"

    def test_rate_limit_with_missing_credentials(self, client, csrf_token):
        """Test rate limiting with missing username/password."""
        # Clear rate limit data
        auth_attempts.clear()

        # Make 5 requests with missing credentials
        for i in range(5):
            response = client.post('/api/login',
                                  json={},  # Empty body
                                  headers={'X-CSRFToken': csrf_token})
            # Should fail validation (400) but still count toward rate limit
            assert response.status_code == 400

        # 6th attempt should be rate limited
        response = client.post('/api/login',
                              json={},
                              headers={'X-CSRFToken': csrf_token})

        assert response.status_code == 429


class TestRateLimitSecurityBypass:
    """Test that rate limiting cannot be bypassed."""

    def test_rate_limit_bypass_with_different_users(self, client, app, csrf_token):
        """Test that rate limit cannot be bypassed by changing usernames."""
        # Rate limiting is per IP, not per username

        # Clear rate limit data
        auth_attempts.clear()

        # Create multiple users
        with app.app_context():
            from src.app import db
            for i in range(6):
                user = User(username=f'bypassuser{i}')
                user.set_password('Password123')
                db.session.add(user)
            db.session.commit()

        # Try to bypass by using different usernames
        for i in range(5):
            response = client.post('/api/login',
                                  json={'username': f'bypassuser{i}', 'password': 'Password123'},
                                  headers={'X-CSRFToken': csrf_token})
            assert response.status_code == 200, f"Login {i+1} should succeed"

        # 6th attempt should still be rate limited
        response = client.post('/api/login',
                              json={'username': 'bypassuser5', 'password': 'Password123'},
                              headers={'X-CSRFToken': csrf_token})

        assert response.status_code == 429, "Rate limit should not be bypassed with different usernames"

    def test_rate_limit_bypass_with_false_headers(self, client, csrf_token):
        """Test that rate limit cannot be bypassed with spoofed headers."""
        # Clear rate limit data
        auth_attempts.clear()

        # Try to bypass by adding fake forwarding headers
        for i in range(5):
            response = client.post('/api/register',
                                  json={'username': f'spoofuser{i}', 'password': 'Password123'},
                                  headers={'X-CSRFToken': csrf_token,
                                          'X-Forwarded-For': f'192.168.{i}.{i}',
                                          'X-Real-IP': f'10.0.{i}.{i}'})
            assert response.status_code == 201

        # 6th attempt should still be rate limited (headers should be ignored in test)
        response = client.post('/api/register',
                              json={'username': 'spoofuser5', 'password': 'Password123'},
                              headers={'X-CSRFToken': csrf_token,
                                      'X-Forwarded-For': '192.168.5.5'})

        assert response.status_code == 429, "Rate limit should not be bypassed with spoofed headers"
