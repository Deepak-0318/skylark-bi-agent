from .planner import build_plan
from .validation import validate_plan


class QueryUnderstandingService:

    def understand(self, query: str):
        plan = build_plan(query)
        return validate_plan(plan)