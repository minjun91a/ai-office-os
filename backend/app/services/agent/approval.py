WRITE_ACTIONS = {"erp_update_production_order"}


def requires_manual_approval(action_name: str) -> bool:
    return action_name in WRITE_ACTIONS