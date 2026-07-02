// ── API Types (mirrors FastAPI Backend schemas) ──────────────────────────────

export interface ShortenRequest {
  long_url: string;
  custom_alias?: string;
  expires_in_days?: number;
}

export interface ShortenResponse {
  short_code: string;
  short_url: string;
  long_url: string;
  expires_at: string | null;
  created_at: string;
}

export interface URLDetail extends ShortenResponse {
  id: string;
  title: string | null;
  is_active: boolean;
  user_id: string | null;
}

export interface URLListResponse {
  items: URLDetail[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
}

export interface AnalyticsResponse {
  short_code: string;
  total_clicks: number;
  devices: Record<string, number>;
  countries: Record<string, number>;
}

export interface ClicksByDay {
  date: string;
  clicks: number;
}

export interface AuthRequest {
  email?: string;
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserProfile {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
}

// ── API Error Types ──────────────────────────────────────────────────────────

export interface APIError {
  error: string;
  message: string;
  field?: string;
  suggestion?: string;
}
