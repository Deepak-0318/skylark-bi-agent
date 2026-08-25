from __future__ import annotations

import os
import sys

import streamlit as st


# ------------------------------------------------------------------
# Project path
# ------------------------------------------------------------------

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")

if SRC not in sys.path:
    sys.path.insert(0, SRC)


# ------------------------------------------------------------------
# Page configuration
# ------------------------------------------------------------------

st.set_page_config(
    page_title="Skylark BI Agent",
    page_icon="🚁",
    layout="wide",
)


# ------------------------------------------------------------------
# Streamlit Secrets → Environment Variables
# ------------------------------------------------------------------

if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

if "GROQ_MODEL" in st.secrets:
    os.environ["GROQ_MODEL"] = st.secrets["GROQ_MODEL"]


# ------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------

from skylark_bi.agents.monday_agent import MondayIntegrationService
from skylark_bi.agents.query_agent import QueryUnderstandingService
from skylark_bi.agents.bi_agent import BIAgentService

from skylark_bi.agents.monday_agent.mapper import (
    map_deal,
    map_work_order,
)


# ------------------------------------------------------------------
# Header
# ------------------------------------------------------------------

st.title("🚁 Skylark BI Agent")

st.caption(
    "Founder-level business intelligence powered by monday.com"
)

st.divider()


# ------------------------------------------------------------------
# Services
# ------------------------------------------------------------------

@st.cache_resource
def get_services():

    monday = MondayIntegrationService()

    query = QueryUnderstandingService()

    bi = BIAgentService()

    return monday, query, bi


try:

    monday, query_service, bi_service = get_services()

except Exception as exc:

    st.error(
        f"Unable to connect to monday.com: {exc}"
    )

    st.stop()


# ------------------------------------------------------------------
# Data loading
# ------------------------------------------------------------------

@st.cache_data(ttl=300)
def load_data():

    deals_board = monday.reader.read_board(
        monday.config.deals_board_id
    )

    work_orders_board = monday.reader.read_board(
        monday.config.work_orders_board_id
    )

    deals = [
        map_deal(
            item,
            deals_board.board,
        )
        for item in deals_board.items
    ]

    work_orders = [
        map_work_order(
            item,
            work_orders_board.board,
        )
        for item in work_orders_board.items
    ]

    return deals, work_orders


try:

    deals, work_orders = load_data()

except Exception as exc:

    st.error(
        f"Unable to load monday.com data: {exc}"
    )

    st.stop()


# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------

with st.sidebar:

    st.header("Data Sources")

    st.success("Monday.com connected")

    st.metric(
        "Deals",
        len(deals),
    )

    st.metric(
        "Work Orders",
        len(work_orders),
    )

    if st.button("Refresh Data"):

        load_data.clear()

        st.rerun()


# ------------------------------------------------------------------
# Query section
# ------------------------------------------------------------------

st.subheader("Ask a business question")


examples = [
    "How is our pipeline looking?",
    "How is the mining sector pipeline?",
    "What is our outstanding receivable?",
    "Compare our sales pipeline with work order execution.",
    "Where should leadership focus?",
    "Give me a leadership update.",
]


selected = st.selectbox(
    "Example questions",
    ["Custom question"] + examples,
)


if selected == "Custom question":

    question = st.text_input(
        "Business question",
        placeholder=(
            "Ask about pipeline, revenue, sectors, "
            "receivables, work orders, or leadership..."
        ),
    )

else:

    question = selected


# ------------------------------------------------------------------
# Analysis
# ------------------------------------------------------------------

if st.button(
    "Analyze",
    type="primary",
) and question.strip():

    with st.spinner(
        "Analyzing monday.com data..."
    ):

        try:

            # ------------------------------------------------------
            # 1. Understand query using Groq
            # ------------------------------------------------------

            plan = query_service.understand(
                question
            )

            # ------------------------------------------------------
            # 2. Handle clarification
            # ------------------------------------------------------

            if plan.clarification_required:

                st.warning(
                    plan.clarification_question
                    or "Could you clarify your question?"
                )

                st.stop()

            # ------------------------------------------------------
            # 3. Deterministic BI analysis
            # ------------------------------------------------------

            result = bi_service.analyze(
                plan,
                deals=deals,
                work_orders=work_orders,
            )

        except Exception as exc:

            st.error(
                f"Unable to analyze the question: {exc}"
            )

            st.stop()


    # --------------------------------------------------------------
    # Business Answer
    # --------------------------------------------------------------

    st.divider()

    st.subheader("Business Answer")


    # --------------------------------------------------------------
    # Headline metrics
    # --------------------------------------------------------------

    if result.metrics:

        metric_items = [
            (key, value)
            for key, value in result.metrics.items()
            if value is not None
        ]

        if metric_items:

            columns = st.columns(
                min(len(metric_items), 4)
            )

            for column, (key, value) in zip(
                columns,
                metric_items,
            ):

                if isinstance(value, float):

                    if (
                        "value" in key
                        or "amount" in key
                        or "pipeline" in key
                    ):

                        display = (
                            f"₹{value:,.2f}"
                        )

                    else:

                        display = (
                            f"{value:,.2f}"
                        )

                elif value is None:

                    display = "N/A"

                else:

                    display = str(value)

                column.metric(
                    key.replace(
                        "_",
                        " ",
                    ).title(),
                    display,
                )


    # --------------------------------------------------------------
    # Insights
    # --------------------------------------------------------------

    if result.insights:

        st.subheader("Insights")

        for insight in result.insights:

            st.info(insight)


    # --------------------------------------------------------------
    # Risks
    # --------------------------------------------------------------

    if result.risks:

        st.subheader(
            "Risks / Attention"
        )

        for risk in result.risks:

            st.warning(risk)


    # --------------------------------------------------------------
    # Caveats
    # --------------------------------------------------------------

    if result.caveats:

        st.subheader(
            "Data Quality / Caveats"
        )

        for caveat in result.caveats:

            st.caption(
                f"⚠️ {caveat}"
            )


    # --------------------------------------------------------------
    # Query interpretation
    # --------------------------------------------------------------

    with st.expander(
        "Query interpretation"
    ):

        st.write(
            {
                "Intent": plan.intent,
                "Datasets": plan.datasets,
                "Filters": plan.filters,
                "Metrics": plan.metrics,
                "Group By": plan.group_by,
                "Confidence": plan.confidence,
            }
        )


else:

    st.info(
        "Ask a founder-level business question to begin."
    )