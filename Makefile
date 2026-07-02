.PHONY: run stop build test lint format migrate shell logs help

# ── Docker ────────────────────────────────────────────────────────────────────
run:           ## Khởi động toàn bộ stack (build lại nếu cần)
	docker-compose up --build

run-d:         ## Khởi động ở background
	docker-compose up --build -d

stop:          ## Dừng toàn bộ stack
	docker-compose down

stop-v:        ## Dừng và xóa volumes (reset DB)
	docker-compose down -v

build:         ## Build Docker image
	docker-compose build

logs:          ## Xem log của service api
	docker-compose logs -f api

shell:         ## Mở bash trong container api
	docker-compose exec api bash

# ── Database ──────────────────────────────────────────────────────────────────
migrate:       ## Chạy Alembic migrations (upgrade head)
	alembic upgrade head

migrate-down:  ## Rollback 1 migration
	alembic downgrade -1

migrate-gen:   ## Tạo migration mới (dùng: make migrate-gen MSG="add_column")
	alembic revision --autogenerate -m "$(MSG)"

migrate-history: ## Xem lịch sử migrations
	alembic history --verbose

# ── Testing ───────────────────────────────────────────────────────────────────
test:          ## Chạy toàn bộ test suite với coverage
	pytest tests/ -v --cov=app --cov-report=term-missing

test-fast:     ## Chạy tests không cần coverage (nhanh hơn)
	pytest tests/ -v

test-file:     ## Chạy 1 file test (dùng: make test-file FILE=tests/test_api.py)
	pytest $(FILE) -v

# ── Code Quality ──────────────────────────────────────────────────────────────
lint:          ## Chạy ruff linter + mypy type checker
	ruff check .
	mypy app/

format:        ## Auto-format code với ruff
	ruff format .
	ruff check --fix .

check:         ## Kiểm tra format mà không sửa (dùng trong CI)
	ruff format --check .
	ruff check .

# ── Development ───────────────────────────────────────────────────────────────
dev:           ## Chạy FastAPI dev server local (không dùng Docker)
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

install:       ## Cài dev dependencies vào .venv
	pip install -r requirements-dev.txt

# ── Help ──────────────────────────────────────────────────────────────────────
help:          ## Hiển thị danh sách lệnh này
	@grep -E '^[a-zA-Z_-]+:.*?##.*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
