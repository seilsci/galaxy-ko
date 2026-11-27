# 아스팔트 레전드 순위 컷 (galaxy-ko) — 작업 안내 (새 세션은 이 파일부터 읽음)

Asphalt Legends Galaxy 클럽 대회 순위 컷을 한국어로 보여 주는 정적 사이트. 사이트: https://seilsci.github.io/galaxy-ko/ (GitHub Pages = main의 `/docs`, push하면 1~2분 안에 배포).

## 소통·작업 방식 (사용자 선호)
- **한국어**로, 짧고 바로 쓸 수 있게. 숫자는 표로. 남에게 설명할 글은 세부 수치를 뺀 불릿으로.
- 폰으로 작업할 때가 많음 → 코드는 파일로 주지 말고 **복붙하기 좋은 풀코드**로(한 줄만 바뀌어도 해당 함수 전체).
- 디자인 변경은 **미리보기 이미지를 먼저** 보여 주고 확인받기.
- 오래 걸리는 일은 단계 끝날 때마다 "무슨 단계 끝 / 전체 n/N / 현재시각(KST) / 100% 예상 시각". 시각은 한국 시간(KST).
- 스크린샷의 특이한 점(이상한 값·중복 등)은 먼저 짚어 주기.
- **main 반영: 사용자가 "앞으로 묻지 말고 올려"라고 함 → 확인(문법·화면)한 변경은 바로 main에 올림**(빨리감기일 때만, 강제 push·기록 다시 쓰기 금지). Actions 봇이 매시간 커밋하므로 push 전에 `git fetch origin main`으로 최신을 받아 그 위에 올릴 것.
- 개인정보·API 키는 저장소·외부 요청에 넣지 않음(키는 저장소 Secrets: `SUPABASE_ANON_KEY`, `ANTHROPIC_API_KEY`).

## 파일 구성
- `crawl.py`: 순위 데이터를 받아 `docs/data.json` 생성(대회 이름은 `glossary.json`·`translation_cache.json`으로 번역), 매번 `history.py`로 `docs/history.json`에 점 추가.
- `history.py`: 시간대별 기록 함수. `docs/history.json` 형식 `{"v":1,"events":{id:[[epoch초,총인원,[순위들],[퍼센트들]?],...]}}`, **값이 바뀔 때만** 점 추가.
- `tools/backfill_history.py`: 과거 커밋(606개)의 data.json에서 기록 복원(대회 232개·3,904점).
- `docs/index.html`: 화면. 카드마다 "📈 시간대별 그래프" 버튼 → 꺾은선 그래프 창(닫기 ✕·바깥 클릭·Esc, 기간 전체/7일/3일/24시간, 선형(기본)/로그 눈금, 상위 % 칩으로 선 켜고 끄기, 마우스 올리면 표 형태 말풍선(시각·각 컷 순위·참가자), 터치하면 말풍선 유지, 화면 밖으로 안 삐져나감).
- `.github/workflows/update.yml`: 매시 23분(cron) + workflow_dispatch로 `crawl.py` 실행, 바뀌면 `docs/data.json`·`docs/history.json`·`translation_cache.json`을 "데이터 갱신"으로 커밋. `glossary.json`을 push해도 바로 실행.

## 확인할 것
- 배포된 사이트의 폰 화면·그래프 시간 눈금 간격.
- 자동 실행에서 history.json이 갱신 커밋되는지(Actions 탭). 참고: 11/27 아침 기준 5분마다 workflow_dispatch 실행(외부에서 호출)이 성공 중이고, 값이 안 바뀌면 커밋이 없음.
