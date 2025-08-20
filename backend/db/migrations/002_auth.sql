-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT now(),
    last_login TIMESTAMP
);

-- Add user_id to existing tables for multi-tenant support
-- Note: DuckDB doesn't support adding columns with constraints, so we add them without foreign keys
ALTER TABLE imports ADD COLUMN IF NOT EXISTS user_id UUID;
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS user_id UUID;
ALTER TABLE txn_overrides ADD COLUMN IF NOT EXISTS user_id UUID;
ALTER TABLE category_rules ADD COLUMN IF NOT EXISTS user_id UUID;
ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS user_id UUID;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_imports_user_id ON imports(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_category_rules_user_id ON category_rules(user_id);