#!/usr/bin/env python3
"""git 기록(매시간 커밋된 docs/data.json)에서 docs/history.json 을 처음 만든다. 한 번만 실행하면 된다.

사용: python tools/backfill_history.py   (저장소가 얕은 클론이면 먼저 git fetch --unshallow 또는 --depth=2000)
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from history import add_snapshot, save_history  # noqa: E402


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True, encoding="utf-8")


def main():
    shas = git("log", "--reverse", "--format=%H %ct", "--", "docs/data.json").split("\n")
    shas = [s.split() for s in shas if s.strip()]
    history = {"v": 1, "events": {}}
    added = 0
    for sha, ct in shas:
        try:
            data = json.loads(git("show", f"{sha}:docs/data.json"))
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            continue
        for ev in data.get("events", []):
            if add_snapshot(history, ev, fallback_ts=int(ct)):
                added += 1
    save_history(history)
    pts = sum(len(v) for v in history["events"].values())
    print(f"커밋 {len(shas)}개 → 대회 {len(history['events'])}개, 기록 {pts}점 저장")


if __name__ == "__main__":
    main()
