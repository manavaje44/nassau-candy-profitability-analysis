import streamlit as st
import pandas as pd

st.set_page_config(page_title="Nassau Candy Dashboard", layout="wide")

# Load Data
df = pd.read_csv("Nassau Candy Distributor Original.csv")

# Date Conversion
df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True)

# Data Cleaning
df = df[df["Sales"] > 0]
df = df[df["Gross Profit"] != 0]

# ======================
# SIDEBAR FILTERS
# ======================

st.sidebar.header("Filters")
product_search = st.sidebar.text_input(
    "Search Product"
)

margin_threshold = st.sidebar.slider(
    "Minimum Margin %",
    0,
    100,
    20
)

division = st.sidebar.selectbox(
    "Select Division",
    ["All"] + list(df["Division"].unique())
)

start_date = st.sidebar.date_input(
    "Start Date",
    df["Order Date"].min()
)

end_date = st.sidebar.date_input(
    "End Date",
    df["Order Date"].max()
)

st.sidebar.markdown("---")

st.sidebar.info(
"""
Nassau Candy Distributor

Product Line Profitability Analysis

Data Analyst Internship Project
"""
)

# Apply Filters

filtered_df = df.copy()
if product_search:
    filtered_df = filtered_df[
        filtered_df["Product Name"]
        .str.contains(product_search, case=False)
    ]

if division != "All":
    filtered_df = filtered_df[
        filtered_df["Division"] == division
    ]

filtered_df = filtered_df[
    (filtered_df["Order Date"] >= pd.to_datetime(start_date))
    &
    (filtered_df["Order Date"] <= pd.to_datetime(end_date))
]

# KPI Calculations

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Gross Profit"].sum()
total_cost = filtered_df["Cost"].sum()

gross_margin = (
    total_profit / total_sales * 100
) if total_sales > 0 else 0

# Title

st.title("Product Line Profitability Analysis")
st.markdown("**Prepared by:** Manav Vaje")
st.caption("Nassau Candy Distributor | Revenue, Profitability & Margin Insights")

# KPI Cards

col1, col2, col3, col4 = st.columns(4)

col1.metric("Revenue", f"${total_sales:,.0f}")
col2.metric("Gross Profit", f"${total_profit:,.0f}")
col3.metric("Operating Cost", f"${total_cost:,.0f}")
col4.metric("Margin %", f"{gross_margin:.2f}%")

st.divider()

st.info(
"""
This dashboard analyzes product profitability, division performance,
cost efficiency and profit concentration across Nassau Candy Distributor's portfolio.
"""
)

# ==========================
# PRODUCT PROFITABILITY
# ==========================

st.subheader("Top Performing Products")

product_summary = (
    filtered_df
    .groupby("Product Name")
    .agg({
        "Sales":"sum",
        "Gross Profit":"sum",
        "Units":"sum"
    })
    .reset_index()
)

product_summary["Gross Margin %"] = (
    product_summary["Gross Profit"]
    /
    product_summary["Sales"]
) * 100

product_summary["Profit Per Unit"] = (
    product_summary["Gross Profit"]
    /
    product_summary["Units"]
)

product_summary = product_summary.sort_values(
    by="Gross Profit",
    ascending=False
)

st.dataframe(
    product_summary.head(10),
    hide_index=True
)

import plotly.express as px

st.subheader("Top 10 Most Profitable Products")

top_products = product_summary.head(10)

fig = px.bar(
    top_products,
    x="Product Name",
    y="Gross Profit",
    title="Top 10 Products by Gross Profit"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Division Financial Performance")

division_summary = (
    filtered_df
    .groupby("Division")
    .agg({
        "Sales":"sum",
        "Gross Profit":"sum"
    })
    .reset_index()
)

fig_division = px.bar(
    division_summary,
    x="Division",
    y=["Sales", "Gross Profit"],
    barmode="group",
    title="Revenue vs Profit by Division"
)

st.plotly_chart(fig_division, use_container_width=True)
division_margin = (
    filtered_df
    .groupby("Division")
    .agg({
        "Sales":"sum",
        "Gross Profit":"sum"
    })
    .reset_index()
)

division_margin["Gross Margin %"] = (
    division_margin["Gross Profit"]
    /
    division_margin["Sales"]
) * 100

best_division = division_margin.loc[
    division_margin["Gross Margin %"].idxmax(),
    "Division"
]

st.success(
    f"Highest Margin Division: {best_division}"
)

st.subheader("Gross Margin % by Division")

division_margin = (
    filtered_df
    .groupby("Division")
    .agg({
        "Sales":"sum",
        "Gross Profit":"sum"
    })
    .reset_index()
)

division_margin["Gross Margin %"] = (
    division_margin["Gross Profit"]
    /
    division_margin["Sales"]
) * 100

fig_margin = px.bar(
    division_margin,
    x="Division",
    y="Gross Margin %",
    title="Gross Margin Percentage by Division"
)

st.plotly_chart(fig_margin, use_container_width=True)

st.subheader("Cost Efficiency Analysis")

fig_scatter = px.scatter(
    filtered_df,
    x="Cost",
    y="Sales",
    color="Division",
    hover_name="Product Name",
    title="Cost vs Sales Analysis"
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("Products Requiring Margin Review")

risk_products = (
    filtered_df
    .groupby("Product Name")
    .agg({
        "Sales":"sum",
        "Gross Profit":"sum"
    })
    .reset_index()
)

risk_products["Gross Margin %"] = (
    risk_products["Gross Profit"]
    /
    risk_products["Sales"]
) * 100

risk_products = risk_products[
    risk_products["Gross Margin %"] < margin_threshold
]



risk_products = risk_products.sort_values(
    by="Gross Margin %",
    ascending=True
)

st.dataframe(
    risk_products,
    hide_index=True
)

st.subheader("Pareto Analysis (80% Profit Contribution)")

pareto = (
    filtered_df
    .groupby("Product Name")
    .agg({
        "Gross Profit":"sum"
    })
    .reset_index()
)

pareto = pareto.sort_values(
    by="Gross Profit",
    ascending=False
)

pareto["Cumulative Profit"] = (
    pareto["Gross Profit"].cumsum()
)

total_profit_pareto = (
    pareto["Gross Profit"].sum()
)

pareto["Cumulative %"] = (
    pareto["Cumulative Profit"]
    /
    total_profit_pareto
) * 100

fig_pareto = px.line(
    pareto,
    x="Product Name",
    y="Cumulative %",
    title="80% Profit Contribution Analysis"
)

st.plotly_chart(
    fig_pareto,
    use_container_width=True
)

st.subheader("Key Insights")

st.markdown("""
• Chocolate division generates the highest revenue.

• Profitability is concentrated among a small group of products.

• Several products have significantly lower margins.

• Margin performance differs across divisions.

• Product profitability analysis can support pricing decisions.
""")
st.subheader("Executive Summary")

st.info(
"""
• Dashboard identifies the most profitable products.

• Compares revenue and profit across divisions.

• Highlights low-margin products requiring review.

• Supports pricing and product portfolio decisions.

• Reveals profit concentration risks through Pareto analysis.
"""
)

product_summary["Gross Margin %"] = product_summary["Gross Margin %"].round(2)
product_summary["Profit Per Unit"] = product_summary["Profit Per Unit"].round(2)

product_summary["Gross Margin %"] = product_summary["Gross Margin %"].round(2)

product_summary["Profit Per Unit"] = product_summary["Profit Per Unit"].round(2)

risk_products["Gross Margin %"] = risk_products["Gross Margin %"].round(2)  