from .selectors import get_funnel_stats, get_source_stats, get_time_in_stage


def build_dashboard_metrics(owner):
    return {
        "funnel": get_funnel_stats(owner),
        "time_in_stage": get_time_in_stage(owner),
        "source_stats": get_source_stats(owner),
    }
