from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.cross_check import CrossCheck
from app.models.document import Document
from app.models.qa_log import QaLog
from app.models.user import User
from app.schemas.qa import AnswerOut, CrossCheckOut
from app.services.erp.metrics import TOLERANCE
from app.services.trust.claim_extractor import extract_claims
from app.services.trust.erp_resolver import resolve_facts


def _find_claim_source(db: Session, part_no: str, sources) -> tuple:
    for source in sources:
        if part_no in source.chunk_text:
            document = db.query(Document).filter(Document.id == source.document_id).first()
            if document is not None:
                return document.uploaded_at, f"{source.filename} (#{source.document_id})"
    return None, None


def _judge(claim_value: Decimal, fact_value, metric, claimed_as_of, fact_as_of) -> str:
    if fact_value is None:
        return "not_applicable"

    tolerance = TOLERANCE.get(metric, TOLERANCE["__default__"])
    if fact_value == 0:
        is_within_tolerance = claim_value == 0
    else:
        is_within_tolerance = abs(claim_value - fact_value) / abs(fact_value) <= Decimal(str(tolerance))

    if is_within_tolerance:
        return "match"
    if claimed_as_of and fact_as_of and claimed_as_of < fact_as_of:
        return "stale_document"
    return "conflict"


def run_cross_check(db: Session, user: User, question: str, result: AnswerOut) -> AnswerOut:
    claims = extract_claims(result.answer)

    qa_log = QaLog(
        user_id=user.id, organization_id=user.organization_id,
        question=question, answer=result.answer,
    )
    db.add(qa_log)
    db.flush()

    if not claims or user.organization_id is None:
        db.commit()
        return AnswerOut(answer=result.answer, sources=result.sources, cross_checks=[])

    facts_by_key = resolve_facts(db, user.organization_id, claims)

    cross_check_outs: list[CrossCheckOut] = []
    stale_notes: list[str] = []

    for claim in claims:
        fact = facts_by_key.get((claim.part_no, claim.metric))
        fact_value = fact.value if fact else None
        fact_as_of = fact.as_of if fact else None
        claimed_as_of, claimed_source = _find_claim_source(db, claim.part_no, result.sources)

        verdict = _judge(claim.value, fact_value, claim.metric, claimed_as_of, fact_as_of)
        delta = (claim.value - fact_value) if fact_value is not None else None
        tolerance = Decimal(str(TOLERANCE.get(claim.metric, TOLERANCE["__default__"])))

        db.add(CrossCheck(
            qa_log_id=qa_log.id, metric_key=claim.metric.value, entity_key=claim.part_no,
            claimed_value=claim.value, claimed_source=claimed_source, claimed_as_of=claimed_as_of,
            erp_value=fact_value, erp_as_of=fact_as_of,
            verdict=verdict, delta=delta, tolerance=tolerance,
        ))

        cross_check_outs.append(CrossCheckOut(
            metric_key=claim.metric.value, entity_key=claim.part_no, verdict=verdict,
            claimed_value=float(claim.value),
            erp_value=float(fact_value) if fact_value is not None else None,
        ))

        if verdict == "stale_document" and fact_value is not None and fact_as_of is not None:
            stale_notes.append(
                f"\n\n> ⚠️ 문서 기준 {claim.part_no} {claim.metric.value}은 {claim.value}이지만, "
                f"ERP 최신값({fact_as_of:%m-%d %H:%M})은 {fact_value}입니다."
            )

    db.commit()

    return AnswerOut(
        answer=result.answer + "".join(stale_notes),
        sources=result.sources,
        cross_checks=cross_check_outs,
    )
