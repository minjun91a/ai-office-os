# AI Office OS 52주 개발 로드맵

## 프로젝트 개요

**AI Office OS**는 기업용 AI 업무 비서 플랫폼을 목표로 하는 포트폴리오 프로젝트다.

처음에는 **RAG 기반 문서 비서**로 시작하고, 이후 문서 요약, 보고서 작성, 이메일 초안, AI Agent, 외부 서비스 연동, 배포까지 확장한다.

최종적으로는 다음과 같은 서비스의 축소판을 목표로 한다.

> Notion AI + ChatGPT Team + Google Workspace 핵심 기능을 축소 구현한 기업용 AI 협업 플랫폼

## 최종 목표

- 회원가입 / 로그인 / 권한 관리
- 문서 업로드 / 삭제 / 다운로드
- PDF, Word, Excel 문서 관리
- RAG 기반 문서 검색
- AI 답변 생성
- 문서 요약 / 키워드 추출 / 액션 아이템 생성
- 보고서 / 회의록 / 이메일 초안 생성
- LangGraph 기반 AI Agent
- Gmail / Google Calendar / Slack / Notion 연동
- 관리자 페이지
- Docker 기반 배포
- GitHub Actions CI/CD
- AWS 배포

## 추천 기술 스택

| 영역 | 기술 |
|---|---|
| Backend | Python, FastAPI |
| Database | PostgreSQL, SQLAlchemy, Alembic |
| AI | OpenAI API, RAG, LangGraph, LangChain 일부 활용 |
| Vector DB | ChromaDB 또는 Qdrant |
| Frontend | React, TypeScript |
| Infra | Docker, Docker Compose, GitHub Actions, AWS |
| 협업/문서 | GitHub, README, Architecture Docs, Blog |

---

# 전체 52주 로드맵

## Phase 0. 개발 환경 구축 (1~2주)

### 목표

개발자처럼 일할 수 있는 기본 환경을 만든다.

### 핵심 결과물

- GitHub 저장소
- 기본 프로젝트 폴더 구조
- README
- 커밋 규칙
- Python 가상환경
- FastAPI Hello World 서버
- Docker 기초 실행
- 첫 번째 의미 있는 커밋

---

## Phase 1. 로그인 시스템 (3~6주)

### 목표

실무 백엔드의 기본인 인증 시스템을 만든다.

### 기능

- 회원가입
- 로그인
- JWT 발급
- JWT 검증
- 비밀번호 해싱
- 사용자 권한 관리
- 내 정보 조회 API

### 기술

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- JWT

### 결과물

- 인증 API 문서
- users 테이블
- 로그인 테스트
- 인증이 필요한 API 예시

---

## Phase 2. 문서 관리 (7~10주)

### 목표

사용자가 업무 문서를 업로드하고 관리할 수 있게 만든다.

### 기능

- PDF 업로드
- Word 업로드
- Excel 업로드
- 문서 목록 조회
- 문서 상세 조회
- 문서 삭제
- 문서 다운로드
- 파일 크기 제한
- 파일 타입 검사

### 결과물

- documents 테이블
- 파일 저장 구조
- 문서 관리 API
- 업로드 실패 케이스 처리

---

## Phase 3. RAG 문서 검색 (11~15주)

### 목표

업로드한 문서에 질문하면 AI가 문서 기반으로 답변하게 만든다.

### 처리 흐름

```text
문서 업로드
-> 텍스트 추출
-> Chunking
-> Embedding
-> Vector DB 저장
-> 사용자 질문
-> 관련 Chunk 검색
-> AI 답변 생성
```

### 기술

- OpenAI Embeddings
- ChromaDB 또는 Qdrant
- LangChain 일부 활용
- 문서 Chunking 전략

### 결과물

- 문서 기반 Q&A API
- 출처 Chunk 표시
- 검색 품질 비교 기록
- RAG 구조 설명 문서

---

## Phase 4. AI 문서 분석 (16~20주)

### 목표

문서를 단순 검색하는 수준을 넘어 업무에 바로 쓸 수 있는 분석 결과를 만든다.

### 기능

- 긴 문서 요약
- 핵심 키워드 추출
- 액션 아이템 생성
- 담당자 / 마감일 추출
- 중요도 분류
- 회의록 분석

### 결과물

- 문서 분석 API
- 분석 결과 저장 구조
- 요약 품질 개선 기록

---

## Phase 5. 보고서 생성 (21~25주)

### 목표

문서 내용을 바탕으로 실무형 산출물을 생성한다.

### 기능

- Markdown 보고서 생성
- 회의록 생성
- 업무 보고서 생성
- PPT 초안 구조 생성
- Word 문서 초안 구조 생성

### 결과물

- 보고서 생성 API
- 보고서 템플릿
- 생성 결과 미리보기
- 다운로드 가능한 Markdown 파일

---

## Phase 6. AI 이메일 작성 (26~30주)

### 목표

문서 내용을 기반으로 이메일 초안을 작성한다.

### 기능

- 이메일 제목 생성
- 이메일 본문 생성
- 정중한 톤 / 간결한 톤 / 보고용 톤 변경
- 한국어 / 영어 번역
- 문서 요약 기반 이메일 작성

### 결과물

- 이메일 초안 생성 API
- 톤 선택 기능
- 이메일 작성 UI

---

## Phase 7. AI Agent (31~36주)

### 목표

AI가 사용자의 요청을 이해하고 여러 도구를 순서대로 실행하게 만든다.

### 예시 요청

```text
회의자료를 읽고 팀원에게 보낼 이메일 초안을 작성해줘.
```

### Agent 처리 흐름

```text
사용자 요청
-> 의도 파악
-> 필요한 도구 선택
-> 문서 검색
-> 문서 요약
-> 이메일 초안 작성
-> 결과 반환
```

### 기술

- LangGraph
- Tool Calling
- Agent State
- Workflow 설계

### 결과물

- Agent 실행 그래프
- Tool 목록
- Agent 로그
- 실패 / 재시도 처리

---

## Phase 8. 외부 서비스 연동 (37~42주)

### 목표

AI Office OS를 실제 업무 도구와 연결한다.

### 연동 후보

- Gmail
- Google Calendar
- Slack
- Notion
- Google Drive

### 기능

- 이메일 초안 외부 전송 준비
- 캘린더 일정 생성 준비
- Slack 메시지 초안 작성
- Notion 페이지 초안 생성
- Google Drive 문서 가져오기

### 주의

처음에는 실제 발송보다 **초안 생성과 사용자 확인 후 실행** 구조로 만드는 것이 좋다.

---

## Phase 9. 관리자 페이지 (43~47주)

### 목표

서비스 운영 관점의 기능을 추가한다.

### 기능

- 사용자 관리
- 문서 업로드 통계
- AI 사용량 통계
- API 호출 로그
- 에러 로그 조회
- 조직별 사용량 조회

### 결과물

- 관리자 대시보드
- 로그 테이블
- 사용량 통계 API

---

## Phase 10. 배포와 운영 (48~52주)

### 목표

포트폴리오를 실제 서비스처럼 배포하고 운영 가능하게 만든다.

### 기능

- Docker 이미지 빌드
- Docker Compose 구성
- 환경변수 관리
- GitHub Actions CI/CD
- AWS 배포
- HTTPS 적용
- 도메인 연결
- 배포 문서 작성

### 결과물

- 배포된 서비스 URL
- GitHub README 완성
- 아키텍처 문서
- 시연 영상
- 최종 회고 글

---

# Phase 0 상세 실행 계획

## Phase 0의 핵심 목표

Phase 0은 기능을 많이 만드는 단계가 아니다.

이 단계의 목표는 다음 한 문장으로 정리된다.

> 앞으로 1년 동안 확장 가능한 프로젝트의 뼈대를 만든다.

좋은 Phase 0은 다음을 만족해야 한다.

- 새 개발자가 저장소를 받아도 실행 방법을 이해할 수 있다.
- 폴더 구조가 백엔드, 프론트엔드, 문서, 배포 파일로 분리되어 있다.
- FastAPI 서버가 정상 실행된다.
- GitHub에 커밋 히스토리가 남아 있다.
- Docker가 왜 필요한지 이해하고 기본 명령을 실행해봤다.

---

## Phase 0 기간

권장 기간: **1~2주**

| 기간 | 목표 |
|---|---|
| 1주차 | 개발 도구 설치, GitHub 저장소 생성, 프로젝트 구조 생성, FastAPI 실행 |
| 2주차 | Docker 기초, README 정리, 커밋 규칙 정리, Phase 1 준비 |

---

## 설치할 항목

### 필수

- Git
- GitHub 계정
- VS Code
- Python 3.14.x
- Docker Desktop
- Node.js LTS

### VS Code 추천 확장

- Python
- Pylance
- Ruff
- Docker
- GitLens
- REST Client
- Prettier
- ESLint

### 계정 준비

- GitHub
- OpenAI Platform 계정
- AWS 계정은 Phase 10 전에 준비해도 된다.

---

## 추천 프로젝트 이름

```text
ai-office-os
```

GitHub 저장소 이름도 동일하게 맞추는 것을 추천한다.

---

## 초기 폴더 구조

```text
ai-office-os/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   └── __init__.py
│   │   ├── core/
│   │   │   └── __init__.py
│   │   ├── models/
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   └── __init__.py
│   │   └── services/
│   │       └── __init__.py
│   ├── tests/
│   │   └── __init__.py
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   └── README.md
├── docker/
│   └── README.md
├── docs/
│   ├── architecture.md
│   ├── roadmap.md
│   └── phase-0.md
├── .gitignore
├── README.md
└── docker-compose.yml
```

### 구조 설계 이유

- `backend/`: FastAPI 서버와 백엔드 로직
- `frontend/`: React 프론트엔드. Phase 0에서는 비워둬도 된다.
- `docker/`: Docker 관련 문서와 설정
- `docs/`: 설계 문서, 로드맵, 회고
- `tests/`: 테스트 코드

처음부터 완벽한 구조를 만들 필요는 없다. 다만 `backend`, `frontend`, `docs`를 분리해두면 이후 확장이 편하다.

---

## Git / GitHub 설정

## 1. Git 사용자 정보 설정

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

## 2. 저장소 생성

GitHub에서 새 저장소를 만든다.

추천 설정:

- Repository name: `ai-office-os`
- Visibility: Public 또는 Private
- README 생성: 선택하지 않아도 된다. 로컬에서 직접 만든다.
- .gitignore: 선택하지 않아도 된다. 로컬에서 직접 만든다.

## 3. 로컬 프로젝트 초기화

```bash
mkdir ai-office-os
cd ai-office-os
git init
```

## 4. 원격 저장소 연결

```bash
git remote add origin https://github.com/YOUR_NAME/ai-office-os.git
```

## 5. 첫 커밋

```bash
git add .
git commit -m "chore: initialize project structure"
git branch -M main
git push -u origin main
```

---

## Python 가상환경 설정

## 1. 백엔드 폴더 이동

```bash
cd backend
```

## 2. 가상환경 생성

```bash
python -m venv .venv
```

## 3. 가상환경 활성화

Windows Git Bash 기준:

```bash
source .venv/Scripts/activate
```

PowerShell 기준:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 4. 패키지 설치

```bash
pip install fastapi uvicorn
```

## 5. requirements.txt 생성

```bash
pip freeze > requirements.txt
```

---

## FastAPI Hello World 만들기

## 1. 파일 생성

경로:

```text
backend/app/main.py
```

내용:

```python
from fastapi import FastAPI

app = FastAPI(title="AI Office OS API")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "AI Office OS API is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
```

## 2. 서버 실행

`backend` 폴더에서 실행한다.

```bash
uvicorn app.main:app --reload
```

## 3. 확인할 주소

- API 기본 주소: `http://127.0.0.1:8000`
- Swagger 문서: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/health`

정상 결과:

```json
{
  "status": "ok"
}
```

---

## Docker 기초

Phase 0에서 Docker를 완벽히 익힐 필요는 없다.

목표는 다음 정도면 충분하다.

- Docker가 왜 필요한지 이해한다.
- Docker Desktop을 설치한다.
- `docker --version`을 실행해본다.
- `docker compose version`을 실행해본다.
- PostgreSQL을 나중에 Docker로 띄울 수 있다는 것을 이해한다.

## Docker가 필요한 이유

개발 환경을 고정하기 위해서다.

예를 들어 내 컴퓨터에서는 되는데 다른 컴퓨터에서는 안 되는 문제를 줄일 수 있다.

AI Office OS에서는 이후 다음 용도로 Docker를 사용한다.

- FastAPI 서버 실행
- PostgreSQL 실행
- Vector DB 실행
- 배포 환경 구성

## Phase 0용 docker-compose.yml 초안

아직 PostgreSQL을 실제로 연결하지 않아도 된다.

```yaml
services:
  api:
    image: python:3.14-slim
    working_dir: /app
    volumes:
      - ./backend:/app
    command: bash -lc "pip install -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port 8000"
    ports:
      - "8000:8000"
```

실행:

```bash
docker compose up
```

중지:

```bash
docker compose down
```

---

## README에 넣을 내용

루트 `README.md`에는 최소한 다음 항목을 넣는다.

```markdown
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
- AI: OpenAI API, RAG, LangGraph
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
```

---

## .gitignore 기본값

```gitignore
# Python
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Virtual environment
.venv/
venv/

# Environment variables
.env
.env.*

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/

# Logs
*.log

# Node
node_modules/
dist/
build/
```

---

## 커밋 규칙

처음부터 커밋 메시지 규칙을 정해두면 포트폴리오 품질이 좋아진다.

추천 규칙:

```text
type: message
```

예시:

```text
chore: initialize project structure
docs: add project roadmap
feat: add FastAPI health check endpoint
fix: handle invalid login request
test: add user service tests
refactor: reorganize auth module
```

## type 목록

| type | 의미 |
|---|---|
| feat | 새 기능 |
| fix | 버그 수정 |
| docs | 문서 수정 |
| chore | 설정, 빌드, 기타 작업 |
| test | 테스트 추가 / 수정 |
| refactor | 동작 변경 없는 구조 개선 |
| style | 포맷팅, 코드 스타일 |

## 브랜치 전략

초기에는 단순하게 시작한다.

```text
main
feature/phase-1-auth
feature/phase-2-documents
feature/phase-3-rag
```

원칙:

- `main`은 항상 실행 가능한 상태로 유지한다.
- 새 기능은 `feature/...` 브랜치에서 작업한다.
- 기능이 끝나면 Pull Request로 병합한다.

혼자 하는 프로젝트라도 Pull Request를 사용하면 실무 협업 흐름을 보여줄 수 있다.

---

## Phase 0 완료 기준

아래 항목이 모두 끝나면 Phase 0 완료로 본다.

- GitHub 저장소가 생성되어 있다.
- 로컬 프로젝트와 원격 저장소가 연결되어 있다.
- `backend`, `frontend`, `docs`, `docker` 폴더가 있다.
- Python 가상환경이 생성되어 있다.
- FastAPI 서버가 실행된다.
- `/health` API가 `{"status": "ok"}`를 반환한다.
- `requirements.txt`가 있다.
- `.gitignore`가 있다.
- 루트 `README.md`가 있다.
- `docs/roadmap.md`가 있다.
- 최소 3개 이상의 의미 있는 커밋이 있다.
- Docker Desktop 설치와 버전 확인이 끝났다.
- `docker compose up`을 한 번 실행해봤다.

---

# 첫날 해야 할 일 체크리스트

## Day 1 목표

오늘의 목표는 거창한 기능 구현이 아니다.

**GitHub 저장소를 만들고, FastAPI 서버를 실행해서 브라우저에 API 문서가 뜨게 만드는 것**이 목표다.

## Day 1 체크리스트

- [ ] Git 설치 확인
- [ ] GitHub 계정 로그인 확인
- [ ] VS Code 설치 확인
- [ ] Python 설치 확인
- [ ] Docker Desktop 설치 시작 또는 설치 확인
- [ ] GitHub에 `ai-office-os` 저장소 생성
- [ ] 로컬에 `ai-office-os` 폴더 생성
- [ ] `git init` 실행
- [ ] 기본 폴더 구조 생성
- [ ] `.gitignore` 생성
- [ ] 루트 `README.md` 생성
- [ ] `backend` 폴더에서 Python 가상환경 생성
- [ ] FastAPI / Uvicorn 설치
- [ ] `backend/app/main.py` 작성
- [ ] `uvicorn app.main:app --reload` 실행
- [ ] `http://127.0.0.1:8000/docs` 접속 확인
- [ ] `http://127.0.0.1:8000/health` 접속 확인
- [ ] 첫 커밋 생성

## Day 1 추천 커밋 순서

```bash
git add .
git commit -m "chore: initialize project structure"
```

FastAPI 서버까지 만든 뒤:

```bash
git add .
git commit -m "feat: add FastAPI health check"
```

README 정리 후:

```bash
git add .
git commit -m "docs: add setup instructions"
```

---

# Phase 0 이후 바로 이어질 일

Phase 0이 끝나면 바로 Phase 1로 넘어간다.

Phase 1에서 가장 먼저 할 일은 다음 순서다.

1. PostgreSQL을 Docker Compose에 추가한다.
2. SQLAlchemy를 설치한다.
3. User 모델을 만든다.
4. Alembic 마이그레이션을 설정한다.
5. 회원가입 API를 만든다.
6. 비밀번호 해싱을 적용한다.
7. 로그인 API와 JWT 발급을 만든다.

---

# 블로그 작성 계획

포트폴리오 프로젝트는 코드만 있으면 약하다.

각 Phase가 끝날 때마다 블로그 글을 1~2개 작성하면 좋다.

## 추천 글감

- Phase 0: AI Office OS 프로젝트를 시작한 이유
- Phase 0: FastAPI 개발 환경 구축 기록
- Phase 1: JWT 인증 시스템 구현기
- Phase 1: PostgreSQL 사용자 테이블 설계 과정
- Phase 3: RAG에서 Chunking 전략 비교
- Phase 3: ChromaDB를 선택한 이유
- Phase 7: LangGraph로 AI Agent Workflow 설계하기
- Phase 10: Docker와 AWS로 FastAPI 서비스 배포하기

---

# 포트폴리오에서 강조할 포인트

면접에서 이 프로젝트를 설명할 때 핵심은 다음이다.

```text
단순 챗봇을 만든 것이 아니라,
기업 문서를 기반으로 검색, 요약, 보고서 생성, 이메일 작성, Agent Workflow, 외부 서비스 연동까지 확장 가능한 업무 자동화 플랫폼을 설계하고 구현했습니다.
```

강조할 기술 흐름:

```text
FastAPI
-> PostgreSQL
-> 파일 업로드
-> RAG
-> Vector DB
-> OpenAI API
-> LangGraph Agent
-> Tool Calling
-> Docker
-> CI/CD
-> AWS 배포
```

---

# 지금 바로 시작하는 순서

가장 먼저 할 일은 이것이다.

1. GitHub에서 `ai-office-os` 저장소를 만든다.
2. 로컬에 `ai-office-os` 폴더를 만든다.
3. `backend`, `frontend`, `docs`, `docker` 폴더를 만든다.
4. FastAPI Hello World를 실행한다.
5. `/health` API를 만든다.
6. README에 실행 방법을 적는다.
7. GitHub에 첫 커밋을 올린다.

오늘은 여기까지만 해도 충분하다.

