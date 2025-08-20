# backend/etl/common.py
import hashlib, re, uuid
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from db.duck import get_conn, execute_update

def sha256_bytes(content: bytes) -> str:
    h = hashlib.sha256()
    h.update(content)
    return h.hexdigest()

def detect_period(dt_like: str | date | datetime) -> date:
    if isinstance(dt_like, date):
        return date(dt_like.year, dt_like.month, 1)
    s = str(dt_like).strip()
    # Accept 'YYYY-MM', 'YYYY/MM', 'YYYY-MM-DD'
    for fmt in ("%Y-%m", "%Y/%m", "%Y-%m-%d"):
        try:
            d = datetime.strptime(s, fmt).date()
            return date(d.year, d.month, 1)
        except Exception:
            continue
    raise ValueError(f"Unrecognized period format: {dt_like}")

def parse_amount(text: str, decimal_comma: bool = True) -> float:
    if text is None:
        return 0.0
    s = str(text).strip()
    if s == "":
        return 0.0
    s = s.replace(" ", "")
    if decimal_comma:
        # 1.234,56 -> 1234.56
        if "," in s and "." in s:
            s = s.replace(".", "").replace(",", ".")
        elif "," in s and "." not in s:
            s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        # fallback: remove non-numeric (keep - .)
        s2 = re.sub(r"[^0-9\.\-]", "", s)
        return float(s2) if s2 else 0.0

def ensure_windows_1252(content: bytes) -> str:
    try:
        return content.decode("cp1252")
    except Exception:
        return content.decode("utf-8", errors="ignore")

def extract_merchant(description: str) -> str:
    if not description:
        return ""
    cleaned = description.upper()
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"CARD\s*\d+/\d+/\d+", "", cleaned)
    cleaned = re.sub(r"REF[:\s]*\d+", "", cleaned)
    return cleaned.strip()[:50]

def upsert_import(bank: str, period_month: date, file_sha256: str, source_file: str, user_id: str, notes: str = "") -> str:
    conn = get_conn()
    row = conn.execute(
        "SELECT id FROM imports WHERE bank=? AND period_month=? AND file_sha256=? AND user_id=?",
        [bank, period_month, file_sha256, user_id]
    ).fetchone()
    if row:
        return str(row[0])
    import_id = str(uuid.uuid4())
    execute_update(
        "INSERT INTO imports(id, bank, period_month, file_sha256, source_file, user_id, notes) VALUES (?,?,?,?,?,?,?)",
        [import_id, bank, period_month, file_sha256, source_file, user_id, notes]
    )
    return import_id

def check_duplicate_import(bank: str, period_month: date, file_sha256: str, user_id: str) -> bool:
    conn = get_conn()
    n = conn.execute(
        "SELECT COUNT(*) FROM imports WHERE bank=? AND period_month=? AND file_sha256=? AND user_id=?",
        [bank, period_month, file_sha256, user_id]
    ).fetchone()[0]
    return bool(n)

def insert_raw_rows(rows: List[Dict[str, Any]], import_batch_id: str, bank: str, user_id: str) -> int:
    """rows must include: ts, description, merchant, amount, currency, account_label; extra optional dict"""
    if not rows:
        return 0
    conn = get_conn()
    to_insert = []
    for r in rows:
        to_insert.append((
            str(uuid.uuid4()),
            import_batch_id,
            bank,
            r.get("ts"),
            r.get("description"),
            r.get("merchant"),
            r.get("amount_raw"),
            r.get("amount"),
            r.get("currency"),
            r.get("account_label"),
            r.get("extra", None),
        ))
    # Insert rows one by one or use executemany
    for row_data in to_insert:
        conn.execute("""
            INSERT INTO transactions_raw
            (id, import_batch_id, bank, ts, description, merchant, amount_raw, amount, currency, account_label, extra)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, row_data)
    conn.commit()
    return len(rows)
