import streamlit as st
import plotly.graph_objects as go

from ai.question_router import (
    route_question,
    get_visualization_type,
)

from ai.tools.database_tools import (
    get_sales_summary,
    get_monthly_revenue,
    get_top_products,
    get_country_revenue,
    get_customer_segments,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="RetailPulse-AI",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "executive_summary" not in st.session_state:
    st.session_state.executive_summary = None


# ============================================================
# CHART HELPERS
# ============================================================

def format_currency(value):
    """Format numeric value as GBP."""

    if value >= 1_000_000:
        return f"£{value / 1_000_000:.2f}M"

    if value >= 1_000:
        return f"£{value / 1_000:.0f}K"

    return f"£{value:,.2f}"


def chart_config():
    """Common Plotly configuration."""

    return {
        "displaylogo": False,
        "responsive": True,
    }


# ============================================================
# DATA LOADING
# ============================================================

def load_sales_summary():

    data = get_sales_summary()

    if not data:
        return None

    return data[0]


# ============================================================
# MONTHLY REVENUE CHART
# ============================================================

def show_monthly_revenue_chart():

    data = get_monthly_revenue()

    if not data:

        st.info(
            "No monthly revenue data available."
        )

        return

    months = []
    revenues = []
    orders = []

    for row in data:

        month_name = row.get("month_name")

        if not month_name:

            month_name = (
                f"{row['year']}-{int(row['month']):02d}"
            )

        months.append(
            f"{month_name[:3]} {row['year']}"
        )

        revenues.append(
            float(row["revenue"])
        )

        orders.append(
            int(row["total_orders"])
        )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=months,
            y=revenues,
            mode="lines+markers",
            name="Revenue",
            customdata=orders,
            line={
                "width": 3,
            },
            marker={
                "size": 8,
            },
            hovertemplate=(
                "<b>%{x}</b>"
                "<br>Revenue: £%{y:,.2f}"
                "<br>Orders: %{customdata:,}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title="Monthly Revenue Trend",
        xaxis_title="Month",
        yaxis_title="Revenue",
        hovermode="x unified",
        height=450,
        margin={
            "l": 20,
            "r": 30,
            "t": 70,
            "b": 60,
        },
        yaxis={
            "tickprefix": "£",
            "tickformat": ",.0f",
            "rangemode": "tozero",
        },
        xaxis={
            "type": "category",
        },
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config=chart_config(),
    )


# ============================================================
# TOP PRODUCTS CHART
# ============================================================

def show_top_products_chart():

    data = get_top_products(10)

    if not data:

        st.info(
            "No product data available."
        )

        return

    data = list(reversed(data))

    products = []
    revenues = []
    units = []

    for row in data:

        products.append(
            row.get(
                "description",
                "Unknown Product",
            )
        )

        revenues.append(
            float(row["revenue"])
        )

        units.append(
            int(
                row.get(
                    "units_sold",
                    0,
                )
            )
        )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=revenues,
            y=products,
            orientation="h",
            name="Revenue",
            customdata=units,
            text=[
                format_currency(value)
                for value in revenues
            ],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b>"
                "<br>Revenue: £%{x:,.2f}"
                "<br>Units sold: %{customdata:,}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title="Top 10 Products by Revenue",
        xaxis_title="Revenue",
        yaxis_title="",
        height=520,
        margin={
            "l": 20,
            "r": 120,
            "t": 70,
            "b": 60,
        },
        xaxis={
            "tickprefix": "£",
            "tickformat": ",.0f",
            "rangemode": "tozero",
        },
        yaxis={
            "automargin": True,
        },
        showlegend=False,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config=chart_config(),
    )


# ============================================================
# COUNTRY REVENUE CHART
# ============================================================

def show_country_revenue_chart():

    data = get_country_revenue(10)

    if not data:

        st.info(
            "No country data available."
        )

        return

    data = list(reversed(data))

    countries = []
    revenues = []
    orders = []

    for row in data:

        countries.append(
            row["country"]
        )

        revenues.append(
            float(row["revenue"])
        )

        orders.append(
            int(
                row.get(
                    "total_orders",
                    0,
                )
            )
        )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=revenues,
            y=countries,
            orientation="h",
            name="Revenue",
            customdata=orders,
            text=[
                format_currency(value)
                for value in revenues
            ],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b>"
                "<br>Revenue: £%{x:,.2f}"
                "<br>Orders: %{customdata:,}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title="Revenue by Country",
        xaxis_title="Revenue",
        yaxis_title="",
        height=500,
        margin={
            "l": 20,
            "r": 120,
            "t": 70,
            "b": 60,
        },
        xaxis={
            "tickprefix": "£",
            "tickformat": ",.0f",
            "rangemode": "tozero",
        },
        yaxis={
            "automargin": True,
        },
        showlegend=False,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config=chart_config(),
    )


# ============================================================
# CUSTOMER SEGMENTS CHART
# ============================================================

def show_customer_segments_chart():

    data = get_customer_segments()

    if not data:

        st.info(
            "No customer segment data available."
        )

        return

    data = sorted(
        data,
        key=lambda row: int(
            row["customer_count"]
        ),
    )

    segments = []
    customers = []
    revenues = []

    for row in data:

        segments.append(
            row["customer_segment"]
        )

        customers.append(
            int(row["customer_count"])
        )

        revenues.append(
            float(
                row.get(
                    "total_revenue",
                    0,
                )
            )
        )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=customers,
            y=segments,
            orientation="h",
            name="Customers",
            customdata=revenues,
            text=[
                f"{value:,}"
                for value in customers
            ],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b>"
                "<br>Customers: %{x:,}"
                "<br>Revenue: £%{customdata:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title="Customer Segments",
        xaxis_title="Customers",
        yaxis_title="",
        height=480,
        margin={
            "l": 30,
            "r": 110,
            "t": 70,
            "b": 60,
        },
        xaxis={
            "tickformat": ",.0f",
            "rangemode": "tozero",
        },
        yaxis={
            "automargin": True,
        },
        showlegend=False,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config=chart_config(),
    )


# ============================================================
# VISUALIZATION RENDERER
# ============================================================

def render_visualization(
    visualization_type
):

    if visualization_type == "monthly_revenue":

        st.markdown(
            "### 📈 Monthly Revenue"
        )

        show_monthly_revenue_chart()

        st.caption(
            "Source: PostgreSQL verified sales data"
        )

    elif visualization_type == "top_products":

        st.markdown(
            "### 🏆 Top Products by Revenue"
        )

        show_top_products_chart()

        st.caption(
            "Source: PostgreSQL verified product data"
        )

    elif visualization_type == "country_revenue":

        st.markdown(
            "### 🌍 Revenue by Country"
        )

        show_country_revenue_chart()

        st.caption(
            "Source: PostgreSQL verified country data"
        )

    elif visualization_type == "customer_segments":

        st.markdown(
            "### 👥 Customer Segments"
        )

        show_customer_segments_chart()

        st.caption(
            "Source: PostgreSQL verified RFM data"
        )


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }

    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.20);
        border-radius: 12px;
        padding: 18px;
    }

    div[data-testid="stChatMessage"] {
        border-radius: 12px;
        margin-bottom: 10px;
    }

    div.stButton > button {
        border-radius: 10px;
        min-height: 48px;
        font-weight: 500;
    }

    .source-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        margin-bottom: 8px;
        background-color: rgba(128, 128, 128, 0.12);
        border: 1px solid rgba(128, 128, 128, 0.20);
    }

    .welcome-box {
        padding: 25px;
        border-radius: 15px;
        background-color: rgba(128, 128, 128, 0.06);
        border: 1px solid rgba(128, 128, 128, 0.15);
        margin-bottom: 20px;
    }

    .executive-box {
        padding: 22px;
        border-radius: 15px;
        background-color: rgba(128, 128, 128, 0.06);
        border: 1px solid rgba(128, 128, 128, 0.15);
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.title("📊 RetailPulse-AI")

st.markdown(
    "**AI-Powered Retail Business Intelligence**"
)

st.caption(
    "Verified retail analytics powered by PostgreSQL, "
    "Python, RFM, CrewAI, Gemini and Power BI."
)


# ============================================================
# NAVIGATION
# ============================================================

assistant_tab, dashboard_tab = st.tabs(
    [
        "💬 AI Assistant",
        "📊 Executive Dashboard",
    ]
)


# ============================================================
# AI ASSISTANT TAB
# ============================================================

with assistant_tab:

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    try:

        sales_summary = load_sales_summary()

        if sales_summary:

            total_revenue = float(
                sales_summary["total_revenue"]
            )

            total_orders = int(
                sales_summary["total_orders"]
            )

            total_units = int(
                sales_summary["total_units"]
            )

            average_order_value = float(
                sales_summary["average_order_value"]
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "💰 Total Revenue",
                    f"£{total_revenue:,.2f}",
                )

            with col2:

                st.metric(
                    "🛒 Total Orders",
                    f"{total_orders:,}",
                )

            with col3:

                st.metric(
                    "📦 Total Units",
                    f"{total_units:,}",
                )

            with col4:

                st.metric(
                    "📈 Average Order Value",
                    f"£{average_order_value:,.2f}",
                )

    except Exception as error:

        st.warning(
            f"Unable to load KPI data: {error}"
        )

    st.divider()

    # --------------------------------------------------------
    # WELCOME
    # --------------------------------------------------------

    if len(st.session_state.messages) == 0:

        st.markdown(
            """
            <div class="welcome-box">

            ### 👋 Welcome to RetailPulse-AI

            I'm your retail business intelligence assistant.

            Ask me about:

            - 💰 Sales and revenue
            - 📦 Product performance
            - 👥 Customer segments
            - 🎯 RFM analysis
            - ⚠️ At-risk customers
            - 🌍 Country performance
            - 📈 Business trends

            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # SUGGESTED QUESTIONS
    # --------------------------------------------------------

    st.markdown(
        "### 💡 Explore your data"
    )

    questions = [
        "What is our total revenue?",
        "Which products generate the most revenue?",
        "Who are our Champions?",
        "Which customers are at risk?",
        "Which country generates the most revenue?",
        "Give me an executive business summary.",
    ]

    cols = st.columns(3)

    for i, question_text in enumerate(
        questions
    ):

        with cols[i % 3]:

            if st.button(
                question_text,
                use_container_width=True,
                key=f"suggested_{i}",
            ):

                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": question_text,
                    }
                )

                with st.spinner(
                    "🔎 Analyzing verified business data..."
                ):

                    answer = route_question(
                        question_text
                    )

                    visualization_type = (
                        get_visualization_type(
                            question_text
                        )
                    )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "visualization": (
                            visualization_type
                        ),
                    }
                )

                st.rerun()

    st.divider()

    # --------------------------------------------------------
    # CHAT HISTORY
    # --------------------------------------------------------

    for message in (
        st.session_state.messages
    ):

        if message["role"] == "user":

            with st.chat_message(
                "user",
                avatar="👤",
            ):

                st.markdown(
                    message["content"]
                )

        else:

            with st.chat_message(
                "assistant",
                avatar="🤖",
            ):

                st.markdown(
                    '<div class="source-badge">'
                    '✓ Verified RetailPulse-AI Analysis'
                    '</div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    message["content"]
                )

                visualization_type = (
                    message.get(
                        "visualization"
                    )
                )

                if visualization_type:

                    render_visualization(
                        visualization_type
                    )

    # --------------------------------------------------------
    # CHAT INPUT
    # --------------------------------------------------------

    question = st.chat_input(
        "Ask RetailPulse-AI about your business..."
    )

    if question:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.chat_message(
            "user",
            avatar="👤",
        ):

            st.markdown(question)

        with st.chat_message(
            "assistant",
            avatar="🤖",
        ):

            st.markdown(
                '<div class="source-badge">'
                '🔎 Analyzing verified business data...'
                '</div>',
                unsafe_allow_html=True,
            )

            with st.spinner(
                "RetailPulse-AI is thinking..."
            ):

                answer = route_question(
                    question
                )

                visualization_type = (
                    get_visualization_type(
                        question
                    )
                )

            st.markdown(answer)

            if visualization_type:

                render_visualization(
                    visualization_type
                )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "visualization": (
                    visualization_type
                ),
            }
        )

        st.rerun()


# ============================================================
# EXECUTIVE DASHBOARD TAB
# ============================================================

with dashboard_tab:

    st.header(
        "📊 Executive Dashboard"
    )

    st.caption(
        "A verified overview of retail sales, "
        "customers, products and geographic performance."
    )

    # --------------------------------------------------------
    # LOAD EXECUTIVE DATA
    # --------------------------------------------------------

    try:

        sales_summary = load_sales_summary()

        if not sales_summary:

            st.error(
                "Unable to load executive dashboard data."
            )

        else:

            total_revenue = float(
                sales_summary["total_revenue"]
            )

            total_orders = int(
                sales_summary["total_orders"]
            )

            total_units = int(
                sales_summary["total_units"]
            )

            average_order_value = float(
                sales_summary[
                    "average_order_value"
                ]
            )

            # ------------------------------------------------
            # EXECUTIVE KPIs
            # ------------------------------------------------

            st.markdown(
                "### 📌 Key Performance Indicators"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "💰 Revenue",
                    f"£{total_revenue:,.2f}",
                )

            with col2:

                st.metric(
                    "🛒 Orders",
                    f"{total_orders:,}",
                )

            with col3:

                st.metric(
                    "📦 Units Sold",
                    f"{total_units:,}",
                )

            with col4:

                st.metric(
                    "📈 Average Order Value",
                    f"£{average_order_value:,.2f}",
                )

            st.divider()

            # ------------------------------------------------
            # SALES PERFORMANCE
            # ------------------------------------------------

            st.markdown(
                "### 📈 Sales Performance"
            )

            show_monthly_revenue_chart()

            st.divider()

            # ------------------------------------------------
            # PRODUCT + COUNTRY
            # ------------------------------------------------

            left_col, right_col = st.columns(
                2
            )

            with left_col:

                st.markdown(
                    "### 🏆 Product Performance"
                )

                show_top_products_chart()

            with right_col:

                st.markdown(
                    "### 🌍 Geographic Performance"
                )

                show_country_revenue_chart()

            st.divider()

            # ------------------------------------------------
            # CUSTOMER INTELLIGENCE
            # ------------------------------------------------

            st.markdown(
                "### 👥 Customer Intelligence"
            )

            show_customer_segments_chart()

            st.divider()

            # ------------------------------------------------
            # AI EXECUTIVE SUMMARY
            # ------------------------------------------------

            st.markdown(
                "### 🤖 AI Executive Summary"
            )

            if st.button(
                "✨ Generate Executive Summary",
                use_container_width=True,
                key="generate_executive_summary",
            ):

                with st.spinner(
                    "Analyzing verified retail data..."
                ):

                    executive_summary = (
                        route_question(
                            "Give me an executive business summary."
                        )
                    )

                st.session_state[
                    "executive_summary"
                ] = executive_summary

            if st.session_state[
                "executive_summary"
            ]:

                st.markdown(
                    '<div class="executive-box">',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    st.session_state[
                        "executive_summary"
                    ]
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True,
                )

            else:

                st.info(
                    "Click 'Generate Executive Summary' "
                    "to let RetailPulse-AI analyze the "
                    "verified business data."
                )

            st.caption(
                "Executive analysis is generated from "
                "verified PostgreSQL business data."
            )

    except Exception as error:

        st.error(
            f"Unable to load Executive Dashboard data: {error}"
        )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header(
        "📊 RetailPulse-AI"
    )

    st.markdown(
        """
        ### Intelligence Stack

        🐍 **Python**

        🐘 **PostgreSQL**

        📊 **Power BI**

        🤖 **CrewAI**

        ✨ **Gemini**

        📈 **Plotly**

        🎈 **Streamlit**
        """
    )

    st.divider()

    st.markdown(
        "### 📁 Data Coverage"
    )

    st.caption(
        "December 2009 – December 9, 2010"
    )

    st.divider()

    st.markdown(
        "### 🧠 AI Architecture"
    )

    st.caption(
        "Factual questions → PostgreSQL"
    )

    st.caption(
        "Analytical questions → CrewAI + Gemini"
    )

    st.caption(
        "Visual questions → PostgreSQL + Plotly"
    )

    st.divider()

    st.caption(
        "RetailPulse-AI | Portfolio Project"
    )