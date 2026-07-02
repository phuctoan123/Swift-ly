"""Initial database schema.

Revision ID: 001
Revises:
Create Date: 2026-06-19

Tạo 4 bảng cốt lõi:
- users: tài khoản người dùng
- urls: URL records (bảng chính)
- click_events: raw analytics data
- url_stats: aggregated statistics
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Bảng users ─────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("hashed_password", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.create_unique_constraint("uq_users_username", "users", ["username"])
    op.create_index("idx_users_email", "users", ["email"])
    op.create_index("idx_users_username", "users", ["username"])

    # ── Bảng urls ──────────────────────────────────────────────────────────────
    op.create_table(
        "urls",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("short_code", sa.String(20), nullable=False),
        sa.Column("long_url", sa.Text(), nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("custom_alias", sa.String(50), nullable=True),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            r"short_code ~ '^[a-zA-Z0-9_-]+$'",
            name="chk_short_code_format",
        ),
    )
    # Index chính cho redirect lookup — UNIQUE + fast
    op.create_unique_constraint("uq_urls_short_code", "urls", ["short_code"])
    op.create_index("idx_urls_short_code", "urls", ["short_code"], unique=True)
    op.create_index("idx_urls_user_id", "urls", ["user_id"])
    # Partial index — chỉ scan active URLs (hot path)
    # Lưu ý: Không thể dùng NOW() trong index predicate vì nó không phải là IMMUTABLE function
    op.execute(
        """
        CREATE INDEX idx_urls_active
            ON urls(short_code)
            WHERE is_active = TRUE
        """
    )

    # ── Bảng click_events ──────────────────────────────────────────────────────
    op.create_table(
        "click_events",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("short_code", sa.String(20), nullable=False),
        sa.Column(
            "clicked_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("referer", sa.Text(), nullable=True),
        sa.Column("country_code", sa.String(2), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("device_type", sa.String(20), nullable=True),
        sa.Column("browser", sa.String(50), nullable=True),
        sa.Column("os", sa.String(50), nullable=True),
    )
    op.create_index(
        "idx_click_events_short_code",
        "click_events",
        ["short_code", sa.text("clicked_at DESC")],
    )

    # ── Bảng url_stats ─────────────────────────────────────────────────────────
    op.create_table(
        "url_stats",
        sa.Column("short_code", sa.String(20), primary_key=True),
        sa.Column("stat_date", sa.Date(), primary_key=True),
        sa.Column("total_clicks", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("unique_ips", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("mobile_clicks", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("desktop_clicks", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("top_countries", sa.JSON(), nullable=True),
        sa.Column("top_referers", sa.JSON(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index(
        "idx_url_stats_short_code",
        "url_stats",
        ["short_code", sa.text("stat_date DESC")],
    )


def downgrade() -> None:
    op.drop_table("url_stats")
    op.drop_table("click_events")
    op.drop_table("urls")
    op.drop_table("users")
