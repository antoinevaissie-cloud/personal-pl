# backend/db/duck.py
import duckdb
from pathlib import Path
from typing import List, Optional, Tuple
import glob
import datetime as dt

_CONN: Optional[duckdb.DuckDBPyConnection] = None

DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "finance.duckdb"
MIGRATIONS_DIR = Path(__file__).parent / "migrations"

def _run_migrations(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS migrations_applied (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT now()
        );
    """)
    applied = {row[0] for row in conn.execute("SELECT version FROM migrations_applied;").fetchall()}

    for path in sorted(glob.glob(str(MIGRATIONS_DIR / "*.sql"))):
        version = Path(path).name
        if version in applied:
            continue
        sql = Path(path).read_text(encoding="utf-8", errors="ignore")
        if sql.strip():
            conn.execute("BEGIN;")
            try:
                conn.execute(sql)
                conn.execute(
                    "INSERT INTO migrations_applied(version, applied_at) VALUES (?, ?);",
                    [version, dt.datetime.now()]
                )
                conn.execute("COMMIT;")
            except Exception:
                conn.execute("ROLLBACK;")
                raise

def get_conn() -> duckdb.DuckDBPyConnection:
    global _CONN
    if _CONN is None:
        DATA_DIR.mkdir(exist_ok=True, parents=True)
        _CONN = duckdb.connect(str(DB_PATH))
        _run_migrations(_CONN)
    return _CONN

def execute_query(sql: str, params: Optional[List] = None) -> List[Tuple]:
    conn = get_conn()
    if params:
        return conn.execute(sql, params).fetchall()
    return conn.execute(sql).fetchall()

def execute_update(sql: str, params: Optional[List] = None) -> None:
    conn = get_conn()
    if params:
        conn.execute(sql, params)
    else:
        conn.execute(sql)
    conn.commit()
