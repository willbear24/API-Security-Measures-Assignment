class TestLoginRateLimiting:
    """Evidence that POST /auth/login enforces its 5/minute rate limit."""

    def test_eleventh_rapid_login_attempt_is_rate_limited(self, client):
        payload = {"email": "nonexistent@example.com", "password": "wrongpassword"}

        responses = [client.post("/auth/login", json=payload) for _ in range(11)]

        assert all(response.status_code == 401 for response in responses[:5])
        assert all(response.status_code == 429 for response in responses[5:])
        assert responses[-1].status_code == 429
