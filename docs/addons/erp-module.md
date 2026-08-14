# ERP 모듈 애드온 (AI Office OS 구조 기준 재설계)

> **이 문서만으로 완결됩니다.** 기존 README, ROADMAP, 기존 Phase 문서는 수정하지 않습니다.
> 저장 위치: `docs/addons/erp-module.md`
>
> **재설계 이력**: 최초 버전은 `Settings(BaseSettings)`, UUID PK, 클래스 기반 RAG 서비스,
> `RiskLevel` 승인 레지스트리, `messages` 채팅 이력 테이블을 전제로 작성됨 — AI Office OS에는
> 전부 존재하지 않는 구조. 이 버전은 실제 AI Office OS 코드베이스(Phase 0~9 기준)에 맞춰 전면
> 재작성함. 핵심 결정 2가지(사용자 확인 완료):
> 1. 대조 결과는 **`qa_logs` 테이블에 영구 저장**한다 (Phase 9 관리자 대시보드에서 통계로 활용 목적).
> 2. ERP 쓰기 도구 승인은 **경량 버전**(단일 게이트 함수)으로 시작 — 나중에 정규화된 레지스트리로
>    옮겨도 마이그레이션 비용이 거의 없도록 게이트 체크를 한 곳에만 둔다.

---

# 0. 설계 원칙 — 기존 것을 깨지 않는다

| 원칙 | 방법 |
|---|---|
| 기존 테이블 스키마 변경 없음 | 신규 테이블만 추가. `documents`, `users` 등에 컬럼 추가 **안 함** |
| 기존 API 응답 스키마 변경 없음 | `AnswerOut`에 신규 필드는 **옵셔널**로만 추가 |
| 기존 QA 파이프라인 동작 유지 | 기능 플래그로 감쌈. `ERP_ENABLED=false`면 이전과 100% 동일 |
| 롤백 가능 | 마이그레이션 downgrade + 플래그 off로 원상 복구 |
| 기존 테스트 깨지지 않음 | 플래그 기본값 `false`. 기존 10개 스모크테스트는 그대로 통과 |

**핵심: 기능 플래그부터 만들고 시작합니다.** AI Office OS엔 `Settings(BaseSettings)` 같은 중앙 설정
클래스가 없고 각 파일이 `os.getenv()`를 직접 읽습니다(`app/core/security.py` 등 기존 관행). 이 관행을
따르되, 파싱 로직 중복을 막기 위해 ERP 전용 얇은 헬퍼 하나만 신설합니다(`app/core/erp_config.py`) —
기존 파일의 config 읽는 방식은 전혀 건드리지 않습니다.

---

# 1. 신규 파일 목록 (전부 새로 만듦)

```
backend/app/core/erp_config.py                     ← ERP_ENABLED 등 플래그 읽기 전용 헬퍼

backend/app/models/erp_material.py
backend/app/models/erp_stock_snapshot.py
backend/app/models/erp_bom.py
backend/app/models/erp_inbound_schedule.py
backend/app/models/erp_production_plan.py
backend/app/models/erp_shipment_plan.py
backend/app/models/qa_log.py                        ← 질문/답변 영구 저장(신규 — QA를 stateful로 만듦)
backend/app/models/cross_check.py                   ← qa_log_id FK (messages 테이블 없음)

backend/app/schemas/erp.py
backend/app/schemas/qa_log.py

backend/app/services/erp/
├── __init__.py
├── metrics.py          ← MetricKey, TOLERANCE
├── repository.py        ← DB 쿼리 (org 스코프 필수)
└── service.py            ← coverage_weeks 등 계산

backend/app/services/trust/
├── __init__.py
├── claim_extractor.py    ← 정규식 기반 주장 추출
├── erp_resolver.py       ← (part_no, metric) 배치 조회
└── cross_validator.py    ← 판정 로직

backend/app/services/agent/approval.py              ← 경량 승인 게이트 (단일 함수)

backend/app/api/erp.py

backend/alembic/versions/xxxx_erp_master_tables.py       ← erp_materials, erp_stock_snapshots
backend/alembic/versions/xxxx_erp_transaction_tables.py  ← bom/inbound/production/shipment
backend/alembic/versions/xxxx_qa_log_and_cross_checks.py ← qa_logs, cross_checks

backend/scripts/seed_erp.py

backend/tests/test_erp_flag.py
backend/tests/test_cross_validation.py
backend/tests/test_erp_query_security.py

docs/addons/erp-module.md              ← 이 문서
docs/adr/xxxx-erp-as-domain-module.md  ← 신규 (선택)
```

**기존 파일 대비 구조 차이 요약**:
- `app/modules/erp/` (원본) → `app/services/erp/` (AI Office OS의 `app/services/agent/`처럼 서비스
  하위 패키지로)
- `app/ai/tools/`, `app/ai/trust/` (원본) → `app/services/trust/` (신규 최상위 `ai/` 디렉토리를
  만들지 않음 — 기존 `app/api`·`app/core`·`app/models`·`app/schemas`·`app/services` 5개 구조 유지)
- UUID PK → **Integer PK** (`Organization`, `User`, `Document` 등 기존 모델 전부 Integer)
- `org_id` → `organization_id` (기존 `User.organization_id`와 이름 통일)

---

# 2. 기존 파일 수정 — 3곳, 전부 추가만

## 2.1 `backend/app/core/erp_config.py` — 신규 파일 (기존 config 클래스가 없어서 수정이 아니라 신설)

```python
import os


def is_erp_enabled() -> bool:
    return os.getenv("ERP_ENABLED", "false").lower() == "true"


def is_cross_check_enabled() -> bool:
    return os.getenv("ERP_CROSS_CHECK_ENABLED", "false").lower() == "true"


ERP_QUERY_TIMEOUT_MS = int(os.getenv("ERP_QUERY_TIMEOUT_MS", "1500"))
```

`.env`에 3줄 추가 (`.env`는 gitignore 대상이라 저장소엔 안 들어감 — 로컬에서만 설정):
```
ERP_ENABLED=false
ERP_CROSS_CHECK_ENABLED=false
ERP_QUERY_TIMEOUT_MS=1500
```

함수로 감싼 이유: 매 호출 시 `os.getenv()`를 다시 읽으므로 **pytest에서 `monkeypatch.setenv()`로
플래그를 테스트마다 자유롭게 켜고 끌 수 있음** (import 시점에 고정되는 상수 방식이면 테스트가 어려움).

## 2.2 `backend/app/main.py` — 라우터 조건부 등록 (기존 패턴과 1:1로 동일)

```python
# 기존 include_router들 아래에 추가
from app.core.erp_config import is_erp_enabled

if is_erp_enabled():
    from app.api.erp import router as erp_router
    app.include_router(erp_router)
```

import를 조건문 안에 두면, 플래그가 꺼져 있을 때 ERP 모듈에 문법 오류가 있어도 앱이 뜹니다
(원본 설계와 동일한 안전장치).

## 2.3 `backend/app/api/qa.py` — 교차검증 훅 추가 (기존 `qa.py`/`app/services/qa.py`는 최소한만 터치)

현재 `POST /qa/ask`는 `search()` → `generate_answer()` → `AnswerOut(...)` 반환으로 끝나는 짧은
함수라서, 원본 문서처럼 "새 메서드 추가, 기존 메서드 0줄 수정"은 그대로는 안 됩니다(클래스가 아니라
함수라 오버라이드할 지점이 없음). 대신 **반환 직전에 3줄만 삽입**하는 형태로 최소화합니다:

```python
# app/api/qa.py, 기존 엔드포인트 안, AnswerOut을 만드는 부분을 아래처럼만 바꿈
from app.core.erp_config import is_cross_check_enabled
from app.services.trust.cross_validator import run_cross_check  # 신규

result = AnswerOut(answer=answer, sources=sources_out)

if is_cross_check_enabled():
    try:
        result = run_cross_check(
            db=db, user=current_user, question=question_in.question, result=result
        )
    except Exception:
        logger.warning("ERP cross-check failed", exc_info=True)
        # 실패해도 원래 답변을 그대로 반환한다

return result
```

**try/except 필수** — ERP가 죽어도 QA는 계속 답해야 합니다. `run_cross_check`는 내부에서
`qa_logs`/`cross_checks` 저장까지 처리하고, 매칭 안 되는 부분이 있으면 `result.answer`에 정정
문단을 덧붙인 새 `AnswerOut`을 반환합니다. **AI Office OS의 QA엔 "trust/grounded" 같은 신뢰도
필드가 애초에 없으므로**, 원본의 "trust downgrade" 개념은 쓰지 않고 **답변 텍스트에 정정 문단만
추가**하는 것으로 단순화합니다.

---

# 3. 신규 테이블 (기존 테이블 ALTER 없음, 전부 Integer PK)

## 3.1 QA 이력 (신규 — QA를 무상태→유상태로 전환하는 핵심 테이블)

**`qa_logs`** — 기존에 없던 "채팅 이력" 개념. `messages` 테이블이 없으므로 `cross_checks`가
참조할 앵커로 이 테이블을 새로 만듭니다.

| 컬럼 | 타입 | 비고 |
|---|---|---|
| id | Integer PK | |
| user_id | Integer FK → users.id | not null |
| organization_id | Integer FK → organizations.id | **nullable** (User.organization_id와 동일하게 미배정 허용) |
| question | Text | |
| answer | Text | 교차검증 정정 문단이 붙은 최종 답변 |
| created_at | DateTime(tz) | server_default now() |

## 3.2 대조 결과

**`cross_checks`**

| 컬럼 | 타입 | 비고 |
|---|---|---|
| id | Integer PK | |
| qa_log_id | Integer FK → qa_logs.id | not null, index (원본의 message_id 대체) |
| metric_key | String | |
| entity_key | String | 보통 part_no |
| claimed_value | Numeric(18,4) | nullable |
| claimed_source | String | 예: "문서 #12" |
| claimed_as_of | DateTime(tz) | nullable — `Document.uploaded_at`에서 옴(주의: `created_at` 아님) |
| erp_value | Numeric(18,4) | nullable |
| erp_as_of | DateTime(tz) | nullable |
| verdict | String | match / stale_document / conflict / not_applicable |
| delta | Numeric(18,4) | nullable |
| tolerance | Numeric(6,4) | |
| created_at | DateTime(tz) | server_default now() |

## 3.3 마스터 2개

**`erp_materials`**

| 컬럼 | 타입 | 비고 |
|---|---|---|
| id | Integer PK | |
| organization_id | Integer FK → organizations.id | not null, index |
| part_no | String | UniqueConstraint(organization_id, part_no) |
| name | String | |
| uom | String | EA / KG / TON |
| safety_stock | Numeric(14,2) | |
| lead_time_days | Integer | |
| unit_price | Numeric(14,2) | |
| vendor_name | String | |
| is_active | Boolean | default True |
| created_at | DateTime(tz) | |

**`erp_stock_snapshots`** — 이 테이블이 애드온의 핵심입니다

| 컬럼 | 타입 | 비고 |
|---|---|---|
| id, organization_id | | |
| part_no | String | |
| available_qty | Numeric(14,2) | |
| allocated_qty | Numeric(14,2) | |
| **as_of** | DateTime(tz) | **시점. 이게 없으면 "문서가 낡았다"를 증명 못 함** |

```python
__table_args__ = (
    Index("ix_erp_stock_latest", "organization_id", "part_no", "as_of"),
)
```

## 3.4 트랜잭션 4개

| 테이블 | 주요 컬럼 |
|---|---|
| `erp_boms` | parent_part_no, child_part_no, qty_per(Numeric), level(Integer), **alt_part_no**(nullable) |
| `erp_inbound_schedules` | po_no, part_no, qty, **original_eta**, **current_eta**, status, vendor_name |
| `erp_production_plans` | wo_no, part_no, planned_qty, start_date, end_date, status |
| `erp_shipment_plans` | so_no, customer, part_no, qty, requested_date, confirmed_date |

`original_eta` / `current_eta` 분리가 중요 — 나중에 "당초 계획 vs 현재"를 그릴 수 있음.
인덱스: `erp_boms (organization_id, child_part_no)` — 역전개가 주 조회 패턴.

전부 `organization_id` **not null** (User와 달리, ERP 데이터는 항상 특정 조직 소속).

---

# 4. MetricKey — 유일한 계약

`backend/app/services/erp/metrics.py`

```python
from enum import StrEnum


class MetricKey(StrEnum):
    SAFETY_STOCK = "safety_stock"
    AVAILABLE_STOCK = "available_stock"
    COVERAGE_WEEKS = "coverage_weeks"
    WEEKLY_DEMAND = "weekly_demand"
    # 아래는 나중에. 지금은 정의만 하고 not_applicable 반환
    LEAD_TIME_DAYS = "lead_time_days"
    INBOUND_ETA = "inbound_eta"
    BOM_QTY_PER = "bom_qty_per"
    ALT_PART_COUNT = "alt_part_count"


TOLERANCE = {
    MetricKey.COVERAGE_WEEKS: 0.05,
    MetricKey.INBOUND_ETA: 0.0,
    "__default__": 0.02,
}
```

**처음엔 위 4개(SAFETY_STOCK/AVAILABLE_STOCK/COVERAGE_WEEKS/WEEKLY_DEMAND)만 실제 구현합니다.**
나머지는 `not_applicable`로 반환하고 감점하지 않습니다.

---

# 5. ERP 조회/쓰기 — Agent 통합 방식

## 5.1 erp_query — Agent 도구로 등록하지 않음 (설계 변경 지점)

원본 문서는 `erp_query`를 `@tool` 데코레이터로 감싼 "에이전트가 스스로 고르는 도구"로 설계했지만,
AI Office OS의 Phase 7 Agent(`app/services/agent/plan.py`)는 **자연어 요청에서 도구 이름만
고르지, 파라미터(part_no 등)까지 구조화 추출하진 못합니다**. `erp_query`의 실제 호출자는
6절의 `erp_resolver`(자동 파이프라인)이므로, 굳이 LLM이 고르게 할 필요가 없습니다.

→ **`erp_query`는 그냥 평범한 서비스 함수로 둡니다**, `app/services/erp/repository.py`에:

```python
def query_facts(db: Session, organization_id: int, part_nos: list[str], metrics: list[MetricKey]) -> list[ErpFact]:
    ...
```

**보안**: `part_no`는 정규식 `^[A-Z]{2,3}-\d{4}(-[A-Z])?$` 통과 후에만 쿼리에 전달. LLM이 만든
문자열을 그대로 넣지 않습니다. `organization_id`는 항상 첫 인자, 기본값 금지(다른 관리자
엔드포인트들의 `_scoped_*_query` 관행과 동일).

## 5.2 erp_update_production_order — Agent 도구로 등록 (경량 승인)

이건 실제로 Phase 7 Agent가 자연어("WO-5521 시작일을 08-14로 바꿔줘")로 호출해야 하므로
`app/services/agent/tools.py`의 `TOOLS`/`TOOL_DESCRIPTIONS` 패턴에 편입합니다.

⚠️ **알려진 갭**: 현재 `plan.py`의 `create_plan()`은 도구 **이름**만 뽑지 파라미터는 안 뽑습니다
(`steps: list[str]`). 생산지시 변경처럼 구체적인 값(wo_no, 새 날짜)이 필요한 쓰기 도구는 이대로
안 됩니다. **F단계(마지막, "있으면 좋은 정도")에서 `PLAN_TOOL` 스키마를 확장**해서, 마지막 스텝이
쓰기 도구일 때 `parameters` 객체도 같이 뽑도록 `plan.py`를 소폭 확장해야 합니다 — 이건 지금
결정하지 않고 F단계 착수 시점에 다시 설계합니다.

**경량 승인 게이트** (`app/services/agent/approval.py`, 사용자 결정: 경량 버전):

```python
WRITE_TOOL_NAMES = {"erp_update_production_order"}


def requires_manual_approval(tool_name: str) -> bool:
    return tool_name in WRITE_TOOL_NAMES
```

**단일 게이트 함수로 몰아둔 이유**: 나중에 이게 부족해지면(도구가 많아지고 위험도가 갈리기
시작하면) `requires_manual_approval()` 내부만 `RiskLevel` enum 비교로 바꾸면 되고, 호출부
(`execute.py`의 실행 로직)는 손댈 필요가 없습니다. 지금은 diff만 반환하고 별도
`POST /erp/production-orders/{wo_no}/approve` 호출 전까진 DB에 반영 안 되는 흐름으로 충분합니다.

```python
def build_diff(before: BaseModel, after: BaseModel) -> list[dict]:
    b, a = before.model_dump(), after.model_dump()
    return [{"field": k, "before": b[k], "after": a[k]} for k in a if b.get(k) != a[k]]
```

---

# 6. 교차 검증 로직

## 6.1 파이프라인 (QA 답변 생성 이후 후처리, `run_cross_check()`)

```
기존 QA 결과 (AnswerOut)
   ↓
[1] claim_extractor  — 답변에서 수치 주장 추출 (정규식)
[2] erp_resolver     — (part_no, metric) 배치로 모아 repository.query_facts() 1회 호출
[3] cross_validator  — 대조 + 판정
[4] 결과 반영        — qa_logs/cross_checks 저장, mismatch면 답변에 정정 문단 추가
```

**프롬프트에 ERP 값을 미리 넣지 않습니다.** 넣어도 LLM이 문서 값과 섞어 씁니다. 결정적 검증은
코드로 합니다.

## 6.2 주장 추출 — 1단계는 정규식만

```python
PATTERNS = [
    (r"안전\s?재고[는은]?\s*([\d,]+)\s*(EA|개)?", MetricKey.SAFETY_STOCK),
    (r"(?:가용|현)\s?재고[는은]?\s*([\d,]+)\s*(EA|개)?", MetricKey.AVAILABLE_STOCK),
    (r"커버리지[는은]?\s*([\d.]+)\s*주", MetricKey.COVERAGE_WEEKS),
    (r"주간\s?소요(?:량)?[는은]?\s*([\d,]+)", MetricKey.WEEKLY_DEMAND),
]
PART_RE = re.compile(r"\b([A-Z]{2,3}-\d{4}(?:-[A-Z])?)\b")
```

품번을 못 찾은 수치는 **버립니다.**

`claimed_as_of`는 인용 chunk가 속한 문서의 **`Document.uploaded_at`**에서 가져옵니다
(⚠️ AI Office OS의 `Document` 모델은 `created_at`이 아니라 `uploaded_at` — 이름이 다릅니다,
`app/models/document.py:15` 확인 필요).

## 6.3 판정 규칙

```python
def judge(claim, fact) -> str:
    if fact is None or fact.value is None:
        return "not_applicable"

    tol = TOLERANCE.get(claim.metric, TOLERANCE["__default__"])
    if within(claim.value, fact.value, tol):
        return "match"

    if claim.as_of and fact.as_of and claim.as_of < fact.as_of:
        return "stale_document"
    return "conflict"
```

`stale_document`(문서 갱신 필요)와 `conflict`(원인 불명, 사람 확인 필요)를 분리하는 게 핵심.

## 6.4 답변 반영 (trust 개념 없이 텍스트로만)

```python
if any(c["verdict"] == "stale_document" for c in checks):
    result.answer += render_note(checks)  # 템플릿. LLM 재생성 금지
```

정정 문단 템플릿:
```
문서 기준 {claimed}{unit}이지만, ERP 최신값({erp_as_of:%m-%d %H:%M})은 {erp}{unit}입니다.
```

원본의 "trust.verdict를 grounded→partial로 강등"은 AI Office OS의 QA에 애초에 trust 필드가
없어서 **적용하지 않습니다** — 텍스트 정정만으로 가치를 전달합니다.

---

# 7. API — 신규 라우터만, 기존 응답은 옵셔널 추가

## 7.1 신규 엔드포인트 (`backend/app/api/erp.py`, `ERP_ENABLED=true`일 때만 등록)

경로에 `/api/v1` 접두사를 붙이지 않습니다 — AI Office OS의 기존 라우트(`/documents`, `/qa/ask`,
`/admin/*`)가 전부 버전 프리픽스 없이 평평한 구조라서 통일합니다.

```
GET  /erp/materials                    # coverage_weeks, status 포함
GET  /erp/materials/{part_no}
GET  /erp/bom/{part_no}
GET  /erp/schedule
POST /erp/sync                         # require_admin
GET  /admin/stats/erp-cross-checks     # Phase 9 관리자 대시보드 패턴 재사용 (아래 7.3)
```

`status` 임계값: coverage < 1.5 → `critical`, < 2.5 → `warning`.

## 7.2 기존 QA 응답 — 옵셔널 필드만 추가

`backend/app/schemas/qa.py`:
```python
class CrossCheckOut(BaseModel):
    metric_key: str
    entity_key: str
    verdict: str
    claimed_value: float | None
    erp_value: float | None


class AnswerOut(BaseModel):
    answer: str
    sources: list[SourceOut]
    cross_checks: list[CrossCheckOut] | None = None   # ← 추가. 기본 None
```

`None`이 기본이므로 **기존 클라이언트가 안 깨집니다.** 플래그가 꺼져 있으면 이 필드가 항상 `None`.

## 7.3 관리자 대시보드 통계 — Phase 9 패턴 재사용 (신규 가치 지점)

원본 문서엔 없던 항목이지만, `qa_logs`/`cross_checks`를 영구 저장하기로 한 이상 Phase 9의
`app/api/admin.py`에 있는 `AI_ENDPOINT_PATTERNS`/`_scoped_document_query` 같은 **org 스코프
집계 패턴**을 그대로 재사용해서 "이번 달 몇 건의 낡은 문서를 잡아냈는지" 보여줄 수 있습니다:

```python
@router.get("/stats/erp-cross-checks")
def erp_cross_check_stats(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    query = (
        db.query(CrossCheck.verdict, func.count(CrossCheck.id))
        .join(QaLog, CrossCheck.qa_log_id == QaLog.id)
    )
    if current_user.role != "superadmin":
        query = query.filter(QaLog.organization_id == current_user.organization_id)
    counts = query.group_by(CrossCheck.verdict).all()
    return {verdict: count for verdict, count in counts}
```

이게 Phase 9와 이 애드온을 잇는 지점이자, 포트폴리오 스토리로도 자연스럽습니다 — "관리자가
문서-ERP 불일치를 대시보드에서 추적한다."

---

# 8. 목업 데이터 설계

`backend/scripts/seed_erp.py`. **의도적으로 어긋나게** 만듭니다(안 그러면 항상 `match`라 데모가
안 됨). 실행 전 `organizations` 테이블에 대상 조직이 있어야 합니다(Phase 9의
`POST /admin/organizations`로 미리 만들어둘 것).

| 품번 | 설계 의도 |
|---|---|
| PN-4471-A | 08-03 재고 320 → 08-07 재고 285. **메인 데모 (stale_document)** |
| PN-3310-C | 커버리지 1.8주. 경고 임계 근접 |
| PN-4472-B | 문서와 ERP 전부 일치. `match` 정상 케이스 |
| PN-5502-A | ERP에만 존재, 문서 언급 없음. `not_applicable` |
| RM-0091 | PN-4471-A 하위 자재. BOM 전개용 |

- 재고 스냅샷 90일치, 하루 1건 — `as_of`가 실제로 움직여야 함
- BOM: 여러 조립품이 PN-4471-A를 공통 사용, `alt_part_no`는 NULL
- 인바운드: `original_eta`≠`current_eta`, `status=delayed`인 건 최소 1개
- **멱등성 필수** — 여러 번 실행해도 중복 없게 upsert (기존 프로젝트에 pandas 의존성 없음 —
  추가하지 말고 표준 라이브러리 + SQLAlchemy만 사용)

---

# 9. 테스트 (pytest, 동기 TestClient — 기존 스타일과 동일)

⚠️ AI Office OS의 기존 테스트(`backend/tests/`)는 전부 **동기** `TestClient` 기반입니다
(`async def` 아님, `await` 없음). 원본 문서의 `async def test_...` 스타일을 그대로 쓰면 기존
컨벤션과 어긋나니, 아래처럼 맞춥니다.

```python
# tests/test_cross_validation.py
import uuid


def test_flag_off_keeps_legacy_behavior(client, monkeypatch):
    """플래그를 끄면 기존과 완전히 동일하게 동작한다."""
    monkeypatch.setenv("ERP_CROSS_CHECK_ENABLED", "false")
    token = _signup_and_login(client)
    response = client.post(
        "/qa/ask", json={"question": "아무 질문"}, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.json()["cross_checks"] is None


def test_erp_failure_does_not_break_qa(client, monkeypatch):
    """ERP 조회가 죽어도 QA 답변은 나온다."""
    monkeypatch.setenv("ERP_CROSS_CHECK_ENABLED", "true")
    # repository.query_facts를 예외 던지도록 monkeypatch
    ...
    response = client.post("/qa/ask", json={"question": "..."}, headers=...)
    assert response.status_code == 200
    assert response.json()["answer"]  # 답은 나옴


def test_erp_query_rejects_injected_part_no():
    from app.services.erp.repository import PART_NO_PATTERN
    assert not PART_NO_PATTERN.match("PN-4471-A'; DROP TABLE--")


def test_erp_query_is_org_scoped(db_session):
    from app.services.erp.repository import query_facts
    facts = query_facts(db_session, organization_id=999, part_nos=["PN-4471-A"], metrics=[...])
    assert facts == []
```

`test_flag_off_keeps_legacy_behavior`와 `test_erp_failure_does_not_break_qa`가 이 애드온의
안전장치입니다. **먼저 작성하세요** — 나머지 구현은 이 두 테스트를 절대 깨지 않는 선에서 진행.

기존 10개 스모크테스트(`test_health.py`/`test_auth.py`/`test_documents.py`/`test_admin.py`)는
이 애드온 작업 내내 **전부 통과 상태를 유지**해야 합니다 (`pytest -v`로 매 단계 확인).

---

# 10. 작업 순서 (기존 일정에 끼워넣기)

기존 Phase 번호(0~10)를 바꾸지 않습니다. **A~F 단계**로 별도 트랙을 씁니다.

| 단계 | 작업 | 시작 조건 |
|---|---|---|
| **A** | 기능 플래그(`erp_config.py`) + `.env` 3줄 | 언제든 |
| **B** | 테이블 8개(`qa_logs`/`cross_checks` 포함) + 마이그레이션 3개 + seed | A 완료 |
| **C** | `app/services/erp/` (metrics/repository/service) | B 완료 |
| **D** | `app/api/erp.py` 5개 엔드포인트 + `/admin/stats/erp-cross-checks` | C 완료 |
| **E** | `app/services/trust/` 3개 + `qa.py` 훅 3줄 | C 완료, **기존 QA가 안정화된 뒤** |
| **F** | `erp_update_production_order` + 경량 승인 + (필요 시 `plan.py` 파라미터 추출 확장) | E 완료 + Phase 7 Agent 이해 필요 |

**E는 기존 QA 파이프라인이 흔들리지 않는 상태에서 하세요.** A~D까지만 해도 "ERP 연동했다"는 말은
성립합니다. E가 차별화 지점, F는 있으면 좋은 정도(파라미터 추출 확장이라는 선행 작업이 있어서
난이도가 가장 높음).

---

# 11. 롤백 절차

```bash
# 1단계: 플래그만 끄기 (즉시, 코드 변경 없음)
# .env에서
ERP_CROSS_CHECK_ENABLED=false
ERP_ENABLED=false

# 2단계: 마이그레이션 되돌리기 (필요 시)
alembic downgrade -3

# 3단계: 브랜치 되돌리기
git revert <merge-commit>
```

1단계만으로 기존 동작이 완전히 복구됩니다. 신규 테이블이 남아 있어도 아무 영향 없습니다.

---

# 12. README에 붙일 문단 (나중에, E 단계 끝난 뒤 별도 커밋으로)

**지금은 README를 건드리지 마세요.**

```markdown
### 문서 ↔ ERP 교차 검증

RAG의 구조적 한계는 문서가 작성 시점에 박제된다는 점입니다. 회의록에 "안전재고 320 EA"라고
적혀 있으면, 3일 뒤 실제 재고가 285 EA가 되어도 RAG는 320이라고 답합니다. 인용도 정확하고
근거율도 높은데, 틀렸습니다.

이 프로젝트는 QA 답변의 수치 주장을 ERP 마스터와 자동 대조하고, 관리자 대시보드
(`/admin/stats/erp-cross-checks`)에서 대조 이력을 조직 단위로 추적합니다.

| 판정 | 의미 |
|---|---|
| `match` | 허용 오차 내 일치 |
| `stale_document` | 문서가 ERP보다 오래됐고 값이 다름 → 답변에 정정 삽입 |
| `conflict` | 값이 다른데 시점으로 설명 안 됨 → 사람 확인 필요 |
| `not_applicable` | ERP에 대조 대상 없음 → 감점 없음 |
```

---

# 13. 단계별 실행 프롬프트 (MINT/Cursor 등 어느 도구에 붙여도 되게)

## A. 기능 플래그

```
ERP 애드온을 붙이기 전에 안전장치부터 만든다.

backend/app/core/erp_config.py 를 신규 생성 (docs/addons/erp-module.md 2.1절 그대로).
backend/.env 에 ERP_ENABLED=false, ERP_CROSS_CHECK_ENABLED=false, ERP_QUERY_TIMEOUT_MS=1500 추가.

기존 파일은 절대 수정하지 마.
```

## B. 테이블 + 시더

```
docs/addons/erp-module.md 의 3절, 8절을 참조해서
backend/app/models/ 아래 신규 모델 8개(erp_material, erp_stock_snapshot, erp_bom,
erp_inbound_schedule, erp_production_plan, erp_shipment_plan, qa_log, cross_check)를 작성해줘.

제약:
- 기존 테이블은 ALTER 하지 않는다. 신규 테이블만 만든다.
- app/core/database.py 의 Base 를 그대로 재사용, 기존 모델(document.py 등)과 동일한 스타일
  (Column/Integer/ForeignKey, class 당 파일 1개)
- ERP 데이터 테이블은 organization_id 전부 nullable=False. qa_logs 만 User.organization_id와
  동일하게 nullable=True
- erp_stock_snapshots 에 (organization_id, part_no, as_of) 복합 인덱스
- erp_boms 에 (organization_id, child_part_no) 인덱스
- alembic/env.py 에 8개 import 추가 잊지 말 것

alembic revision 3개로 나눠 생성 (master / transaction / qa_log+cross_checks).
그다음 backend/scripts/seed_erp.py 를 8절 표대로 작성. 멱등성 필수, pandas 금지.

완료하면 실행 명령만 알려주고 멈춰.
```

**확인**: `alembic upgrade head` → `downgrade -3` → `upgrade head` 왕복 성공, 기존 `pytest -v`
10개 그대로 통과.

## C. Repository + 서비스

```
docs/addons/erp-module.md 4절, 5.1절 기준으로
backend/app/services/erp/{metrics,repository,service}.py 를 작성해줘.

- metrics.py: MetricKey StrEnum 전체 정의. 실제 구현은 앞의 4개만, 나머지는 not_applicable.
- repository.py: 모든 함수 첫 인자가 organization_id, 기본값 금지.
  최신 스냅샷 조회는 DISTINCT ON 한 방 쿼리로 (N+1 금지).
  part_no 는 정규식(PART_NO_PATTERN) 검증 통과 후에만 쿼리에 전달.
- service.py: coverage_weeks 계산. weekly_demand 가 0이면 None (0으로 나누지 말 것).

테스트 4개도 함께 (9절 참조): org 격리 / 인젝션 거부 / 최신 스냅샷 / 0 나누기.
기존 pytest 10개가 여전히 통과하는지 마지막에 확인.
```

## D. 라우터

```
backend/app/api/erp.py 를 7.1절 엔드포인트로 작성하고
backend/app/main.py 에 조건부 등록만 추가해줘 (2.2절 형태 그대로, 다른 줄은 건드리지 마).

- 기존 pagination 없음, 에러 포맷은 기존 admin.py/documents.py와 동일한 HTTPException 패턴
- get_current_user / require_admin 의존성 그대로 재사용
- /erp/materials 응답에 coverage_weeks 와 status 포함 (임계: 1.5 / 2.5)
- /admin/stats/erp-cross-checks 도 7.3절 그대로 추가 (require_admin, org 스코프)
```

## E. 교차 검증 (기존 QA가 안정된 뒤)

```
docs/addons/erp-module.md 6절 기준으로
backend/app/services/trust/{claim_extractor,erp_resolver,cross_validator}.py 를 작성해줘.

claim_extractor:
- LLM 안 씀. 6.2절 정규식만.
- 품번을 못 찾은 수치는 버린다.
- claimed_as_of 는 인용 chunk가 속한 Document.uploaded_at 에서 가져온다 (created_at 아님).

erp_resolver:
- (part_no, metric) 조합을 모아서 repository.query_facts 를 1회만 호출.

cross_validator:
- run_cross_check(db, user, question, result) 함수 하나로 노출.
  claim_extractor → erp_resolver → judge() → qa_logs/cross_checks 저장 → answer에 정정 문단.

그다음 backend/app/api/qa.py 에 2.3절 형태로 3줄만 추가해줘.
기존 코드는 절대 고치지 말고, result 변수에 담은 뒤 조건부로 run_cross_check 호출하고 반환.
try/except 로 감싸서 실패해도 원래 답변을 반환할 것.

backend/app/schemas/qa.py 에 CrossCheckOut 추가하고 AnswerOut에 cross_checks: list[...] | None = None.

테스트는 9절 전부. test_flag_off_keeps_legacy_behavior 와 test_erp_failure_does_not_break_qa
를 먼저 작성. 기존 pytest 10개 통과 유지 확인.
```

**확인**: 플래그를 끄면 기존 테스트가 전부 그대로 통과하는지.

## F. ERP_WRITE + 승인 (경량 버전)

```
먼저 backend/app/services/agent/plan.py 의 PLAN_TOOL 스키마를 확장해서, 마지막 스텝이 쓰기
도구일 때 parameters 객체도 함께 추출하도록 만들어줘 (이게 선행 조건).

그다음 backend/app/services/agent/approval.py 를 5.2절 그대로 작성 (경량 승인 게이트,
단일 함수 requires_manual_approval).

backend/app/services/agent/tools.py 의 TOOLS 딕셔너리에 erp_update_production_order 를
추가하되, 기존 3개 도구(search_document/summarize_document/draft_email) 코드는 손대지 마.

diff 는 5.2절 build_diff() 로 스키마에서 자동 생성. 도구별 하드코딩 금지.

테스트:
- test_erp_write_requires_approval (승인 전 DB 값이 안 바뀜)
- test_diff_is_generated_from_schema
```
