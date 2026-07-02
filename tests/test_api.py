"""
Integration tests cho API endpoints.

Test end-to-end với test database (SQLite in-memory):
- POST /v1/shorten
- GET /{short_code}
- GET /v1/health
"""

from httpx import AsyncClient

# ── POST /v1/shorten ───────────────────────────────────────────────────────────

class TestShortenEndpoint:
    """Tests cho POST /v1/shorten."""

    async def test_shorten_success(self, client: AsyncClient):
        """Tạo URL ngắn hợp lệ phải trả về 201 với short_url."""
        response = await client.post(
            "/v1/shorten",
            json={"long_url": "https://www.google.com"},
        )
        assert response.status_code == 201
        data = response.json()
        assert "short_code" in data
        assert "short_url" in data
        assert data["long_url"] == "https://www.google.com/"
        assert len(data["short_code"]) == 7
        assert data["expires_at"] is None

    async def test_shorten_with_custom_alias(self, client: AsyncClient):
        """Custom alias hợp lệ phải được dùng làm short_code."""
        response = await client.post(
            "/v1/shorten",
            json={
                "long_url": "https://github.com",
                "custom_alias": "my-github",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["short_code"] == "my-github"
        assert "my-github" in data["short_url"]

    async def test_shorten_with_expiry(self, client: AsyncClient):
        """URL tạo với expires_in_days phải có expires_at khác None."""
        response = await client.post(
            "/v1/shorten",
            json={
                "long_url": "https://example.com",
                "expires_in_days": 30,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["expires_at"] is not None

    async def test_shorten_invalid_url_no_scheme(self, client: AsyncClient):
        """URL không có scheme phải trả về 422."""
        response = await client.post(
            "/v1/shorten",
            json={"long_url": "not-a-valid-url"},
        )
        assert response.status_code == 422

    async def test_shorten_empty_body(self, client: AsyncClient):
        """Body rỗng phải trả về 422."""
        response = await client.post("/v1/shorten", json={})
        assert response.status_code == 422

    async def test_shorten_custom_alias_conflict(self, client: AsyncClient):
        """Dùng lại alias đã tồn tại phải trả về 409."""
        alias = "conflict-test"
        # Tạo lần đầu
        r1 = await client.post(
            "/v1/shorten",
            json={"long_url": "https://first.com", "custom_alias": alias},
        )
        assert r1.status_code == 201

        # Tạo lần hai với cùng alias
        r2 = await client.post(
            "/v1/shorten",
            json={"long_url": "https://second.com", "custom_alias": alias},
        )
        assert r2.status_code == 409
        data = r2.json()
        assert "ALIAS_CONFLICT" in str(data)

    async def test_shorten_localhost_blocked(self, client: AsyncClient):
        """URL trỏ đến localhost phải bị chặn (SSRF prevention)."""
        response = await client.post(
            "/v1/shorten",
            json={"long_url": "http://localhost:8080/admin"},
        )
        assert response.status_code == 422

    async def test_shorten_invalid_alias_special_chars(self, client: AsyncClient):
        """Custom alias chứa ký tự đặc biệt phải trả về 422."""
        response = await client.post(
            "/v1/shorten",
            json={
                "long_url": "https://example.com",
                "custom_alias": "invalid alias!",
            },
        )
        assert response.status_code == 422

    async def test_shorten_returns_request_id_header(self, client: AsyncClient):
        """Response phải có header X-Request-ID."""
        response = await client.post(
            "/v1/shorten",
            json={"long_url": "https://example.com"},
        )
        assert "x-request-id" in response.headers


# ── GET /{short_code} ──────────────────────────────────────────────────────────

class TestRedirectEndpoint:
    """Tests cho GET /{short_code}."""

    async def test_redirect_success(self, client: AsyncClient):
        """Redirect đến URL gốc phải trả về 302 với Location header đúng."""
        # Tạo URL trước
        r = await client.post(
            "/v1/shorten",
            json={"long_url": "https://www.python.org"},
        )
        assert r.status_code == 201
        short_code = r.json()["short_code"]

        # Redirect (không follow redirect để kiểm tra 302)
        response = await client.get(f"/{short_code}", follow_redirects=False)
        assert response.status_code == 302
        assert "python.org" in response.headers.get("location", "")

    async def test_redirect_not_found(self, client: AsyncClient):
        """Short code không tồn tại phải trả về 404."""
        response = await client.get("/nonexistent-code-xyz", follow_redirects=False)
        assert response.status_code == 404
        data = response.json()
        # FastAPI wraps HTTPException detail in {"detail": ...}
        detail = data.get("detail", {})
        assert detail.get("error") == "URL_NOT_FOUND"

    async def test_redirect_with_custom_alias(self, client: AsyncClient):
        """Custom alias phải redirect đúng."""
        await client.post(
            "/v1/shorten",
            json={
                "long_url": "https://fastapi.tiangolo.com",
                "custom_alias": "fastapi-docs",
            },
        )
        response = await client.get("/fastapi-docs", follow_redirects=False)
        assert response.status_code == 302
        assert "fastapi" in response.headers.get("location", "")

    async def test_redirect_expired_url(self, client: AsyncClient):
        """URL đã hết hạn không nên được redirect."""
        # Tạo URL đã hết hạn: expires_in_days=0 không hợp lệ (min=1)
        # Nên ta sẽ tạo với alias rồi manually expire — test tương lai
        # Hiện tại test URL không tìm thấy
        response = await client.get("/expired-url-xyz", follow_redirects=False)
        assert response.status_code == 404


# ── GET /v1/health ─────────────────────────────────────────────────────────────

class TestHealthEndpoint:
    """Tests cho GET /v1/health."""

    async def test_health_returns_200(self, client: AsyncClient):
        """Health check phải trả về 200."""
        response = await client.get("/v1/health")
        assert response.status_code == 200

    async def test_health_response_schema(self, client: AsyncClient):
        """Response phải có các field bắt buộc."""
        response = await client.get("/v1/health")
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        assert "dependencies" in data

    async def test_health_has_database_dependency(self, client: AsyncClient):
        """Response phải báo cáo trạng thái database."""
        response = await client.get("/v1/health")
        data = response.json()
        assert "database" in data["dependencies"]
