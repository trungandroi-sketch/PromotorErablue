from typing import List

import pandas as pd
import streamlit as st


def render_preview_table(df: pd.DataFrame, columns: List[str]) -> None:
    try:
        from st_aggrid import AgGrid, GridOptionsBuilder
    except ImportError:
        st.warning("AgGrid không được cài đặt. Hiển thị bảng bằng Streamlit mặc định.")
        st.dataframe(df[columns].head(20), use_container_width=True)
        return

    builder = GridOptionsBuilder.from_dataframe(df[columns].head(20))
    builder.configure_default_column(resizable=True, filter=True, sortable=True, floating_filter=True)
    builder.configure_grid_options(domLayout="normal")
    builder.configure_selection(selection_mode="single", use_checkbox=False)
    builder.configure_grid_options(enableBrowserTooltips=True)
    builder.configure_grid_options(ensureDomOrder=True)
    builder.configure_column(columns[0], pinned="left")
    builder.configure_grid_options(rowHeight=42)
    grid_options = builder.build()
    AgGrid(
        df[columns].head(20),
        gridOptions=grid_options,
        enable_enterprise_modules=False,
        fit_columns_on_grid_load=True,
        height=460,
        allow_unsafe_jscode=True,
    )


def render_full_table(df: pd.DataFrame, columns: List[str]) -> None:
    try:
        from st_aggrid import AgGrid, GridOptionsBuilder
    except ImportError:
        st.dataframe(df[columns], use_container_width=True)
        return

    builder = GridOptionsBuilder.from_dataframe(df[columns])
    builder.configure_default_column(resizable=True, filter=True, sortable=True, floating_filter=True)
    builder.configure_grid_options(domLayout="normal")
    builder.configure_selection(selection_mode="multiple", use_checkbox=True)
    builder.configure_grid_options(enableBrowserTooltips=True)
    builder.configure_grid_options(ensureDomOrder=True)
    if columns:
        builder.configure_column(columns[0], pinned="left")
    builder.configure_pagination(paginationAutoPageSize=True)
    builder.configure_grid_options(rowHeight=42)
    grid_options = builder.build()
    AgGrid(
        df[columns],
        gridOptions=grid_options,
        enable_enterprise_modules=False,
        fit_columns_on_grid_load=True,
        height=520,
        allow_unsafe_jscode=True,
    )
