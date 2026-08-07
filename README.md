# AI Office OS

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

## API 문서

http://127.0.0.1:8000/docs

## 진행 상황

52주 로드맵 기준 개발 중입니다. 전체 계획은 [`docs/roadmap.md`](docs/roadmap.md) 참고.

- [x] Phase 0: 개발 환경 구축
- [x] Phase 1: 로그인 시스템
- [x] Phase 2: 문서 관리
- [x] Phase 3: RAG 문서 검색
- [x] Phase 4: AI 문서 분석
- [x] Phase 5: 보고서 생성
- [x] Phase 6: AI 이메일 작성
