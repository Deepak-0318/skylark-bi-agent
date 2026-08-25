from .schemas import FinalAnswer
from .response import (
    GroqResponseClient,
    format_answer,
)

from skylark_bi.agents.query_agent import QueryUnderstandingService
from skylark_bi.agents.bi_agent import BIAgentService
from skylark_bi.agents.monday_agent import MondayIntegrationService


class OrchestratorService:

    def __init__(
        self,
        query_service=None,
        bi_service=None,
        monday_service=None,
        resilience_service=None,
        response_client=None,
    ):
        self.query_service = (
            query_service or QueryUnderstandingService()
        )

        self.bi_service = (
            bi_service or BIAgentService()
        )

        self.monday_service = (
            monday_service or MondayIntegrationService()
        )

        self.resilience_service = resilience_service

        if response_client is not None:
            self.response_client = response_client
        else:
            try:
                self.response_client = (
                    GroqResponseClient.from_environment()
                )
            except Exception:
                self.response_client = None

    def answer(self, query: str) -> FinalAnswer:

        plan = self.query_service.understand(query)

        if plan.clarification_required:
            return FinalAnswer(
                answer=(
                    plan.clarification_question
                    or "Could you clarify your question?"
                ),
                clarification_required=True,
                clarification_question=(
                    plan.clarification_question
                ),
            )

        try:
            deals, work_orders = self._load_data()

            if self.resilience_service:
                deals = self._resilient_deals(deals)
                work_orders = self._resilient_work_orders(
                    work_orders
                )

            result = self.bi_service.analyze(
                plan,
                deals=deals,
                work_orders=work_orders,
            )

            answer = format_answer(
                plan,
                result,
                llm_client=self.response_client,
            )

            return FinalAnswer(
                answer=answer,
                headline_metrics=result.metrics,
                insights=result.insights,
                risks=result.risks,
                caveats=result.caveats,
                data_quality=result.data_quality,
            )

        except Exception as exc:
            return FinalAnswer(
                answer=(
                    "I couldn't retrieve the business data right now. "
                    "Please try again."
                ),
                caveats=[
                    "The data source could not be queried successfully."
                ],
            )

    def _load_data(self):
        """
        Load canonical business records from Monday.com.

        Mapping happens inside MondayIntegrationService.
        """

        deals = self.monday_service.read_deals()

        work_orders = (
            self.monday_service.read_work_orders()
        )

        return deals, work_orders

    def _resilient_deals(self, records):

        if hasattr(
            self.resilience_service,
            "process_deals",
        ):
            return self.resilience_service.process_deals(
                records
            )

        return records

    def _resilient_work_orders(self, records):

        if hasattr(
            self.resilience_service,
            "process_work_orders",
        ):
            return self.resilience_service.process_work_orders(
                records
            )

        return records