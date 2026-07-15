import os
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import streamlit as st

from charts.plotly_charts import render_brand_bar, render_category_donut
from components.table import render_preview_table, render_full_table
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

TRANSLATIONS = {
    "en": {
        "dashboard_title": "Promotor Master Dashboard",
        "dashboard_subtitle": "Enterprise summary for promoter coverage, blacklist verification and store health.",
        "google_sheet_connected": "Google Sheet Connected",
        "last_sync": "Last Sync",
        "records": "Records",
        "version": "Version",
        "source": "Source",
        "last_refresh": "Last refresh",
        "loading_status": "Loading status: Ready",
        "loading_data": "Loading data...",
        "controls_title": "Dashboard Controls",
        "data_section": "Data",
        "refresh_data": "Refresh data",
        "sheet_id_url": "Google Sheet ID / URL",
        "sheet_gid": "Sheet GID",
        "use_private_api": "Use Google Sheets API",
        "use_local_csv": "Use local CSV",
        "filter_section": "Filter",
        "global_search": "Global Search",
        "global_search_placeholder": "Search by Store, Promotor, Mobile, Brand, Area Manager...",
        "area_manager": "Area Manager",
        "brand": "Brand",
        "category": "Category",
        "active": "Active",
        "advanced_filter": "Advanced Filter",
        "verification_only": "Verification only",
        "blacklist_only": "Blacklist only",
        "show_inactive": "Show inactive",
        "export_section": "Export",
        "export_csv": "Export CSV",
        "export_excel": "Export Excel",
        "export_blacklist_csv": "Export Blacklist CSV",
        "export_blacklist_excel": "Export Blacklist Excel",
        "help_section": "Help",
        "help_text": "Use filters to narrow the dataset. Refresh clears caches. Export using the buttons above.",
        "loading_error": "Unable to load Google Sheet data:",
        "sheet_error": "The sheet may not be public or shared. Try enabling Google Sheets API or use offline CSV.",
        "empty_data": "Data is empty. Please check the Sheet ID / URL and GID.",
        "executive_summary": "Executive Summary",
        "active_promoters": "Active Promoters",
        "active_only": "Active only",
        "blacklist_metric": "Blacklist",
        "blacklist_total": "Total blacklist records",
        "stores_metric": "Stores",
        "monitored_stores": "Monitored stores",
        "brands_metric": "Brands",
        "distinct_brands": "Distinct brands",
        "analysis_section": "Brand & Category Analysis",
        "health_score_title": "Dashboard Health Score",
        "health_score_note": "Health score based on coverage, verification, and duplicates.",
        "blacklist_center": "Blacklist Center",
        "no_blacklist_records": "No blacklist records were found in the dataset.",
        "top_preview": "Top 20 Data Preview",
        "view_full_data": "View Full Data",
        "view_mode": "View mode",
        "main_page": "Dashboard",
        "blacklist_page": "Blacklist",
        "raw_blacklist_note": "Showing the blacklist table exactly as the source sheet.",
        "language_label": "Language",
        "language_en": "English",
        "language_vi": "Tiếng Việt",
    },
    "vi": {
        "dashboard_title": "Bảng điều khiển Promotor",
        "dashboard_subtitle": "Tổng quan doanh nghiệp về coverage promotors, kiểm tra blacklist và sức khỏe cửa hàng.",
        "google_sheet_connected": "Đã kết nối Google Sheet",
        "last_sync": "Đồng bộ lần cuối",
        "records": "Số bản ghi",
        "version": "Phiên bản",
        "source": "Nguồn",
        "last_refresh": "Lần làm mới cuối",
        "loading_status": "Trạng thái tải: Sẵn sàng",
        "loading_data": "Đang tải dữ liệu...",
        "controls_title": "Điều khiển Dashboard",
        "data_section": "Dữ liệu",
        "refresh_data": "Làm mới dữ liệu",
        "sheet_id_url": "Google Sheet ID / URL",
        "sheet_gid": "Sheet GID",
        "use_private_api": "Dùng Google Sheets API",
        "use_local_csv": "Dùng CSV local",
        "filter_section": "Bộ lọc",
        "global_search": "Tìm kiếm chung",
        "global_search_placeholder": "Tìm theo Cửa hàng, Promotor, Số điện thoại, Thương hiệu, Quản lý khu vực...",
        "area_manager": "Quản lý khu vực",
        "brand": "Thương hiệu",
        "category": "Danh mục",
        "active": "Trạng thái",
        "advanced_filter": "Bộ lọc nâng cao",
        "verification_only": "Chỉ verification",
        "blacklist_only": "Chỉ blacklist",
        "show_inactive": "Hiện inactive",
        "export_section": "Xuất dữ liệu",
        "export_csv": "Xuất CSV",
        "export_excel": "Xuất Excel",
        "export_blacklist_csv": "Xuất blacklist CSV",
        "export_blacklist_excel": "Xuất blacklist Excel",
        "help_section": "Trợ giúp",
        "help_text": "Dùng bộ lọc để thu hẹp dữ liệu. Làm mới sẽ xóa cache. Xuất dữ liệu bằng các nút trên.",
        "loading_error": "Không tải được dữ liệu Google Sheet:",
        "sheet_error": "Sheet có thể chưa public hoặc chưa được chia sẻ. Thử bật Google Sheets API hoặc dùng CSV offline.",
        "empty_data": "Dữ liệu trống. Vui lòng kiểm tra lại Sheet ID / URL và GID.",
        "executive_summary": "Tóm tắt tổng quan",
        "active_promoters": "Promotor đang hoạt động",
        "active_only": "Chỉ hoạt động",
        "blacklist_metric": "Blacklist",
        "blacklist_total": "Tổng bản ghi blacklist",
        "stores_metric": "Cửa hàng",
        "monitored_stores": "Cửa hàng đang giám sát",
        "brands_metric": "Thương hiệu",
        "distinct_brands": "Số thương hiệu",
        "analysis_section": "Phân tích Thương hiệu & Danh mục",
        "health_score_title": "Điểm sức khỏe Dashboard",
        "health_score_note": "Điểm sức khỏe dựa trên coverage, kiểm tra và trùng lặp.",
        "blacklist_center": "Trung tâm Blacklist",
        "no_blacklist_records": "Không có bản ghi blacklist trong dữ liệu.",
        "top_preview": "Xem nhanh 20 dòng đầu",
        "view_full_data": "Xem toàn bộ dữ liệu",
        "view_mode": "Chế độ xem",
        "main_page": "Dashboard",
        "blacklist_page": "Blacklist",
        "raw_blacklist_note": "Hiển thị bảng blacklist giống như sheet gốc.",
        "language_label": "Ngôn ngữ",
        "language_en": "English",
        "language_vi": "Tiếng Việt",
    },
}


def get_label(lang: str, key: str) -> str:
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)
from utils.insights import (
    build_executive_summary,
    build_health_score,
    get_duplicate_count,
    get_store_coverage_insights,
)


# --- UI helpers ---

def render_header(record_count: int, source_label: str, last_sync: str, lang_code: str) -> None:
    st.markdown(
        f"""
        <div class='dashboard-header'>
            <div style='display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:18px;'>
                <div style='min-width:280px;'>
                    <div class='dash-title'>{get_label(lang_code, 'dashboard_title')}</div>
                    <div class='dash-subtitle'>{get_label(lang_code, 'dashboard_subtitle')}</div>
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


def render_status_bar(source_status: str, last_sync: str, lang_code: str) -> None:
    st.markdown(
        f"""
        <div class='status-strip'>
            <div style='display:flex; flex-wrap:wrap; justify-content:space-between; gap:14px;'>
                <div class='small-text'>{get_label(lang_code, 'source')}: {source_status}</div>
                <div class='small-text'>{get_label(lang_code, 'last_refresh')}: {last_sync}</div>
                <div class='small-text'>{get_label(lang_code, 'loading_status')}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_blacklist_page(blacklist_data: pd.DataFrame, lang_code: str) -> None:
    st.markdown(f"<div class='section-title'>{get_label(lang_code, 'blacklist_center')}</div>", unsafe_allow_html=True)
    st.info(get_label(lang_code, 'raw_blacklist_note'))
    if blacklist_data.empty:
        st.info(get_label(lang_code, 'no_blacklist_records'))
        return
    render_full_table(blacklist_data, blacklist_data.columns.tolist())


def render_sidebar(
    data: pd.DataFrame,
    sheet_ref: str,
    gid: str,
    use_private: bool,
    use_local_csv: bool,
    local_csv,
    selected_filters: Dict[str, List[str]],
    search_text: str,
    lang_code: str,
) -> Dict[str, object]:
    sidebar = st.sidebar
    sidebar.title(get_label(lang_code, "controls_title"))
    selected_view = sidebar.radio(
        get_label(lang_code, "view_mode"),
        [get_label(lang_code, "main_page"), get_label(lang_code, "blacklist_page")],
        index=0,
        key="selected_view",
    )
    sidebar.markdown("### " + get_label(lang_code, "data_section"))
    sidebar.button(get_label(lang_code, "refresh_data"), on_click=st.rerun)
    sidebar.text_input(get_label(lang_code, "sheet_id_url"), value=sheet_ref, key="sheet_ref")
    sidebar.text_input(get_label(lang_code, "sheet_gid"), value=gid, key="sheet_gid")
    use_private = sidebar.checkbox(get_label(lang_code, "use_private_api"), value=use_private, key="use_private")
    use_local_csv = sidebar.checkbox(get_label(lang_code, "use_local_csv"), value=use_local_csv, key="use_local_csv")
    if use_local_csv:
        local_csv = sidebar.file_uploader("Upload CSV", type=["csv"], key="local_csv")

    if selected_view == get_label(lang_code, "main_page"):
        sidebar.markdown("---")
        sidebar.markdown("### " + get_label(lang_code, "filter_section"))
    globals_search = sidebar.text_input(
        get_label(lang_code, "global_search"),
        value=search_text,
        placeholder=get_label(lang_code, "global_search_placeholder"),
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

    if selected_view == get_label(lang_code, "main_page"):
        sidebar.markdown("---")
        sidebar.markdown("### " + get_label(lang_code, "export_section"))
        sidebar.button(get_label(lang_code, "export_csv"), key="export_csv")
        sidebar.button(get_label(lang_code, "export_excel"), key="export_excel")
        sidebar.button(get_label(lang_code, "export_blacklist_csv"), key="export_blacklist_csv")
        sidebar.button(get_label(lang_code, "export_blacklist_excel"), key="export_blacklist_excel")

        sidebar.markdown("---")
        sidebar.markdown("### " + get_label(lang_code, "help_section"))
        sidebar.info(get_label(lang_code, "help_text"))

    return {
        "globals_search": globals_search,
        "selected_filters": selected_filters,
        "use_private": use_private,
        "use_local_csv": use_local_csv,
        "local_csv": local_csv,
        "selected_view": selected_view,
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
    language = st.sidebar.selectbox(
        "Language",
        ["English", "Tiếng Việt"],
        index=0,
        key="language_select",
    )
    lang_code = "en" if language == "English" else "vi"

    data = None
    error_message = None
    try:
        with st.spinner(get_label(lang_code, "loading_data")):
            data = load_data(sheet_ref, gid, use_private, local_file=local_csv)
    except Exception as exc:
        error_message = str(exc)

    if error_message:
        st.error(get_label(lang_code, "loading_error"))
        st.error(error_message)
        st.warning(get_label(lang_code, "sheet_error"))
        return

    if data is None or data.empty:
        st.warning(get_label(lang_code, "empty_data"))
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
        lang_code,
    )
    search_text = sidebar_state["globals_search"]
    selected_filters = sidebar_state["selected_filters"]
    use_private = sidebar_state["use_private"]
    use_local_csv = sidebar_state["use_local_csv"]
    local_csv = sidebar_state["local_csv"]
    selected_view = sidebar_state["selected_view"]

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
    render_header(len(data), get_label(lang_code, "google_sheet_connected"), current_time, lang_code)
    render_status_bar(get_label(lang_code, "google_sheet_connected"), current_time, lang_code)

    st.markdown(f"<div class='section-title'>{get_label(lang_code, 'executive_summary')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='alert-banner'>{summary_text}</div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4, gap="large")
    col1.markdown(
        f"<div class='metric-card'><div class='metric-title'>👥 {get_label(lang_code, 'active_promoters')}</div><div class='metric-value'>{len(filtered_data[filtered_data[cols.get('active')] == 'ACTIVE']) if cols.get('active') else len(filtered_data):,}</div><div class='metric-note'>{get_label(lang_code, 'active_only')}</div></div>",
        unsafe_allow_html=True,
    )
    col2.markdown(
        f"<div class='metric-card'><div class='metric-title'>⚠ {get_label(lang_code, 'blacklist_metric')}</div><div class='metric-value'>{len(blacklist_data):,}</div><div class='metric-note'>{get_label(lang_code, 'blacklist_total')}</div></div>",
        unsafe_allow_html=True,
    )
    col3.markdown(
        f"<div class='metric-card'><div class='metric-title'>🏪 {get_label(lang_code, 'stores_metric')}</div><div class='metric-value'>{len(store_summary):,}</div><div class='metric-note'>{get_label(lang_code, 'monitored_stores')}</div></div>",
        unsafe_allow_html=True,
    )
    col4.markdown(
        f"<div class='metric-card'><div class='metric-title'>📱 {get_label(lang_code, 'brands_metric')}</div><div class='metric-value'>{filtered_data[cols.get('brand')].nunique() if cols.get('brand') else 0:,}</div><div class='metric-note'>{get_label(lang_code, 'distinct_brands')}</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown(f"<div class='section-title'>{get_label(lang_code, 'analysis_section')}</div>", unsafe_allow_html=True)
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

    if selected_view == get_label(lang_code, "blacklist_page"):
        render_blacklist_page(blacklist_data, lang_code)
        return

    st.markdown(f"<div class='section-title'>{get_label(lang_code, 'top_preview')}</div>", unsafe_allow_html=True)
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
        st.button(get_label(lang_code, 'view_full_data'), key="view_full_data")


if __name__ == "__main__":
    main()
