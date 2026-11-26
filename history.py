"""대회별 순위 컷 변화(시간대별 기록)를 docs/history.json 에 쌓는다.

형식: {"v": 1, "events": {"<대회 id>": [[시각(초, UTC epoch), 참가자 수, [순위...], [상위 %...]], ...]}}
- 순위·% 배열의 길이는 같고, 값이 이전 기록과 달라졌을 때만 새로 추가한다(변화 없는 시간은 그래프에서 직선으로 이어짐).
- 상위 % 배열이 이전 기록과 같으면 생략(null)해서 용량을 줄인다.
"""
import json
from datetime import datetime
from pathlib import Path

HISTORY_PATH = Path(__file__).resolve().parent / "docs" / "history.json"


def load_history(path=HISTORY_PATH):
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("events"), dict):
                return data
        except json.JSONDecodeError:
            pass
    return {"v": 1, "events": {}}


def to_epoch(iso):
    if not iso:
        return None
    try:
        return int(datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp())
    except ValueError:
        return None


def last_pcts(points):
    """기록을 거꾸로 보면서 가장 최근에 적힌 상위 % 배열을 찾는다."""
    for p in reversed(points):
        if len(p) > 3 and p[3]:
            return p[3]
    return None


def add_snapshot(history, event, fallback_ts=None):
    """대회 한 개의 현재 값을 기록에 더한다. 새로 추가했으면 True."""
    tiers = event.get("tiers") or []
    if not tiers:
        return False
    ts = to_epoch(event.get("updated_at")) or fallback_ts
    if ts is None:
        return False
    ranks = [t["rank"] for t in tiers]
    pcts = [t["pct"] for t in tiers]
    total = event.get("total") or 0
    pts = history["events"].setdefault(str(event["id"]), [])
    prev_pcts = last_pcts(pts)
    if pts:
        last = pts[-1]
        if last[2] == ranks and (prev_pcts == pcts) and (last[1] or 0) == total:
            return False
        if ts <= last[0]:                      # 시각이 거꾸로 가는 값은 무시(같은 시각이면 마지막 값을 덮어씀)
            if ts == last[0]:
                last[1], last[2] = total, ranks
                if prev_pcts != pcts:
                    last[3:] = [pcts]
                return True
            return False
    point = [ts, total, ranks]
    if prev_pcts != pcts:
        point.append(pcts)
    pts.append(point)
    return True


def save_history(history, path=HISTORY_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(history, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
