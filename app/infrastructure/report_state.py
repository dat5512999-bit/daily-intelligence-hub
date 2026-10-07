"""Compare public report contents across runs without a database.

The snapshot stores public article fingerprints, never browser preferences.
Missing/corrupt snapshots mean an unknown baseline, not 'all items are new'.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from app.domain.models import DailyReport, IntelligenceCluster


def article_key(cluster: IntelligenceCluster) -> str:
    """Stable identity across layout changes; discard URL fragments only."""
    parsed = urlsplit(cluster.primary_url)
    url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, parsed.query, ""))
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]


def load_snapshot(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def compare_report(report: DailyReport, previous: dict[str, Any]) -> tuple[DailyReport, dict[str, Any]]:
    """Count new URLs and revised title/summary separately from a fetch time."""
    fingerprints = {
        article_key(cluster): hashlib.sha256(f"{cluster.title}\n{cluster.summary}\n{cluster.items[0].repo_description}".encode("utf-8")).hexdigest()
        for cluster in report.clusters
    }
    old = previous.get("fingerprints")
    baseline = previous.get("schema") == 1 and isinstance(old, dict) and bool(old)
    old = old if baseline else {}
    new_count = sum(key not in old for key in fingerprints) if baseline else 0
    changed_count = sum(key in old and old[key] != value for key, value in fingerprints.items()) if baseline else 0
    last_change = None
    try:
        last_change = datetime.fromisoformat(previous["last_content_change_at"])
        if last_change.tzinfo is None:
            last_change = None
    except (KeyError, TypeError, ValueError):
        pass
    if new_count or changed_count:
        last_change = report.generated_at
    # Preserve the baseline through a complete source outage.
    history = dict(old)
    for key, value in fingerprints.items():
        history.pop(key, None)
        history[key] = value
    snapshot = {
        "schema": 1,
        "checked_at": report.generated_at.isoformat(),
        "last_content_change_at": last_change.isoformat() if last_change else None,
        "fingerprints": dict(list(history.items())[-500:]),
    }
    return replace(report, last_content_change_at=last_change, new_item_count=new_count,
                   changed_item_count=changed_count, comparison_available=baseline), snapshot


def save_snapshot(path: Path, snapshot: dict[str, Any]) -> None:
    """Write atomically so an interrupted local run cannot corrupt the baseline."""
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(snapshot, ensure_ascii=False), encoding="utf-8")
    temporary.replace(path)
