# AI Office OS

![CI](https://github.com/minjun91a/ai-office-os/actions/workflows/ci.yml/badge.svg)

기업용 AI 업무 비서 플랫폼 포트폴리오 프로젝트입니다.

## 목표

- 문서 관리
- RAG 기반 문서 검색
- AI 문서 요약
- AI 이메일 작성
- AI Agent Workflow
- 외부 서비스 연동
- 배포

## 기술 스택

- Backend: Python, FastAPI
- Database: PostgreSQL
- AI: Anthropic Claude (답변 생성/요약/Agent), sentence-transformers 로컬 임베딩 (RAG 벡터 검색)
- Vector DB: ChromaDB
- Agent: LangGraph (Plan → Execute → Finish/Fail 워크플로우)
- 외부 연동: Gmail API (OAuth 2.0, 초안 자동 생성)
- 운영/관리: 멀티테넌트(Organization) 구조, role 기반 접근 제어(user/admin/superadmin), API 요청 로깅 미들웨어
- Frontend: React, TypeScript
- Infra: Docker, GitHub Actions, AWS

## 실행 방법

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Docker로 실행

```bash
docker compose up -d
```
`db`(PostgreSQL), `chroma`(ChromaDB), `api`(FastAPI) 3개 컨테이너가 한 번에 뜹니다.

## API 문서

http://127.0.0.1:8000/docs

## 애드온: 문서 ↔ ERP 교차 검증

RAG의 구조적 한계는 문서가 작성 시점에 박제된다는 점입니다. 회의록에 "안전재고 320 EA"라고
적혀 있으면, 3일 뒤 실제 재고가 285 EA가 되어도 RAG는 320이라고 답합니다. 인용도 정확하고
근거율도 높은데, 틀렸습니다.

이 애드온은 QA 답변에서 수치 주장을 정규식으로 추출해 ERP 마스터 데이터와 자동 대조하고,
불일치가 발견되면 답변에 정정 문단을 덧붙입니다. 대조 이력은 `qa_logs`/`cross_checks` 테이블에
영구 저장되어 관리자 대시보드(`GET /admin/stats/erp-cross-checks`)에서 조직 단위로 추적할 수
있습니다.

| 판정 | 의미 |
|---|---|
| `match` | 허용 오차 내 일치 |
| `stale_document` | 문서가 ERP보다 오래됐고 값이 다름 → 답변에 정정 삽입 |
| `conflict` | 값이 다른데 시점으로 설명 안 됨 → 사람 확인 필요 |
| `not_applicable` | ERP에 대조 대상 없음 → 감점 없음 |

`ERP_ENABLED`/`ERP_CROSS_CHECK_ENABLED` 플래그로 켜고 끄며, 기본값은 `false`(비활성)입니다.
설계 배경은 [`docs/addons/erp-module.md`](docs/addons/erp-module.md) 참고.

## 진행 상황

52주 로드맵 기준 개발 중입니다. 전체 계획은 [`docs/roadmap.md`](docs/roadmap.md) 참고.

- [x] Phase 0: 개발 환경 구축
- [x] Phase 1: 로그인 시스템
- [x] Phase 2: 문서 관리
- [x] Phase 3: RAG 문서 검색
- [x] Phase 4: AI 문서 분석
- [x] Phase 5: 보고서 생성
- [x] Phase 6: AI 이메일 작성
- [x] Phase 7: AI Agent
- [x] Phase 8: 외부 서비스 연동 (Gmail)
- [x] Phase 9: 관리자 페이지 (사용자/조직 관리, 사용량 통계, 에러 로그)
- [ ] Phase 10: 배포와 운영 (Docker Compose + GitHub Actions CI 완료, AWS 배포 진행 중)
