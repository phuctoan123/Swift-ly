"""
Unit tests cho app/services/url_service.py.

Test các hàm thuần túy (không cần DB):
- generate_short_code()
- validate_url()

Và test DB operations với test database.
"""

import pytest

from app.services.url_service import BASE62_CHARS, generate_short_code, validate_url

# ── generate_short_code() ──────────────────────────────────────────────────────


class TestGenerateShortCode:
    """Tests cho hàm generate_short_code()."""

    def test_default_length(self):
        """Short code mặc định phải có độ dài 7 ký tự."""
        code = generate_short_code()
        assert len(code) == 7

    def test_custom_length(self):
        """Short code phải có đúng độ dài được chỉ định."""
        for length in [4, 6, 7, 8, 10]:
            code = generate_short_code(length=length)
            assert len(code) == length, f"Expected length {length}, got {len(code)}"

    def test_charset_is_base62(self):
        """Short code chỉ được chứa ký tự Base62 (a-z, A-Z, 0-9)."""
        for _ in range(100):
            code = generate_short_code()
            for char in code:
                assert (
                    char in BASE62_CHARS
                ), f"Character '{char}' is not in BASE62_CHARS"

    def test_randomness(self):
        """1000 short codes liên tiếp phải có ít nhất 990 giá trị khác nhau."""
        codes = {generate_short_code() for _ in range(1000)}
        # Xác suất collision với 7 ký tự Base62 cực kỳ thấp
        assert len(codes) >= 990, f"Too many collisions: only {len(codes)} unique codes"

    def test_returns_string(self):
        """Phải trả về kiểu string."""
        code = generate_short_code()
        assert isinstance(code, str)

    def test_no_special_characters(self):
        """Không được chứa ký tự đặc biệt như @, #, !, space, v.v."""
        for _ in range(200):
            code = generate_short_code()
            assert code.isalnum(), f"Code '{code}' contains non-alphanumeric chars"


# ── validate_url() ─────────────────────────────────────────────────────────────


class TestValidateUrl:
    """Tests cho hàm validate_url()."""

    @pytest.mark.parametrize(
        "url",
        [
            "https://www.google.com",
            "http://example.com",
            "https://github.com/user/repo",
            "https://sub.domain.co.uk/path?param=value&other=123",
            "http://192.168.1.1/admin",  # validate_url chỉ check scheme, không check SSRF
        ],
    )
    def test_valid_urls(self, url: str):
        """URL hợp lệ phải trả về True."""
        assert validate_url(url) is True, f"Expected True for URL: {url}"

    @pytest.mark.parametrize(
        "url",
        [
            "",
            "   ",
            "not-a-url",
            "ftp://example.com",
            "mailto:user@example.com",
            "javascript:alert(1)",
            "http",
            "https://",
            "//example.com",
        ],
    )
    def test_invalid_urls(self, url: str):
        """URL không hợp lệ phải trả về False."""
        assert validate_url(url) is False, f"Expected False for URL: {url!r}"
