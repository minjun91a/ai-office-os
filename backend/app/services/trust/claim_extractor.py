import re
from decimal import Decimal, InvalidOperation

from pydantic import BaseModel

from app.services.erp.metrics import MetricKey

PATTERNS = [
    (re.compile(r"안전\s?재고[는은]?\s*([\d,]+)\s*(?:EA|개)?"), MetricKey.SAFETY_STOCK),
    (re.compile(r"(?:가용|현)\s?재고[는은]?\s*([\d,]+)\s*(?:EA|개)?"), MetricKey.AVAILABLE_STOCK),
    (re.compile(r"커버리지[는은]?\s*([\d.]+)\s*주"), MetricKey.COVERAGE_WEEKS),
    (re.compile(r"주간\s?소요(?:량)?[는은]?\s*([\d,]+)"), MetricKey.WEEKLY_DEMAND),
]
PART_NO_PATTERN = re.compile(r"\b([A-Z]{2,3}-\d{4}(?:-[A-Z])?)\b")


class Claim(BaseModel):
    part_no: str
    metric: MetricKey
    value: Decimal


def extract_claims(answer: str) -> list[Claim]:
    part_no_matches = list(PART_NO_PATTERN.finditer(answer))
    if not part_no_matches:
        return []

    claims: list[Claim] = []
    for pattern, metric in PATTERNS:
        for match in pattern.finditer(answer):
            raw_value = match.group(1).replace(",", "")
            try:
                value = Decimal(raw_value)
            except InvalidOperation:
                continue
            # 이 숫자와 가장 가까이 등장한 품번을 대상으로 삼음 (1단계는 LLM 없이 정규식만)
            nearest = min(part_no_matches, key=lambda m: abs(m.start() - match.start()))
            claims.append(Claim(part_no=nearest.group(1), metric=metric, value=value))
    return claims
