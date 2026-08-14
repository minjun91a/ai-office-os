from sqlalchemy.orm import Session

from app.services.erp.repository import query_facts
from app.services.trust.claim_extractor import Claim


def resolve_facts(db: Session, organization_id: int, claims: list[Claim]) -> dict:
    if not claims:
        return {}

    part_nos = list({c.part_no for c in claims})
    metrics = list({c.metric for c in claims})
    facts = query_facts(db, organization_id, part_nos, metrics)
    return {(fact.part_no, fact.metric): fact for fact in facts}
