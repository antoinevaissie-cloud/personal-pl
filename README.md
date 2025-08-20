# Personal P&L MVP

Personal finance P&L application that ingests bank CSV files, normalizes transactions, and provides P&L analysis with drill-down capabilities.

## Architecture

- **Backend**: FastAPI + DuckDB + Python
- **Frontend**: Next.js (App Router) + TypeScript
- **Data**: DuckDB persisted locally with materialized rollups for performance

## Features

- Import CSV files from 3 banks: BNP, Boursorama, Revolut
- Automatic categorization via configurable rules
- Transfer detection and exclusion
- P&L dashboard with category drill-down
- Transaction editing with audit trail
- Journal entries with auto-generated metrics
- Reconciliation with end-of-month balances

## Quick Start

```bash
# Setup
make setup
cp .env.sample .env

# Run backend
make backend

# Run frontend (separate terminal)
make frontend

# Run tests
make test
```

## API Examples

```bash
# Upload CSV
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@july_bnp.csv" \
  -F "bank=BNP" \
  -F "period_month=2025-07-01"

# Commit imported data
curl -X POST "http://localhost:8000/api/import/commit" \
  -H "Content-Type: application/json" \
  -d '{"period_month": "2025-07-01"}'

# Get P&L summary
curl -X POST "http://localhost:8000/api/pl/summary" \
  -H "Content-Type: application/json" \
  -d '{"month": "2025-07-01", "accounts": ["BNP"], "exclude_transfers": true}'
```

## Project Structure

```
personal-pl/
├── backend/          # FastAPI application
├── frontend/         # Next.js application  
├── data/            # DuckDB file + imports (runtime)
├── Makefile         # Development commands
└── README.md        # This file
```

## Environment Variables

```bash
# Backend
API_KEY=optional-api-key
DATABASE_URL=data/finance.duckdb

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```