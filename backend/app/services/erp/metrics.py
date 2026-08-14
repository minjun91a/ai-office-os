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
