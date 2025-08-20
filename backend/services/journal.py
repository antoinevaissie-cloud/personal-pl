import uuid
from typing import Dict, Any, Optional, List
from datetime import date, datetime
from db.duck import get_conn, execute_update

def create_journal_entry(period_start: date, period_end: date, 
                        observations_md: str = "", decisions_md: str = "") -> str:
    """Create a new journal entry with auto-generated metrics snapshot."""
    
    # Generate metrics snapshot
    metrics_snapshot = generate_metrics_snapshot(period_start, period_end)
    
    # Append metrics to observations
    full_observations = f"{observations_md}\n\n{metrics_snapshot}".strip()
    
    entry_id = str(uuid.uuid4())
    
    execute_update("""
        INSERT INTO journal_entries (id, period_start, period_end, observations_md, decisions_md)
        VALUES (?, ?, ?, ?, ?)
    """, {
        'id': entry_id,
        'period_start': period_start,
        'period_end': period_end,
        'observations_md': full_observations,
        'decisions_md': decisions_md
    })
    
    return entry_id

def update_journal_entry(entry_id: str, observations_md: Optional[str] = None, 
                        decisions_md: Optional[str] = None) -> Dict[str, Any]:
    """Update an existing journal entry."""
    conn = get_conn()
    
    # Get current entry
    current = conn.execute("""
        SELECT observations_md, decisions_md, period_start, period_end
        FROM journal_entries WHERE id = ?
    """, [entry_id]).fetchone()
    
    if not current:
        raise ValueError(f"Journal entry {entry_id} not found")
    
    # Use existing values if not provided
    new_observations = observations_md if observations_md is not None else current[0]
    new_decisions = decisions_md if decisions_md is not None else current[1]
    
    # Regenerate metrics snapshot if observations changed
    if observations_md is not None:
        metrics_snapshot = generate_metrics_snapshot(current[2], current[3])
        
        # Strip old metrics and add new
        lines = new_observations.split('\n')
        # Remove lines starting with ## Metrics Snapshot
        filtered_lines = []
        skip_metrics = False
        for line in lines:
            if line.strip() == "## Metrics Snapshot":
                skip_metrics = True
                break
            filtered_lines.append(line)
        
        user_content = '\n'.join(filtered_lines).strip()
        new_observations = f"{user_content}\n\n{metrics_snapshot}".strip()
    
    execute_update("""
        UPDATE journal_entries 
        SET observations_md = ?, decisions_md = ?, updated_at = now()
        WHERE id = ?
    """, {
        'observations_md': new_observations,
        'decisions_md': new_decisions,
        'id': entry_id
    })
    
    return get_journal_entry(entry_id)

def get_journal_entry(entry_id: str) -> Optional[Dict[str, Any]]:
    """Get a journal entry by ID."""
    conn = get_conn()
    
    result = conn.execute("""
        SELECT id, period_start, period_end, observations_md, decisions_md, 
               created_at, updated_at
        FROM journal_entries 
        WHERE id = ?
    """, [entry_id]).fetchone()
    
    if not result:
        return None
    
    return {
        'id': result[0],
        'period_start': result[1],
        'period_end': result[2],
        'observations_md': result[3],
        'decisions_md': result[4],
        'created_at': result[5],
        'updated_at': result[6]
    }

def get_journal_entries_by_month(month: date) -> List[Dict[str, Any]]:
    """Get journal entries for a specific month."""
    conn = get_conn()
    
    result = conn.execute("""
        SELECT id, period_start, period_end, observations_md, decisions_md, 
               created_at, updated_at
        FROM journal_entries 
        WHERE DATE_TRUNC('month', period_start) = ?
        ORDER BY period_start DESC
    """, [month]).fetchall()
    
    entries = []
    for row in result:
        entries.append({
            'id': row[0],
            'period_start': row[1],
            'period_end': row[2],
            'observations_md': row[3],
            'decisions_md': row[4],
            'created_at': row[5],
            'updated_at': row[6]
        })
    
    return entries

def generate_metrics_snapshot(period_start: date, period_end: date) -> str:
    """Generate auto-metrics snapshot for a period."""
    conn = get_conn()
    
    # Get current period metrics
    current_metrics = conn.execute("""
        SELECT 
            SUM(CASE WHEN amount > 0 AND NOT is_transfer THEN amount ELSE 0 END) as income,
            SUM(CASE WHEN amount < 0 AND NOT is_transfer THEN -amount ELSE 0 END) as expense,
            SUM(CASE WHEN NOT is_transfer THEN amount ELSE 0 END) as net
        FROM transactions
        WHERE ts >= ? AND ts < ?
    """, [period_start, period_end]).fetchone()
    
    income = current_metrics[0] if current_metrics else 0.0
    expense = current_metrics[1] if current_metrics else 0.0
    net = current_metrics[2] if current_metrics else 0.0
    
    # Get previous period for comparison
    prev_start = date(period_start.year, period_start.month - 1, 1) if period_start.month > 1 else date(period_start.year - 1, 12, 1)
    prev_end = period_start  # Previous period ends when current starts
    
    prev_metrics = conn.execute("""
        SELECT 
            SUM(CASE WHEN amount > 0 AND NOT is_transfer THEN amount ELSE 0 END) as income,
            SUM(CASE WHEN amount < 0 AND NOT is_transfer THEN -amount ELSE 0 END) as expense,
            SUM(CASE WHEN NOT is_transfer THEN amount ELSE 0 END) as net
        FROM transactions
        WHERE ts >= ? AND ts < ?
    """, [prev_start, prev_end]).fetchone()
    
    prev_income = prev_metrics[0] if prev_metrics else 0.0
    prev_expense = prev_metrics[1] if prev_metrics else 0.0
    prev_net = prev_metrics[2] if prev_metrics else 0.0
    
    # Calculate deltas
    delta_income = income - prev_income
    delta_expense = expense - prev_expense
    delta_net = net - prev_net
    
    # Get top 3 category movers (biggest absolute change)
    movers = conn.execute("""
        WITH current_categories AS (
            SELECT 
                category,
                SUM(CASE WHEN NOT is_transfer THEN amount ELSE 0 END) as net
            FROM transactions
            WHERE ts >= ? AND ts < ?
              AND category IS NOT NULL
            GROUP BY category
        ),
        prev_categories AS (
            SELECT 
                category,
                SUM(CASE WHEN NOT is_transfer THEN amount ELSE 0 END) as net
            FROM transactions
            WHERE ts >= ? AND ts < ?
              AND category IS NOT NULL
            GROUP BY category
        )
        SELECT 
            COALESCE(c.category, p.category) as category,
            COALESCE(c.net, 0) - COALESCE(p.net, 0) as delta
        FROM current_categories c
        FULL OUTER JOIN prev_categories p ON c.category = p.category
        WHERE ABS(COALESCE(c.net, 0) - COALESCE(p.net, 0)) > 10  -- Only significant changes
        ORDER BY ABS(COALESCE(c.net, 0) - COALESCE(p.net, 0)) DESC
        LIMIT 3
    """, [period_start, period_end, prev_start, prev_end]).fetchall()
    
    # Format metrics snapshot
    snapshot_lines = [
        "## Metrics Snapshot",
        "",
        f"**Period:** {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}",
        "",
        "### Financial Summary",
        f"- **Income:** €{income:,.2f} ({delta_income:+,.2f} vs prior month)",
        f"- **Expenses:** €{expense:,.2f} ({delta_expense:+,.2f} vs prior month)", 
        f"- **Net:** €{net:,.2f} ({delta_net:+,.2f} vs prior month)",
        ""
    ]
    
    if movers:
        snapshot_lines.extend([
            "### Top Category Movements",
            ""
        ])
        for i, (category, delta) in enumerate(movers, 1):
            direction = "↗" if delta > 0 else "↘"
            snapshot_lines.append(f"{i}. **{category}** {direction} €{delta:+,.2f}")
        snapshot_lines.append("")
    
    snapshot_lines.extend([
        "---",
        f"*Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
    ])
    
    return '\n'.join(snapshot_lines)

def export_journal_as_markdown(entry_id: str) -> str:
    """Export journal entry as formatted Markdown."""
    entry = get_journal_entry(entry_id)
    
    if not entry:
        raise ValueError(f"Journal entry {entry_id} not found")
    
    markdown_lines = [
        f"# Journal Entry - {entry['period_start']} to {entry['period_end']}",
        "",
        f"**Created:** {entry['created_at']}",
        f"**Updated:** {entry['updated_at']}",
        "",
        "## Observations & Variances",
        "",
        entry['observations_md'] or "*No observations recorded.*",
        "",
        "## Decisions & Actions",  
        "",
        entry['decisions_md'] or "*No decisions recorded.*",
        "",
        "---",
        "",
        f"*Journal Entry ID: {entry['id']}*"
    ]
    
    return '\n'.join(markdown_lines)