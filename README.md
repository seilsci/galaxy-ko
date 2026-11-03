# 아스팔트 레전드 순위 컷 (한국어)

狂野飙车传奇 Galaxy 클럽 순위 데이터를 매시간 가져와 한국어로 보여주는 정적 사이트입니다.

## 구조
- `crawl.py` : 데이터를 가져와 `docs/data.json` 생성 (대회 이름은 `glossary.json`으로 번역)
- `docs/index.html` : 화면 (GitHub Pages로 공개)
- `.github/workflows/update.yml` : 매시간 `crawl.py`를 실행하고 바뀐 데이터를 커밋

## 설정 (한 번만)
1. 이 폴더를 GitHub 저장소에 올립니다.
2. 저장소 **Settings → Secrets and variables → Actions → New repository secret**에 등록합니다.
   - `SUPABASE_ANON_KEY` (필수): 원본 사이트에서 크롬 F12 → Network → `leaderboards` 요청 → Request Headers의 `apikey` 값
   - `ANTHROPIC_API_KEY` (선택): 용어집에 없는 새 대회 이름을 자동 번역할 때만 필요
3. **Settings → Pages**에서 Source를 `Deploy from a branch`, Branch를 `main` / `/docs`로 지정합니다.
4. **Actions → update-data → Run workflow**로 첫 데이터를 만듭니다.

## 로컬 테스트
```
SUPABASE_ANON_KEY=여기에키 python crawl.py
python -m http.server -d docs 8000
```
브라우저에서 http://localhost:8000 을 엽니다.

## 번역 고치기
`glossary.json`에 `"중국어": "한국어"`를 추가하면 다음 실행부터 반영됩니다.
실행 로그에 "번역 필요"가 보이면 그 단어를 추가하세요.
