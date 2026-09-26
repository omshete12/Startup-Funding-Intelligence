import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Startup Funding Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    df = pd.read_csv("data/startup_funding_cleaned.csv")

    # Convert date
    df["funding_date"] = pd.to_datetime(
        df["funding_date"],
        errors="coerce"
    )

    # Create year
    df["year"] = df["funding_date"].dt.year

    # Make sure funding amount is numeric
    df["funding_amount_usd"] = pd.to_numeric(
        df["funding_amount_usd"],
        errors="coerce"
    )

    return df


df = load_data()


# ============================================================
# TITLE
# ============================================================

st.title("🚀 Startup Funding Intelligence")

st.markdown(
    """
    **Interactive analysis of startup funding activity in India**

    Explore funding trends, investment types, geographic concentration,
    industries, and startup-level funding patterns.
    """
)

st.divider()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Filters")

# -------------------------
# Year Filter
# -------------------------

years = sorted(
    df["year"].dropna().unique().astype(int)
)

selected_years = st.sidebar.multiselect(
    "Funding Year",
    options=years,
    default=years
)


# -------------------------
# Industry Filter
# -------------------------

industries = sorted(
    df["industry_standardized"]
    .dropna()
    .unique()
)

selected_industries = st.sidebar.multiselect(
    "Industry",
    options=industries,
    default=industries
)


# -------------------------
# City Filter
# -------------------------

cities = sorted(
    df["city"]
    .dropna()
    .unique()
)

selected_cities = st.sidebar.multiselect(
    "City",
    options=cities,
    default=cities
)


# -------------------------
# Investment Type Filter
# -------------------------

investment_types = sorted(
    df["investment_type"]
    .dropna()
    .unique()
)

selected_investment_types = st.sidebar.multiselect(
    "Investment Type",
    options=investment_types,
    default=investment_types
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df[
    (df["year"].isin(selected_years)) &
    (df["industry_standardized"].isin(selected_industries)) &
    (df["city"].isin(selected_cities)) &
    (df["investment_type"].isin(selected_investment_types))
].copy()


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_records = len(filtered_df)

disclosed_df = filtered_df[
    filtered_df["funding_amount_usd"].notna()
]

disclosed_records = len(disclosed_df)

total_funding = disclosed_df[
    "funding_amount_usd"
].sum()

unique_startups = filtered_df[
    "startup_name_standardized"
].nunique()


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Funding Records",
        f"{total_records:,}"
    )

with col2:
    st.metric(
        "Disclosed Records",
        f"{disclosed_records:,}"
    )

with col3:
    st.metric(
        "Disclosed Funding",
        f"${total_funding / 1e9:.2f}B"
    )

with col4:
    st.metric(
        "Unique Startups",
        f"{unique_startups:,}"
    )


st.divider()


# ============================================================
# FUNDING ACTIVITY BY YEAR
# ============================================================

st.subheader("📈 Funding Activity Over Time")

yearly_data = (
    filtered_df
    .groupby("year")
    .agg(
        funding_records=("Startup Name", "count"),
        unique_startups=("startup_name_standardized", "nunique"),
        disclosed_funding=("funding_amount_usd", "sum")
    )
    .reset_index()
)

yearly_data["disclosed_funding_billion"] = (
    yearly_data["disclosed_funding"] / 1e9
)


col1, col2 = st.columns(2)


with col1:

    fig_records = px.bar(
        yearly_data,
        x="year",
        y="funding_records",
        title="Funding Records by Year",
        labels={
            "year": "Year",
            "funding_records": "Funding Records"
        }
    )

    fig_records.update_layout(
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_records,
        use_container_width=True
    )


with col2:

    fig_funding = px.bar(
        yearly_data,
        x="year",
        y="disclosed_funding_billion",
        title="Disclosed Funding by Year",
        labels={
            "year": "Year",
            "disclosed_funding_billion": "Funding (USD Billion)"
        }
    )

    fig_funding.update_layout(
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_funding,
        use_container_width=True
    )


# ============================================================
# INVESTMENT TYPE
# ============================================================

st.subheader("💰 Investment Type Distribution")

investment_data = (
    filtered_df["investment_type"]
    .value_counts()
    .reset_index()
)

investment_data.columns = [
    "investment_type",
    "records"
]

col1, col2 = st.columns(2)


with col1:

    fig_investment = px.pie(
        investment_data.head(8),
        names="investment_type",
        values="records",
        hole=0.45,
        title="Funding Records by Investment Type"
    )

    st.plotly_chart(
        fig_investment,
        use_container_width=True
    )


with col2:

    st.dataframe(
        investment_data,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# INDUSTRY ANALYSIS
# ============================================================

st.subheader("🏭 Industry Analysis")

industry_data = (
    filtered_df["industry_standardized"]
    .value_counts()
    .head(15)
    .reset_index()
)

industry_data.columns = [
    "industry",
    "records"
]

fig_industry = px.bar(
    industry_data.sort_values("records"),
    x="records",
    y="industry",
    orientation="h",
    title="Top Industries by Funding Records",
    labels={
        "records": "Funding Records",
        "industry": "Industry"
    }
)

st.plotly_chart(
    fig_industry,
    use_container_width=True
)


# ============================================================
# GEOGRAPHIC ANALYSIS
# ============================================================

st.subheader("📍 Geographic Distribution")

city_data = (
    filtered_df["city"]
    .value_counts()
    .head(15)
    .reset_index()
)

city_data.columns = [
    "city",
    "records"
]

fig_city = px.bar(
    city_data.sort_values("records"),
    x="records",
    y="city",
    orientation="h",
    title="Top Cities by Funding Records",
    labels={
        "records": "Funding Records",
        "city": "City"
    }
)

st.plotly_chart(
    fig_city,
    use_container_width=True
)


# ============================================================
# TOP STARTUPS BY FUNDING
# ============================================================

st.subheader("🏆 Top Startups by Disclosed Funding")

startup_data = (
    filtered_df
    .dropna(subset=["funding_amount_usd"])
    .groupby("startup_name_standardized")
    .agg(
        funding_records=("startup_name_standardized", "size"),
        total_funding=("funding_amount_usd", "sum")
    )
    .reset_index()
    .sort_values(
        "total_funding",
        ascending=False
    )
    .head(15)
)

startup_data["total_funding_billion"] = (
    startup_data["total_funding"] / 1e9
)

fig_startups = px.bar(
    startup_data.sort_values("total_funding_billion"),
    x="total_funding_billion",
    y="startup_name_standardized",
    orientation="h",
    title="Top 15 Startups by Disclosed Funding",
    labels={
        "total_funding_billion": "Funding (USD Billion)",
        "startup_name_standardized": "Startup"
    },
    hover_data=[
        "funding_records",
        "total_funding"
    ]
)

st.plotly_chart(
    fig_startups,
    use_container_width=True
)


# ============================================================
# FUNDING DISTRIBUTION
# ============================================================

st.subheader("📊 Funding Amount Distribution")

amount_data = filtered_df[
    filtered_df["funding_amount_usd"] > 0
].copy()

fig_distribution = px.histogram(
    amount_data,
    x="funding_amount_usd",
    nbins=50,
    title="Distribution of Disclosed Funding Amounts",
    labels={
        "funding_amount_usd": "Funding Amount (USD)"
    }
)

fig_distribution.update_xaxes(
    type="log"
)

st.plotly_chart(
    fig_distribution,
    use_container_width=True
)


# ============================================================
# DATA TABLE
# ============================================================

st.subheader("📋 Filtered Funding Records")

display_columns = [
    "funding_date",
    "startup_name_standardized",
    "industry_standardized",
    "SubVertical",
    "city",
    "investors",
    "investment_type",
    "funding_amount_usd"
]

available_columns = [
    col for col in display_columns
    if col in filtered_df.columns
]

st.dataframe(
    filtered_df[available_columns]
    .sort_values(
        "funding_date",
        ascending=False
    ),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Startup Funding Intelligence | "
    "Data analysis based on the cleaned startup funding dataset."
)
