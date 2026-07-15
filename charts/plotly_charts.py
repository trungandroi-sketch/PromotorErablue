from typing import Optional

import pandas as pd
import streamlit as st

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    px = None
    PLOTLY_AVAILABLE = False


def render_brand_bar(df: pd.DataFrame, brand_col: str) -> None:
    chart_data = df[brand_col].value_counts().reset_index()
    chart_data.columns = ["brand", "count"]
    if chart_data.empty:
        st.info("Không có dữ liệu thương hiệu để hiển thị.")
        return

    if not PLOTLY_AVAILABLE:
        st.caption("Plotly chưa được cài đặt. Hiển thị biểu đồ cột đơn giản bằng Streamlit.")
        summary = chart_data.sort_values("count", ascending=False).head(12).set_index("brand")
        st.bar_chart(summary["count"])
        return

    fig = px.bar(
        chart_data.sort_values("count", ascending=False).head(12),
        x="count",
        y="brand",
        orientation="h",
        text="count",
        labels={"count": "Số lượng", "brand": "Brand"},
        color="count",
        color_continuous_scale="Blues",
    )
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        margin=dict(t=10, b=20, l=0, r=0),
        template="plotly_white",
        height=420,
    )
    fig.update_traces(marker_line_color="#eff6ff", marker_line_width=1.5, hovertemplate="%{y}: %{x}")
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True, "displayModeBar": True})


def render_category_donut(df: pd.DataFrame, category_col: str) -> None:
    chart_data = df[category_col].value_counts().reset_index()
    chart_data.columns = ["category", "count"]
    if chart_data.empty:
        st.info("Không có dữ liệu danh mục để hiển thị.")
        return

    if not PLOTLY_AVAILABLE:
        st.caption("Plotly chưa được cài đặt. Hiển thị tóm tắt danh mục bằng Streamlit.")
        st.dataframe(chart_data.sort_values("count", ascending=False).reset_index(drop=True))
        st.bar_chart(chart_data.set_index("category")['count'])
        return

    fig = px.pie(
        chart_data,
        names="category",
        values="count",
        hole=0.55,
        color_discrete_sequence=["#1d4ed8", "#3b82f6", "#60a5fa", "#93c5fd", "#bae6fd"],
    )
    fig.update_traces(textinfo="percent+label", hovertemplate="%{label}: %{value}")
    fig.update_layout(margin=dict(t=10, b=10, l=0, r=0), template="plotly_white", height=420)
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True, "displayModeBar": True})
