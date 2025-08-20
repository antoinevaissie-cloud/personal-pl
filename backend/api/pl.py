# backend/api/pl.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date
from services.rollup import rebuild_rollup_monthly, get_rollup_summary
from db.duck import execute_query
from etl.common import detect_period

router = APIRouter()

class PLSummaryIn(BaseModel):
    month: str = Field(..., description="YYYY-MM")
    accounts: Optional[List[str]] = None  # ['BNP','Boursorama','Revolut']
    exclude_transfers: bool = True  # already excluded in rollup for MVP
    currency_view: str = "native"   # placeholder

@router.post("/api/pl/summary")
def pl_summary(req: PLSummaryIn) -> Dict[str, Any]:
    month = detect_period(req.month)

    # Ensure rollup exists (idempotent; cheap)
    rebuild_rollup_monthly(month, req.accounts)

    acc_sql = ""
    params = [month]
    if req.accounts:
        acc_sql = "AND account_id IN (" + ",".join("?"*len(req.accounts)) + ")"
        params += req.accounts

    rows = execute_query(f"""
        SELECT account_id, category, subcategory, SUM(income), SUM(expense), SUM(net)
        FROM rollup_monthly
        WHERE month = ?
          {acc_sql if req.accounts else ""}
        GROUP BY 1,2,3
        ORDER BY category, subcategory;
    """, params)

    by_category: Dict[str, Dict[str, Any]] = {}
    for acct, cat, sub, inc, exp, net in rows:
        cat = cat or "Uncategorized"
        sub = sub or ""
        if cat not in by_category:
            by_category[cat] = {"total": 0.0, "subcategory": {}}
        by_category[cat]["total"] += float(net or 0.0)
        if sub not in by_category[cat]["subcategory"]:
            by_category[cat]["subcategory"][sub] = 0.0
        by_category[cat]["subcategory"][sub] += float(net or 0.0)

    summary = get_rollup_summary(month, req.accounts)
    # Convert subcategory maps to arrays for frontend
    cat_rows = []
    for cat, data in by_category.items():
        subs = [{"name": s, "net": round(v, 2)} for s, v in sorted(data["subcategory"].items())]
        cat_rows.append({"category": cat, "net": round(data["total"], 2), "subs": subs})
    cat_rows.sort(key=lambda r: r["category"])

    return {
        "summary": summary,
        "rows": cat_rows,
        "filters": {"month": month.isoformat(), "accounts": req.accounts or []}
    }
