import os


def is_erp_enabled() -> bool:
    return os.getenv("ERP_ENABLED", "false").lower() == "true"


def is_cross_check_enabled() -> bool:
    return os.getenv("ERP_CROSS_CHECK_ENABLED", "false").lower() == "true"



ERP_QUERY_TIMEOUT_MS = int(os.getenv("ERP_QUERY_TIMEOUT_MS", "1500"))