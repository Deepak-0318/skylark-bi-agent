from .schemas import QueryPlan


def validate_plan(plan: QueryPlan) -> QueryPlan:
    if not plan.original_query.strip():
        plan.clarification_required = True
        plan.clarification_question = "What business question would you like me to answer?"

    return plan