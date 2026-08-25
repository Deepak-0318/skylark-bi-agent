from .schemas import QueryPlan


def needs_clarification(plan: QueryPlan) -> bool:
    return plan.clarification_required or plan.confidence < 0.5