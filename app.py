import os
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import streamlit as st

from charts.plotly_charts import render_brand_bar, render_category_donut
from components.table import render_preview_table
from styles.theme import apply_theme
from utils.data import (
    DEFAULT_GID,
    DEFAULT_SHEET_ID,
    build_store_summary,
    filter_dataframe,
    get_dashboard_columns,
    get_blacklist_rows,
    load_data,
    parse_sheet_reference,
)
from utils.insights import (
    build_executive_summary,
    build_health_score,
    get_duplicate_count,
    get_store_coverage_insights,
)


# --- UI helpers ---

def render_header(record_count: int, source_label: str, last_sync: str) -> None:
    st.markdown(
        f"""
        <div class='dashboard-header'>
            <div style='display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:18px;'>
                <div style='min-width:280px;'>
                    <div class='dash-title'>Promotor Master Dashboard</div>
                    <div class='dash-subtitle'>Enterprise summary for promoter coverage, blacklist verification and store health.</div>
                </div>
                <div style='display:flex; flex-wrap:wrap; gap:12px; align-items:center;'>
                    <div class='status-pill connected'>Google Sheet Connected</div>
                    <div class='status-pill'>Last Sync: {last_sync}</div>
                    <div class='status-pill'>Records: {record_count:,}</div>
                    <div class='status-pill'>Version 2.0</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_bar(source_status: str, last_sync: str) -> None:
    st.markdown(
        f"""
        <div class='status-strip'>
            <div style='display:flex; flex-wrap:wrap; justify-content:space-between; gap:14px;'>
                <div class='small-text'>Source: {source_status}</div>
                <div class='small-text'>Last refresh: {last_sync}</div>
                <div class='small-text'>Loading status: Ready</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(
    data: pd.DataFrame,
    sheet_ref: str,
    gid: str,
    use_private: bool,
    use_local_csv: bool,
    local_csv,
    selected_filters: Dict[str, List[str]],
    search_text: str,
) -> Dict[str, object]:
    sidebar = st.sidebar
    sidebar.title("Dashboard Controls")
    sidebar.markdown("### Data")
    sidebar.button("Refresh data", on_click=st.rerun)
    sidebar.text_input("Google Sheet ID / URL", value=sheet_ref, key="sheet_ref")
    sidebar.text_input("Sheet GID", value=gid, key="sheet_gid")
    use_private = sidebar.checkbox("Dùng Google Sheets API", value=use_private, key="use_private")
    use_local_csv = sidebar.checkbox("Dùng CSV local", value=use_local_csv, key="use_local_csv")
    if use_local_csv:
        local_csv = sidebar.file_uploader("Upload CSV", type=["csv"], key="local_csv")

    sidebar.markdown("---")
    sidebar.markdown("### Filter")
    globals_search = sidebar.text_input(
        "Global Search",
        value=search_text,
        placeholder="Search by Store, Promotor, Mobile, Brand, Area Manager...",
        key="global_search",
    )

    cols = get_dashboard_columns(data.columns.tolist()) if data is not None else {}
    if cols.get("area_manager"):
        selected_filters["area_manager"] = sidebar.multiselect(
            "Area Manager",
            sorted(data[cols["area_manager"]].dropna().unique().tolist()),
            key="selected_area",
            default=selected_filters.get("area_manager", []),
        )
    if cols.get("brand"):
        selected_filters["brand"] = sidebar.multiselect(
            "Brand",
            sorted(data[cols["brand"]].dropna().unique().tolist()),
            key="selected_brand",
            default=selected_filters.get("brand", []),
        )
    if cols.get("category"):
        selected_filters["category"] = sidebar.multiselect(
            "Category",
            sorted(data[cols["category"]].dropna().unique().tolist()),
            key="selected_category",
            default=selected_filters.get("category", []),
        )
    if cols.get("active"):
        selected_filters["active"] = sidebar.multiselect(
            "Active",
            sorted(data[cols["active"]].dropna().unique().tolist()),
            key="selected_active",
            default=selected_filters.get("active", []),
        )

    with sidebar.expander("Advanced Filter", expanded=False):
        sidebar.checkbox("Verification only", value=False, key="verification_only")
        sidebar.checkbox("Blacklist only", value=False, key="blacklist_only")
        sidebar.checkbox("Show inactive", value=False, key="show_inactive")

    sidebar.markdown("---")
    sidebar.markdown("### Export")
    sidebar.button("Export CSV", key="export_csv")
    sidebar.button("Export Excel", key="export_excel")
    sidebar.button("Export Blacklist CSV", key="export_blacklist_csv")
    sidebar.button("Export Blacklist Excel", key="export_blacklist_excel")

    sidebar.markdown("---")
    sidebar.markdown("### Help")
    sidebar.info(
        "Use filters to narrow the dataset. Refresh clears caches. Export using the buttons above."
    )

    return {
        "globals_search": globals_search,
        "selected_filters": selected_filters,
        "use_private": use_private,
        "use_local_csv": use_local_csv,
        "local_csv": local_csv,
    }


def main() -> None:
    st.set_page_config(page_title="Promotor Dashboard", page_icon=":bar_chart:", layout="wide")
    apply_theme()

    sheet_ref = os.environ.get("GOOGLE_SHEET_ID", DEFAULT_SHEET_ID)
    gid = os.environ.get("GOOGLE_SHEET_GID", DEFAULT_GID)
    use_private = False
    use_local_csv = False
    local_csv = None
    selected_filters: Dict[str, List[str]] = {}
    search_text = ""

    data = None
    error_message = None
    try:
        with st.spinner("Loading data..."):
            data = load_data(sheet_ref, gid, use_private, local_file=local_csv)
    except Exception as exc:
        error_message = str(exc)

    if error_message:
        st.error("Không tải được dữ liệu Google Sheet:")
        st.error(error_message)
        st.warning(
            "Sheet có thể chưa public hoặc chưa được chia sẻ. Thử bật Google Sheets API hoặc dùng CSV offline."
        )
        return

    if data is None or data.empty:
        st.warning("Dữ liệu trống. Vui lòng kiểm tra lại Sheet ID / URL và GID.")
        return

    sidebar_state = render_sidebar(
        data,
        sheet_ref,
        gid,
        use_private,
        use_local_csv,
        local_csv,
        selected_filters,
        search_text,
    )
    search_text = sidebar_state["globals_search"]
    selected_filters = sidebar_state["selected_filters"]
    use_private = sidebar_state["use_private"]
    use_local_csv = sidebar_state["use_local_csv"]
    local_csv = sidebar_state["local_csv"]

    cols = get_dashboard_columns(data.columns.tolist())
    filtered_data = filter_dataframe(data, selected_filters, search_text)
    blacklist_data = get_blacklist_rows(data, cols)
    store_summary = pd.DataFrame()
    if not filtered_data.empty:
        store_summary = build_store_summary(filtered_data, cols)

    duplicate_mobile = get_duplicate_count(filtered_data, cols.get("mobile"))
    duplicate_nik = get_duplicate_count(filtered_data, cols.get("name"))
    coverage = get_store_coverage_insights(filtered_data, store_summary, cols)

    health_score = build_health_score(
        total_stores=len(store_summary),
        missing_ce=coverage["stores_missing_ce"],
        missing_ict=coverage["stores_missing_ict"],
        missing_brand_coverage=coverage["stores_missing_brand_coverage"],
        blacklist_count=len(blacklist_data),
        duplicate_mobile=duplicate_mobile,
        duplicate_nik=duplicate_nik,
    )

    summary_text = build_executive_summary(
        total_stores=len(store_summary),
        issues=coverage["stores_with_issues"],
        missing_ict=coverage["stores_missing_ict"],
        missing_ce=coverage["stores_missing_ce"],
        blacklist_count=len(blacklist_data),
        duplicate_mobile=duplicate_mobile,
        duplicate_nik=duplicate_nik,
    )

    current_time = datetime.now().strftime("%d %b %Y %H:%M")
    render_header(len(data), "Google Sheet Connected", current_time)
    render_status_bar("Google Sheet Connected", current_time)

    st.markdown("<div class='section-title'>Executive Summary</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='alert-banner'>{summary_text}</div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4, gap="large")
    col1.markdown(
        f"<div class='metric-card'><div class='metric-title'>👥 Active Promotors</div><div class='metric-value'>{len(filtered_data[filtered_data[cols.get('active')] == 'ACTIVE']) if cols.get('active') else len(filtered_data):,}</div><div class='metric-note'>Active only</div></div>",
        unsafe_allow_html=True,
    )
    col2.markdown(
        f"<div class='metric-card'><div class='metric-title'>⚠ Blacklist</div><div class='metric-value'>{len(blacklist_data):,}</div><div class='metric-note'>Total blacklist records</div></div>",
        unsafe_allow_html=True,
    )
    col3.markdown(
        f"<div class='metric-card'><div class='metric-title'>🏪 Stores</div><div class='metric-value'>{len(store_summary):,}</div><div class='metric-note'>Monitored stores</div></div>",
        unsafe_allow_html=True,
    )
    col4.markdown(
        f"<div class='metric-card'><div class='metric-title'>📱 Brands</div><div class='metric-value'>{filtered_data[cols.get('brand')].nunique() if cols.get('brand') else 0:,}</div><div class='metric-note'>Distinct brands</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='section-title'>Brand & Category Analysis</div>", unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns([3, 2], gap="large")
    with chart_col1:
        if cols.get("brand"):
            render_brand_bar(filtered_data, cols["brand"])
    with chart_col2:
        if cols.get("category"):
            render_category_donut(filtered_data, cols["category"])
        st.markdown(
            f"<div class='health-score'><div style='font-size:1rem; font-weight:700; margin-bottom:12px;'>Dashboard Health Score</div><div style='font-size:2.5rem; font-weight:700;'>{health_score}</div><div class='small-text'>Health score based on coverage, verification, and duplicates.</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='section-title'>Blacklist Center</div>", unsafe_allow_html=True)
    if blacklist_data.empty:
        st.info("Không có blacklist records trong toàn bộ dữ liệu.")
    else:
        render_preview_table(
            blacklist_data,
            [
                cols.get("store_id"),
                cols.get("store_name"),
                cols.get("brand"),
                cols.get("category"),
                cols.get("active"),
                cols.get("name"),
                cols.get("mobile"),
                cols.get("name_verification"),
                cols.get("nik_verification"),
                cols.get("area_manager"),
            ],
        )

    st.markdown("<div class='section-title'>Top 20 Data Preview</div>", unsafe_allow_html=True)
    render_preview_table(
        filtered_data,
        [
            cols.get("store_id"),
            cols.get("store_name"),
            cols.get("brand"),
            cols.get("category"),
            cols.get("active"),
            cols.get("name"),
            cols.get("mobile"),
        ],
    )

    if len(filtered_data) > 20:
        st.button("View Full Data", key="view_full_data")


if __name__ == "__main__":
    main()
