-- Kết nối vào database urlshortener
\c urlshortener

-- Bảng users
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(320) NOT NULL UNIQUE,
    username        VARCHAR(50)  NOT NULL UNIQUE,
    hashed_password TEXT         NOT NULL,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    is_verified     BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Bảng urls
CREATE TABLE urls (
    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    short_code    VARCHAR(20)  NOT NULL UNIQUE,
    long_url      TEXT         NOT NULL,
    user_id       UUID         REFERENCES users(id) ON DELETE SET NULL,
    custom_alias  VARCHAR(50),
    title         VARCHAR(500),
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    expires_at    TIMESTAMPTZ,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_short_code_format CHECK (short_code ~ '^[a-zA-Z0-9_-]+$')
);

CREATE UNIQUE INDEX idx_urls_short_code ON urls(short_code);
CREATE INDEX idx_urls_user_id ON urls(user_id);

CREATE INDEX idx_urls_active_not_expired 
    ON urls(short_code) 
    WHERE is_active = TRUE AND (expires_at IS NULL OR expires_at > NOW());

-- Bảng click_events (TimescaleDB hypertable)
CREATE TABLE click_events (
    id            BIGSERIAL,
    short_code    VARCHAR(20)   NOT NULL,
    clicked_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    ip_address    INET,
    user_agent    TEXT,
    referer       TEXT,
    country_code  CHAR(2),
    city          VARCHAR(100),
    device_type   VARCHAR(20),
    browser       VARCHAR(50),
    os            VARCHAR(50),

    PRIMARY KEY (short_code, clicked_at, id)
);

-- Chuyển thành hypertable
SELECT create_hypertable('click_events', 'clicked_at', if_not_exists => TRUE);

SELECT add_compression_policy('click_events', INTERVAL '7 days');
SELECT add_retention_policy('click_events', INTERVAL '2 years');

CREATE INDEX idx_click_events_short_code 
    ON click_events(short_code, clicked_at DESC);

-- Bảng url_stats (aggregated)
CREATE TABLE url_stats (
    short_code     VARCHAR(20)  NOT NULL,
    stat_date      DATE         NOT NULL,
    total_clicks   BIGINT       NOT NULL DEFAULT 0,
    unique_ips     BIGINT       NOT NULL DEFAULT 0,
    mobile_clicks  BIGINT       NOT NULL DEFAULT 0,
    desktop_clicks BIGINT       NOT NULL DEFAULT 0,
    top_countries  JSONB,
    top_referers   JSONB,
    updated_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    PRIMARY KEY (short_code, stat_date)
);

CREATE INDEX idx_url_stats_short_code 
    ON url_stats(short_code, stat_date DESC);