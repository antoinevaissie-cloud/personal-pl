-- Reference tables
CREATE TABLE IF NOT EXISTS imports (
  id UUID PRIMARY KEY,
  bank TEXT NOT NULL,                 -- 'BNP' | 'Boursorama' | 'Revolut'
  period_month DATE NOT NULL,         -- first of month
  file_sha256 TEXT NOT NULL,
  source_file TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT now(),
  notes TEXT
);

-- Raw, strongly typed
CREATE TABLE IF NOT EXISTS transactions_raw (
  id UUID PRIMARY KEY,
  import_batch_id UUID NOT NULL REFERENCES imports(id),
  bank TEXT NOT NULL,
  ts TIMESTAMP,
  description TEXT,
  merchant TEXT,
  amount_raw TEXT,
  amount DOUBLE,
  currency TEXT,
  account_label TEXT,
  extra JSON,
  created_at TIMESTAMP DEFAULT now()
);

-- Derived (rules + overrides + transfers applied)
CREATE TABLE IF NOT EXISTS transactions (
  id UUID PRIMARY KEY,
  raw_id UUID NOT NULL REFERENCES transactions_raw(id),
  ts TIMESTAMP NOT NULL,
  account_id TEXT NOT NULL,           -- same domain as imports.bank
  account_label TEXT,
  description TEXT,
  merchant TEXT,
  category TEXT,
  subcategory TEXT,
  amount DOUBLE NOT NULL,
  currency TEXT NOT NULL,
  balance DOUBLE,
  is_transfer BOOLEAN DEFAULT FALSE,
  source_file TEXT,
  import_batch_id UUID NOT NULL REFERENCES imports(id),
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS txn_overrides (
  id UUID PRIMARY KEY,
  txn_id UUID NOT NULL REFERENCES transactions(id),
  set_category TEXT,
  set_subcategory TEXT,
  set_is_transfer BOOLEAN,
  note TEXT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS category_rules (
  id UUID PRIMARY KEY,
  active BOOLEAN DEFAULT TRUE,
  priority INT DEFAULT 100,
  field TEXT CHECK (field IN ('merchant','description')),
  operator TEXT CHECK (operator IN ('contains','startswith','equals','regex')),
  pattern TEXT NOT NULL,
  set_category TEXT,
  set_subcategory TEXT,
  set_is_transfer BOOLEAN
);

CREATE TABLE IF NOT EXISTS fx_rates (
  month DATE NOT NULL,
  from_ccy TEXT NOT NULL,
  to_ccy TEXT NOT NULL,
  rate DOUBLE NOT NULL,
  PRIMARY KEY(month, from_ccy, to_ccy)
);

CREATE TABLE IF NOT EXISTS statements_eom (
  account_id TEXT NOT NULL,
  period_month DATE NOT NULL,
  balance DOUBLE NOT NULL,
  PRIMARY KEY (account_id, period_month)
);

CREATE TABLE IF NOT EXISTS rollup_monthly (
  account_id TEXT NOT NULL,
  month DATE NOT NULL,
  category TEXT,
  subcategory TEXT,
  income DOUBLE DEFAULT 0,
  expense DOUBLE DEFAULT 0,
  net DOUBLE NOT NULL,
  PRIMARY KEY (account_id, month, category, subcategory)
);

CREATE TABLE IF NOT EXISTS journal_entries (
  id UUID PRIMARY KEY,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  observations_md TEXT,
  decisions_md TEXT,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);