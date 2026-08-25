from .schemas import BIResult
from .filters import apply_filters
from .metrics import count, total, percentage
from .aggregations import grouped_total
from .insights import generate_sector_insights, generate_pipeline_insights
from .leadership import leadership_summary


class BIAgentService:

    def analyze(self, plan, deals=None, work_orders=None):
        deals = list(deals or [])
        work_orders = list(work_orders or [])

        if plan.datasets == ["deals"]:
            records = deals
        elif plan.datasets == ["work_orders"]:
            records = work_orders
        else:
            records = deals + work_orders

        if plan.filters:
            if plan.datasets == ["deals"]:
                deals = apply_filters(deals, plan.filters)
            elif plan.datasets == ["work_orders"]:
                work_orders = apply_filters(work_orders, plan.filters)

            records = (
                deals
                if plan.datasets == ["deals"]
                else work_orders
                if plan.datasets == ["work_orders"]
                else deals + work_orders
            )

        metrics = {}
        insights = []
        risks = []
        caveats = []

        if plan.intent in {
            "pipeline_health",
            "pipeline_value",
            "sector_performance",
            "deal_analysis",
            "cross_board_analysis",
            "leadership_update",
        }:
            metrics["deal_count"] = len(deals)
            metrics["pipeline_value"] = self._total(
                deals, "deal_value"
            )
            metrics["weighted_pipeline"] = self._weighted_pipeline(deals)

        if plan.intent in {
            "revenue",
            "billing",
            "collections",
            "accounts_receivable",
            "sector_performance",
            "cross_board_analysis",
            "leadership_update",
        }:
            metrics["work_order_count"] = len(work_orders)
            metrics["billed_value"] = self._total(
                work_orders, "billed_value"
            )
            metrics["collected_value"] = self._total(
                work_orders, "collected_value"
            )
            metrics["amount_to_be_billed"] = self._total(
                work_orders, "amount_to_be_billed"
            )
            metrics["amount_receivable"] = self._total(
                work_orders, "amount_receivable"
            )

        grouped = []

        if "sector" in plan.group_by:
            grouped = grouped_total(
                deals,
                "sector",
                "deal_value",
            )

            if not grouped:
                grouped = grouped_total(
                    work_orders,
                    "sector",
                    "billed_value",
                )

            insights.extend(generate_sector_insights(grouped))

        insights.extend(generate_pipeline_insights(metrics))

        receivable = metrics.get("amount_receivable")

        if isinstance(receivable, (int, float)) and receivable > 0:
            risks.append("Outstanding receivables require attention.")

        if not records:
            caveats.append("No records matched the requested filters.")

        return BIResult(
            intent=plan.intent,
            metrics=metrics,
            grouped=grouped,
            insights=insights,
            risks=risks,
            caveats=caveats,
            data_quality={
                "deal_records": len(deals),
                "work_order_records": len(work_orders),
            },
        )

    @staticmethod
    def _total(records, field):
        values = []

        for record in records:
            value = (
                record.get(field)
                if isinstance(record, dict)
                else getattr(record, field, None)
            )

            if isinstance(value, (int, float)):
                values.append(float(value))

        return sum(values) if values else None

    @staticmethod
    def _weighted_pipeline(records):
        total = 0.0
        usable = False

        probability_map = {
            "high": 0.8,
            "medium": 0.5,
            "low": 0.2,
        }

        for record in records:
            def get(field):
                return (
                    record.get(field)
                    if isinstance(record, dict)
                    else getattr(record, field, None)
                )

            value = get("deal_value")
            probability = get("closure_probability")

            if not isinstance(value, (int, float)):
                continue

            if isinstance(probability, str):
                probability = probability_map.get(
                    probability.strip().lower()
                )

            if isinstance(probability, (int, float)):
                total += float(value) * float(probability)
                usable = True

        return total if usable else None