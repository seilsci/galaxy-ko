#!/usr/bin/env python3
"""狂野飙车传奇 순위 데이터를 가져와 한국어 이름을 붙여 docs/data.json 으로 저장한다."""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
API = "https://jflpzvmpjeeqfkvqppuq.supabase.co/rest/v1/leaderboards"
PAGE = 100
HAN = re.compile(r"[\u4e00-\u9fff]")
TIER_KEY = re.compile(r"^(\d+(?:\.\d+)?)%$")

GLOSSARY_PATH = ROOT / "glossary.json"
CACHE_PATH = ROOT / "translation_cache.json"
OUT_PATH = ROOT / "docs" / "data.json"


def load_json(path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def fetch_all(key):
    rows, offset = [], 0
    while True:
        url = f"{API}?select=*&order=updated_at.desc,id.desc&offset={offset}&limit={PAGE}"
        req = urllib.request.Request(
            url, headers={"apikey": key, "Authorization": f"Bearer {key}"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            batch = json.load(resp)
        rows += batch
        if len(batch) < PAGE:
            return rows
        offset += PAGE


def apply_glossary(text, glossary):
    for zh in sorted(glossary, key=len, reverse=True):
        text = text.replace(zh, glossary[zh])
    return re.sub(r"\s+", " ", text).strip()


def translate_api(text):
    """용어집으로 해결되지 않은 이름만 Claude API로 번역한다. 키가 없으면 None."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    prompt = (
        "모바일 레이싱 게임 Asphalt Legends(狂野飙车传奇)의 중국어 대회 이름을 "
        "자연스러운 한국어로 번역하세요. 차량명·영문·숫자는 그대로 두고, "
        "번역 결과만 한 줄로 출력하세요.\n\n" + text
    )
    body = json.dumps(
        {
            "model": os.environ.get("TRANSLATE_MODEL", "claude-haiku-5-5"),
            "max_tokens": 100,
            "messages": [{"role": "user", "content": prompt}],
        }
    ).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.load(resp)
        return data["content"][0]["text"].strip()
    except Exception as exc:  # 번역 실패가 전체 갱신을 막지 않게 한다
        print(f"번역 API 실패 ({text}): {exc}", file=sys.stderr)
        return None


def translate_name(zh, glossary, cache):
    ko = apply_glossary(zh, glossary)
    if not HAN.search(ko):
        return ko
    if zh in cache:
        return cache[zh]
    translated = translate_api(zh)
    if translated:
        cache[zh] = translated
        return translated
    print(f"번역 필요: {zh}  (glossary.json에 추가하세요)", file=sys.stderr)
    return ko


def parse_tiers(raw):
    """'10%' 형식의 키만 골라 [{'pct','rank'}] 로 만든다. 다른 형식은 건너뛴다."""
    tiers = []
    if not isinstance(raw, dict):
        return tiers
    for key, value in raw.items():
        match = TIER_KEY.match(str(key))
        if not match or not isinstance(value, (int, float)):
            continue
        pct = float(match.group(1))
        tiers.append({"pct": int(pct) if pct.is_integer() else pct, "rank": int(value)})
    return sorted(tiers, key=lambda t: t["pct"])


def build_event(row, glossary, cache):
    zh = (row.get("event_name") or "").strip()
    return {
        "id": row["id"],
        "name_ko": translate_name(zh, glossary, cache),
        "name_zh": zh,
        "status": row.get("status"),
        "total": row.get("total_participants"),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "tiers": parse_tiers(row.get("tier_ranks")),
    }


def main():
    key = os.environ.get("SUPABASE_ANON_KEY")
    if not key:
        sys.exit("SUPABASE_ANON_KEY 환경변수가 필요합니다.")

    rows = fetch_all(key)
    if not rows:
        sys.exit("받아온 데이터가 없어 data.json을 덮어쓰지 않습니다.")

    glossary = load_json(GLOSSARY_PATH, {})
    cache = load_json(CACHE_PATH, {})

    events = [build_event(r, glossary, cache) for r in rows]
    result = {
        "latest_update": max(e["updated_at"] for e in events if e["updated_at"]),
        "events": events,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    CACHE_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(f"{len(events)}개 대회 저장 완료")


if __name__ == "__main__":
    main()
