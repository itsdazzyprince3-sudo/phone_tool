"""
vault.py — SQLite Evidence Vault with Safe Migrations, Backup, Restore & Search
VirgoYT OSINT Toolkit v4.0
Developer Credit: VIRGOYT707
"""

import sqlite3
import shutil
import csv
import secrets
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from .config import DB_FILE, BACKUP_DIR, EXPORT_DIR, C

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CASE ID GENERATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_case_id() -> str:
    """Generate a clean, standardized VirgoYT Case Identifier."""
    date_stamp = datetime.now().strftime("%Y%m%d")
    rand_hex = secrets.token_hex(2).upper()
    return f"VY-{date_stamp}-{rand_hex}"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DATABASE INITIALIZATION & SCHEMA MIGRATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def init_db(db_path: Optional[Path] = None) -> bool:
    """
    Initialize evidence vault with automatic pre-migration backup
    and non-destructive schema migrations.
    """
    target = db_path or DB_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Non-destructive safety backup if database already exists
    if target.exists() and target.stat().st_size > 0:
        try:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            auto_bak = BACKUP_DIR / f"pre_v4_auto_backup_{ts}.db"
            shutil.copy2(str(target), str(auto_bak))
        except Exception:
            pass  # Non-fatal if backup directory permissions differ

    conn = sqlite3.connect(str(target))
    cur = conn.cursor()

    # 2. Base table creation (creates full v4.0 schema if table does not exist)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS evidence (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id      TEXT UNIQUE,
            case_hash    TEXT,
            phone        TEXT NOT NULL,
            country      TEXT,
            region       TEXT,
            carrier      TEXT,
            line_type    TEXT,
            timezones    TEXT,
            is_valid     INTEGER,
            burner_flag  INTEGER DEFAULT 0,
            risk_score   INTEGER DEFAULT 0,
            risk_level   TEXT DEFAULT 'UNKNOWN',
            risk_factors TEXT DEFAULT '',
            confidence   TEXT DEFAULT 'MEDIUM',
            category     TEXT DEFAULT 'General',
            tags         TEXT DEFAULT '',
            platform     TEXT,
            notes        TEXT,
            intl_fmt     TEXT,
            e164_fmt     TEXT,
            national_fmt TEXT,
            date_added   TEXT NOT NULL,
            updated_at   TEXT NOT NULL
        )
    """)

    # 3. Non-destructive migration for existing v3.0 tables
    cur.execute("PRAGMA table_info(evidence)")
    existing_cols = {row[1] for row in cur.fetchall()}

    columns_to_add = [
        ("case_id", "TEXT"),
        ("risk_level", "TEXT DEFAULT 'UNKNOWN'"),
        ("risk_factors", "TEXT DEFAULT ''"),
        ("confidence", "TEXT DEFAULT 'MEDIUM'"),
        ("category", "TEXT DEFAULT 'General'"),
        ("tags", "TEXT DEFAULT ''"),
        ("updated_at", "TEXT"),
    ]

    for col_name, col_def in columns_to_add:
        if col_name not in existing_cols:
            try:
                cur.execute(f"ALTER TABLE evidence ADD COLUMN {col_name} {col_def}")
            except Exception:
                pass

    # 4. Backfill any missing metadata for existing rows
    cur.execute("SELECT id, case_hash, date_added, case_id, updated_at FROM evidence")
    rows = cur.fetchall()
    for row in rows:
        row_id, chash, d_added, cid, u_at = row
        updates = []
        params = []

        if not cid:
            new_cid = f"VY-LEGACY-{(chash or str(row_id))[:8].upper()}"
            updates.append("case_id = ?")
            params.append(new_cid)

        if not u_at:
            updates.append("updated_at = ?")
            params.append(d_added or datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        if updates:
            params.append(row_id)
            cur.execute(f"UPDATE evidence SET {', '.join(updates)} WHERE id = ?", params)

    conn.commit()
    conn.close()
    return True

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CRUD OPERATIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def save_case(
    analysis: Dict[str, Any],
    risk: Dict[str, Any],
    platform: str = "",
    notes: str = "",
    category: str = "General",
    tags: str = "",
    db_path: Optional[Path] = None,
) -> Tuple[int, str]:
    """Save an analyzed phone case into the evidence vault."""
    target = db_path or DB_FILE
    init_db(target)
    conn = sqlite3.connect(str(target))
    cur = conn.cursor()

    case_id = generate_case_id()
    legacy_hash = (analysis.get("e164", "") + str(datetime.now().timestamp()))[:12]
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    tz_str = ", ".join(analysis.get("timezones", []))
    factors_summary = "; ".join(
        f"[{f['code']} {f['delta']:+d}]" for f in risk.get("factors", [])
    )

    cur.execute("""
        INSERT INTO evidence (
            case_id, case_hash, phone, country, region, carrier,
            line_type, timezones, is_valid, burner_flag,
            risk_score, risk_level, risk_factors, confidence,
            category, tags, platform, notes,
            intl_fmt, e164_fmt, national_fmt,
            date_added, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        case_id,
        legacy_hash,
        analysis.get("international", analysis.get("phone_input", "")),
        analysis.get("country_name", "UNKNOWN"),
        analysis.get("region_code", "??"),
        analysis.get("carrier", "UNKNOWN"),
        analysis.get("line_type", "Unknown Line Type"),
        tz_str,
        1 if analysis.get("is_valid") else 0,
        1 if analysis.get("is_voip") else 0,
        risk.get("score") if risk.get("score") is not None else -1,
        risk.get("risk_level", "UNKNOWN"),
        factors_summary,
        risk.get("confidence", "MEDIUM"),
        category.strip() or "General",
        tags.strip(),
        platform.strip(),
        notes.strip(),
        analysis.get("international", ""),
        analysis.get("e164", ""),
        analysis.get("national", ""),
        now_str,
        now_str,
    ))

    row_id = cur.lastrowid or 0
    conn.commit()
    conn.close()
    return row_id, case_id

def update_case_notes(
    record_id: Any,
    new_notes: str,
    new_tags: Optional[str] = None,
    new_category: Optional[str] = None,
    db_path: Optional[Path] = None,
) -> bool:
    """Update user notes, tags, or category on an existing evidence entry."""
    target = db_path or DB_FILE
    conn = sqlite3.connect(str(target))
    cur = conn.cursor()

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clauses = ["notes = ?", "updated_at = ?"]
    params: List[Any] = [new_notes.strip(), now_str]

    if new_tags is not None:
        clauses.append("tags = ?")
        params.append(new_tags.strip())

    if new_category is not None:
        clauses.append("category = ?")
        params.append(new_category.strip())

    # Record ID can be primary key int or string case_id
    if str(record_id).isdigit():
        params.append(int(record_id))
        cur.execute(f"UPDATE evidence SET {', '.join(clauses)} WHERE id = ?", params)
    else:
        params.append(str(record_id).strip())
        cur.execute(f"UPDATE evidence SET {', '.join(clauses)} WHERE case_id = ? OR case_hash = ?", params + [str(record_id).strip()])

    modified = cur.rowcount > 0
    conn.commit()
    conn.close()
    return modified

def get_case(record_id: Any, db_path: Optional[Path] = None) -> Optional[sqlite3.Row]:
    """Retrieve full detail for a single case record by ID or Case ID."""
    target = db_path or DB_FILE
    conn = sqlite3.connect(str(target))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if str(record_id).isdigit():
        cur.execute("SELECT * FROM evidence WHERE id = ?", (int(record_id),))
    else:
        q = str(record_id).strip()
        cur.execute("SELECT * FROM evidence WHERE case_id = ? OR case_hash = ?", (q, q))

    row = cur.fetchone()
    conn.close()
    return row

def list_all_cases(db_path: Optional[Path] = None) -> List[sqlite3.Row]:
    """List all evidence records ordered by last updated timestamp."""
    target = db_path or DB_FILE
    init_db(target)
    conn = sqlite3.connect(str(target))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM evidence ORDER BY updated_at DESC, id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def search_cases(query: str, db_path: Optional[Path] = None) -> List[sqlite3.Row]:
    """Search across phone, case ID, tags, category, platform, and analyst notes."""
    target = db_path or DB_FILE
    init_db(target)
    conn = sqlite3.connect(str(target))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    term = f"%{query.strip()}%"
    cur.execute("""
        SELECT * FROM evidence
        WHERE case_id LIKE ? OR case_hash LIKE ?
           OR phone LIKE ? OR e164_fmt LIKE ? OR national_fmt LIKE ?
           OR country LIKE ? OR carrier LIKE ? OR platform LIKE ?
           OR notes LIKE ? OR tags LIKE ? OR category LIKE ?
        ORDER BY updated_at DESC
    """, (term, term, term, term, term, term, term, term, term, term, term))

    rows = cur.fetchall()
    conn.close()
    return rows

def delete_case(record_id: Any, db_path: Optional[Path] = None) -> bool:
    """Delete a single evidence record after confirmation."""
    target = db_path or DB_FILE
    conn = sqlite3.connect(str(target))
    cur = conn.cursor()

    if str(record_id).isdigit():
        cur.execute("DELETE FROM evidence WHERE id = ?", (int(record_id),))
    else:
        q = str(record_id).strip()
        cur.execute("DELETE FROM evidence WHERE case_id = ? OR case_hash = ?", (q, q))

    deleted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  INTEGRITY, BACKUP & RESTORE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def check_integrity(db_path: Optional[Path] = None) -> Tuple[bool, str]:
    """Execute PRAGMA integrity_check on the evidence database."""
    target = db_path or DB_FILE
    if not target.exists():
        return False, "Database file does not exist."
    try:
        conn = sqlite3.connect(str(target))
        cur = conn.cursor()
        cur.execute("PRAGMA integrity_check")
        status = cur.fetchone()[0]
        conn.close()
        return (status == "ok"), status
    except Exception as e:
        return False, str(e)

def backup_database(dest_path: Optional[Path] = None, src_path: Optional[Path] = None) -> Path:
    """
    Perform a live, crash-consistent SQLite backup using the official SQLite Backup API.
    """
    src = src_path or DB_FILE
    init_db(src)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    if dest_path:
        dest = dest_path
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = BACKUP_DIR / f"virgoyt_vault_backup_{ts}.db"

    src_conn = sqlite3.connect(str(src))
    dest_conn = sqlite3.connect(str(dest))
    with dest_conn:
        src_conn.backup(dest_conn)
    dest_conn.close()
    src_conn.close()
    return dest

def restore_database(backup_path: Path, target_path: Optional[Path] = None) -> Tuple[bool, str]:
    """
    Safely restore database from a backup file after verifying backup integrity.
    """
    if not backup_path.exists():
        return False, f"Backup file not found: {backup_path}"

    # Verify backup integrity first
    is_ok, msg = check_integrity(backup_path)
    if not is_ok:
        return False, f"Backup file failed integrity check: {msg}"

    target = target_path or DB_FILE

    # Pre-restore safety backup of active database
    if target.exists():
        try:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safety_copy = BACKUP_DIR / f"pre_restore_safety_{ts}.db"
            shutil.copy2(str(target), str(safety_copy))
        except Exception:
            pass

    # Copy backup over target
    try:
        shutil.copy2(str(backup_path), str(target))
        return True, "Database restored successfully."
    except Exception as e:
        return False, f"Restore failed during file copy: {e}"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CSV EXPORT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def export_to_csv(
    destination: Optional[Path] = None,
    case_ids: Optional[List[Any]] = None,
    db_path: Optional[Path] = None,
) -> Tuple[int, Path]:
    """
    Export evidence records to a standardized CSV file.
    Supports exporting all records or a selected filter.
    """
    target = db_path or DB_FILE
    rows = list_all_cases(target)
    if case_ids:
        filter_set = {str(c) for c in case_ids}
        rows = [r for r in rows if str(r["id"]) in filter_set or str(r["case_id"]) in filter_set]

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    if destination:
        out_path = destination
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = EXPORT_DIR / f"virgoyt_evidence_export_{ts}.csv"

    fieldnames = [
        "ID", "Case_ID", "Legacy_Hash", "Phone", "E164", "National",
        "Country", "Region", "Carrier", "Line_Type", "Timezones",
        "Is_Valid", "Is_Burner", "Risk_Score", "Risk_Level", "Confidence",
        "Category", "Tags", "Platform", "Notes", "Date_Added", "Updated_At"
    ]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)
        for r in rows:
            writer.writerow([
                r["id"],
                r["case_id"] or "",
                r["case_hash"] or "",
                r["phone"] or "",
                r["e164_fmt"] or "",
                r["national_fmt"] or "",
                r["country"] or "",
                r["region"] or "",
                r["carrier"] or "",
                r["line_type"] or "",
                r["timezones"] or "",
                r["is_valid"],
                r["burner_flag"],
                r["risk_score"],
                r["risk_level"] or "UNKNOWN",
                r["confidence"] or "MEDIUM",
                r["category"] or "General",
                r["tags"] or "",
                r["platform"] or "",
                r["notes"] or "",
                r["date_added"],
                r["updated_at"],
            ])

    return len(rows), out_path

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  VAULT STATISTICS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_vault_stats(db_path: Optional[Path] = None) -> Dict[str, Any]:
    """Calculate aggregated vault statistics and distribution metrics."""
    target = db_path or DB_FILE
    init_db(target)
    conn = sqlite3.connect(str(target))
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM evidence")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM evidence WHERE burner_flag = 1")
    burners = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM evidence WHERE risk_score >= 60")
    high_risk = cur.fetchone()[0]

    cur.execute("SELECT AVG(risk_score) FROM evidence WHERE risk_score >= 0")
    avg_score = cur.fetchone()[0] or 0

    cur.execute("SELECT category, COUNT(*) FROM evidence GROUP BY category ORDER BY COUNT(*) DESC")
    categories = cur.fetchall()

    cur.execute("SELECT platform, COUNT(*) FROM evidence GROUP BY platform ORDER BY COUNT(*) DESC LIMIT 5")
    top_platforms = cur.fetchall()

    conn.close()

    return {
        "total": total,
        "burners": burners,
        "high_risk": high_risk,
        "avg_risk": round(avg_score),
        "categories": categories,
        "top_platforms": top_platforms,
    }
