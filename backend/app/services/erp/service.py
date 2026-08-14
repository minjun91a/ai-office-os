from decimal import Decimal


def coverage_weeks(available_qty: Decimal | None, weekly_demand: Decimal | None) -> Decimal | None:
    if available_qty is None or weekly_demand is None or weekly_demand == 0:
        return None
    return available_qty / weekly_demand
