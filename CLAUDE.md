# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal P&L application for tracking financial transactions across multiple bank accounts. Built with FastAPI backend (Python/DuckDB) and Next.js frontend (TypeScript/React).

## Development Commands

### Setup & Installation
```bash
# Initial setup (installs both backend and frontend dependencies)
make setup
cp .env.example .env

# Manual backend setup
cd backend && python -m venv .venv && .venv/bin/pip install -r requirements.txt

# Manual frontend setup  
cd frontend && npm install
```

### Running the Application
```bash
# Run backend (port 8000)
make backend
# OR manually:
cd backend && .venv/bin/uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Run frontend (port 3000) - separate terminal
make frontend  
# OR manually:
cd frontend && npm run dev

# Access points:
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/api/docs (debug mode only)
```

### Testing
```bash
# Run all tests
make test

# Backend tests only
make test-backend
# OR: cd backend && .venv/bin/pytest -v
# Run single test: cd backend && .venv/bin/pytest tests/test_etl.py::test_bnp_parser -v

# Frontend type checking
make test-frontend
# OR: cd frontend && npm run type-check
```

### Code Quality
```bash
# Linting
make lint  # Both backend and frontend
make lint-backend  # cd backend && .venv/bin/ruff check .
make lint-frontend # cd frontend && npm run lint

# Formatting
make format  # Auto-format all code
# Backend: cd backend && .venv/bin/ruff format .
# Frontend: cd frontend && npm run format

# Frontend specific
cd frontend && npm run lint:fix  # Auto-fix linting issues
```

### Database Operations
```bash
# Run migrations (creates tables if needed)
make migrate

# Database location: data/finance.duckdb
# Migrations: backend/db/migrations/*.sql (auto-applied on startup)
```

## Architecture & Data Flow

### CSV Import Pipeline
1. **Upload** (`/api/upload`) → Validates file, checks SHA256 for duplicates
2. **Parse** → Bank-specific parsers in `backend/etl/`:
   - `bnp.py`: Windows-1252 encoding, semicolon-delimited
   - `boursorama.py`: Custom format
   - `revolut.py`: Standard CSV
3. **Store Raw** → `transactions_raw` table (preserves original format)
4. **Commit** (`/api/import/commit`) → Normalizes to `transactions` table
5. **Enrich** → Applies category rules, detects transfers
6. **Materialize** → Updates `rollup_monthly` for fast P&L queries

### Key Database Tables
- `transactions_raw`: Unprocessed bank data with original fields
- `transactions`: Normalized, categorized transactions (main working table)
- `txn_overrides`: Audit trail for manual edits
- `category_rules`: Pattern-based auto-categorization engine
- `rollup_monthly`: Pre-aggregated P&L summaries by category
- `imports`: Tracks file uploads with SHA256 deduplication
- `users`: Authentication with bcrypt password hashing

### Authentication Flow
- JWT-based authentication with `python-jose`
- Token required for all API endpoints except `/api/auth/*`
- User context automatically applied to all queries
- Tokens expire after 24 hours (configurable)

### Service Layer Pattern
Backend uses a service layer (`backend/services/`) for business logic:
- `rollup.py`: Materialized view management for performance
- `rules_engine.py`: Category rule application
- `transfers.py`: Transfer detection between accounts
- `journal.py`: Period-based financial observations

### API Request Flow
```
Frontend (Next.js) → API Call with JWT → FastAPI Router (backend/api/*.py)
→ Service Layer → DuckDB (via backend/db/duck.py) → Response DTOs (backend/models/dto.py)
```

### Frontend Architecture
- Next.js 14 with App Router (`frontend/app/`)
- Authentication pages: `/login`, `/register`
- Main features: `/upload` (CSV import), `/pl` (P&L dashboard)
- API client uses fetch with JWT in Authorization header
- Tailwind CSS for styling

## Environment Variables

Backend requires `.env` file:
```bash
SECRET_KEY=your-secret-key-here-change-in-production  # JWT signing
DEBUG=false  # Enables API docs at /api/docs
DATABASE_URL=data/finance.duckdb
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
MAX_UPLOAD_SIZE=10485760  # 10MB
LOG_LEVEL=INFO
LOG_FORMAT=json
```

Frontend requires `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Common Development Tasks

### Adding a New Bank Parser
1. Create `backend/etl/newbank.py` following pattern of existing parsers
2. Update `backend/api/upload.py` to route to new parser
3. Add bank enum value to `backend/models/dto.py:BankType`
4. Test with sample CSV: `cd backend && .venv/bin/pytest tests/test_etl.py`

### Modifying Database Schema
1. Create migration file: `backend/db/migrations/00X_description.sql`
2. Migrations auto-apply on startup or via `make migrate`
3. Update relevant DTOs in `backend/models/dto.py`

### Adding API Endpoints
1. Create router in `backend/api/new_feature.py`
2. Include router in `backend/app.py`
3. Add DTOs to `backend/models/dto.py`
4. Add service logic to `backend/services/` if complex

### Testing CSV Processing
```bash
# Test upload endpoint
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@sample.csv" \
  -F "bank=BNP" \
  -F "period_month=2025-01"

# Commit imported data
curl -X POST "http://localhost:8000/api/import/commit" \
  -H "Content-Type: application/json" \
  -d '{"period_month": "2025-01"}'
```

## Important Patterns

### User Context Isolation
All database queries include `user_id` filtering to ensure data isolation between users. This is handled automatically in the service layer.

### Duplicate Prevention
Files are SHA256-hashed to prevent duplicate imports. Check happens at upload time in `backend/etl/common.py:check_duplicate_import()`.

### Error Handling
Custom exceptions in `backend/exceptions.py` provide structured error responses. All exceptions are logged with context via `structlog`.

### Performance Optimization
- `rollup_monthly` table provides pre-aggregated data for P&L queries
- Materialized views rebuilt on data changes via `rebuild_rollup_monthly()`
- DuckDB connection pooling via singleton in `backend/db/duck.py`

### Transaction Categorization
Rules engine applies patterns in priority order:
1. Check `category_rules` table patterns
2. Apply first matching rule
3. Manual overrides stored in `txn_overrides`
4. Uncategorized transactions flagged in P&L response