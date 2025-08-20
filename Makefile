.PHONY: setup backend frontend dev dev-backend dev-frontend test test-backend test-frontend lint lint-backend lint-frontend format clean migrate

# configurable
PY ?= python3
VENV ?= .venv
PYBIN := $(VENV)/bin/python
PIP   := $(VENV)/bin/pip
UVICORN := $(VENV)/bin/uvicorn
PYTEST := $(VENV)/bin/pytest
RUFF := $(VENV)/bin/ruff

# Setup development environment
setup:
	@echo "Setting up backend..."
	cd backend && \
		$(PY) -m venv $(VENV) && \
		$(PYBIN) -m pip install -U pip && \
		$(PIP) install -r requirements.txt
	@echo "Setting up frontend..."
	cd frontend && npm install
	@echo "Setup complete! Copy .env.example to .env and configure."

# Run backend development server
backend:
	cd backend && \
		$(UVICORN) app:app --reload --host 0.0.0.0 --port 8000

# Run frontend development server
frontend:
	cd frontend && npm run dev

# Run both backend and frontend (requires two terminals)
dev:
	@echo "Run 'make backend' in one terminal and 'make frontend' in another"

# Testing
test: test-backend test-frontend

test-backend:
	cd backend && $(PYTEST) -v

test-frontend:
	cd frontend && npm run type-check

# Linting
lint: lint-backend lint-frontend

lint-backend:
	cd backend && $(RUFF) check .

lint-frontend:
	cd frontend && npm run lint

# Format code
format:
	cd backend && $(RUFF) format .
	cd frontend && npm run format

# Clean build artifacts
clean:
	rm -rf backend/$(VENV)
	rm -rf backend/__pycache__
	rm -rf backend/**/__pycache__
	rm -rf backend/.pytest_cache
	rm -rf frontend/node_modules
	rm -rf frontend/.next
	rm -rf frontend/out

# Database migrations
migrate:
	cd backend && $(PYBIN) -c "from db.duck import get_conn; get_conn()"

# Development shortcuts (legacy support)
dev-backend: backend
dev-frontend: frontend
clean-venv:
	rm -rf backend/$(VENV)