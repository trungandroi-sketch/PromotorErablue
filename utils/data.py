import io
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import certifi
import pandas as pd
import requests
import streamlit as st

DEFAULT_SHEET_ID = "15Hpk_d8G2UFtiOzNcd-CqtidzIZPoRwLXt5dXU1jjas"
DEFAULT_GID = "0"


def get_csv_export_url(sheet_id: str, gid: str = "0") -> str:
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


def get_csv_gviz_url(sheet_id: str, gid: str = "0") -> str:
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"


def parse_sheet_reference(sheet_ref: str, default_gid: str) -> Tuple[str, str]:
    sheet_ref = sheet_ref.strip()
    if not sheet_ref:
        return sheet_ref, default_gid

    gid = default_gid
    parsed = urlparse(sheet_ref)
    if parsed.scheme and parsed.netloc:
        query = parse_qs(parsed.query)
        if "gid" in query and query["gid"]:
            gid = query["gid"][0]

        fragment = parse_qs(parsed.fragment)
        if "gid" in fragment and fragment["gid"]:
            gid = fragment["gid"][0]

        match = re.search(r"/d/([a-zA-Z0-9_-]+)", parsed.path)
        if match:
            sheet_ref = match.group(1)

    return sheet_ref, gid


@st.cache_data(show_spinner=False)
def load_public_sheet(sheet_id: str, gid: str) -> pd.DataFrame:
    urls = [get_csv_export_url(sheet_id, gid), get_csv_gviz_url(sheet_id, gid)]
    last_error = None

    for url in urls:
        try:
            response = requests.get(url, timeout=20, verify=certifi.where())
            response.raise_for_status()
            data = io.StringIO(response.text)
            df = pd.read_csv(data, dtype=str)
            df.columns = [col.strip() for col in df.columns]
            return df.fillna("")
        except requests.exceptions.RequestException as exc:
            last_error = exc
            continue

    raise RuntimeError(
        f"Không thể tải Google Sheet public: {last_error}.\n"
        "Sheet này có thể vẫn yêu cầu đăng nhập hoặc chưa được chia sẻ public. "
        "Thử bật Google Sheets API hoặc dùng CSV offline."
    ) from last_error


@st.cache_data(show_spinner=False)
def load_private_sheet(sheet_id: str, gid: str) -> pd.DataFrame:
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError as exc:
        raise RuntimeError(
            "Missing Google Sheets dependencies. Install from requirements.txt."
        ) from exc

    creds = None
    json_text = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if json_text:
        credentials_info = json.loads(json_text)
        creds = Credentials.from_service_account_info(
            credentials_info,
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
        )
    elif cred_path:
        creds = Credentials.from_service_account_file(
            cred_path,
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
        )
    else:
        local_path = Path("credentials.json")
        if local_path.exists():
            creds = Credentials.from_service_account_file(
                local_path,
                scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
            )

    if creds is None:
        raise RuntimeError(
            "Không tìm thấy credentials cho Google Sheets API.\n"
            "Đặt GOOGLE_APPLICATION_CREDENTIALS hoặc GOOGLE_SERVICE_ACCOUNT_JSON,\n"
            "hoặc tạo file credentials.json trong thư mục dự án."
        )

    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(sheet_id)
    try:
        worksheet = spreadsheet.worksheet_by_id(int(gid))
    except Exception:
        worksheet = spreadsheet.get_worksheet(0)

    records = worksheet.get_all_records(head=1)
    df = pd.DataFrame(records)
    df.columns = [str(col).strip() for col in df.columns]
    return df.fillna("")


def load_local_csv(local_file) -> pd.DataFrame:
    if hasattr(local_file, "getvalue"):
        content = local_file.getvalue()
    elif hasattr(local_file, "read"):
        content = local_file.read()
    else:
        content = local_file

    if isinstance(content, bytes):
        data = io.BytesIO(content)
    else:
        data = io.StringIO(content)

    df = pd.read_csv(data, dtype=str)
    df.columns = [col.strip() for col in df.columns]
    return df.fillna("")


def load_data(
    sheet_id: str,
    gid: str,
    use_private: bool,
    local_file=None,
) -> pd.DataFrame:
    if local_file is not None:
        return load_local_csv(local_file)
    if use_private:
        return load_private_sheet(sheet_id, gid)
    return load_public_sheet(sheet_id, gid)


def get_best_column(columns: List[str], candidates: List[str]) -> Optional[str]:
    normalized = {col.strip().lower(): col for col in columns}
    for candidate in candidates:
        if candidate.lower() in normalized:
            return normalized[candidate.lower()]
    return None


def get_dashboard_columns(columns: List[str]) -> Dict[str, Optional[str]]:
    return {
        "area_manager": get_best_column(columns, ["area manager", "area_manager", "area"]),
        "brand": get_best_column(columns, ["brand", "thương hiệu", "hãng"]),
        "category": get_best_column(columns, ["category", "danh mục"]),
        "status": get_best_column(columns, ["status"]),
        "name_verification": get_best_column(columns, ["name verification", "name_verification"]),
        "nik_verification": get_best_column(columns, ["nik verification", "nik_verification"]),
        "active": get_best_column(columns, ["active/inactive", "active"]),
        "store_name": get_best_column(columns, ["store name", "store_name"]),
        "store_id": get_best_column(columns, ["store id", "store_id"]),
        "name": get_best_column(columns, ["name"]),
        "join_date": get_best_column(columns, ["join date", "join_date"]),
        "year": get_best_column(columns, ["year"]),
        "mobile": get_best_column(columns, ["mobile", "contact number"]),
    }


def filter_dataframe(
    df: pd.DataFrame,
    filters: Dict[str, List[str]],
    search_text: str,
) -> pd.DataFrame:
    filtered = df
    for col, values in filters.items():
        if values and col in filtered.columns:
            filtered = filtered[filtered[col].isin(values)]

    if search_text:
        mask = pd.Series(False, index=filtered.index)
        for col in filtered.select_dtypes(include="object").columns:
            mask |= filtered[col].str.contains(search_text, case=False, na=False)
        filtered = filtered[mask]

    return filtered


def get_blacklist_rows(df: pd.DataFrame, cols: Dict[str, Optional[str]]) -> pd.DataFrame:
    mask = pd.Series(False, index=df.index)
    blacklist_pattern = r"(?:black|block|blk)[\s_-]*list(?:ed)?"
    for col in df.select_dtypes(include="object").columns:
        mask |= df[col].astype(str).str.contains(blacklist_pattern, case=False, na=False)
    return df[mask]


def build_store_summary(df: pd.DataFrame, cols: Dict[str, Optional[str]]) -> pd.DataFrame:
    group_keys = []
    if cols["store_id"]:
        group_keys.append(cols["store_id"])
    if cols["store_name"] and cols["store_name"] not in group_keys:
        group_keys.append(cols["store_name"])
    if not group_keys:
        return pd.DataFrame()

    if cols["active"]:
        active_df = df[df[cols["active"]] == "ACTIVE"]
        inactive_df = df[df[cols["active"]] == "INACTIVE"]
        summary = active_df.groupby(group_keys).size().to_frame("total_promotor")
    else:
        active_df = df
        inactive_df = df.iloc[0:0]
        summary = df.groupby(group_keys).size().to_frame("total_promotor")

    if cols["brand"]:
        summary["distinct_brand_count"] = active_df.groupby(group_keys)[cols["brand"]].nunique()
    if cols["category"]:
        summary["ce_count"] = active_df[active_df[cols["category"]] == "CE"].groupby(group_keys).size()
        summary["finance_count"] = active_df[active_df[cols["category"]] == "FINANCE"].groupby(group_keys).size()
        summary["ict_count"] = active_df[active_df[cols["category"]].isin(["PHONE", "LAPTOP"])].groupby(group_keys).size()
        if cols["brand"]:
            summary["ce_brand_count"] = (
                active_df[active_df[cols["category"]] == "CE"].groupby(group_keys)[cols["brand"]].nunique()
            )
            summary["ict_brand_count"] = (
                active_df[active_df[cols["category"]].isin(["PHONE", "LAPTOP"])].groupby(group_keys)[cols["brand"]].nunique()
            )
    if cols["active"]:
        summary["active_count"] = active_df.groupby(group_keys).size()
        summary["inactive_count"] = inactive_df.groupby(group_keys).size()
    if cols["name_verification"]:
        summary["blacklist_name"] = df[df[cols["name_verification"]].str.upper() == "BLACKLISTED"].groupby(group_keys).size()
    if cols["nik_verification"]:
        summary["blacklist_nik"] = df[df[cols["nik_verification"]].str.upper() == "BLACKLISTED"].groupby(group_keys).size()

    summary = summary.fillna(0).reset_index()

    integer_columns = [
        "total_promotor",
        "distinct_brand_count",
        "ce_count",
        "ict_count",
        "finance_count",
        "ce_brand_count",
        "ict_brand_count",
        "active_count",
        "inactive_count",
        "blacklist_name",
        "blacklist_nik",
    ]
    for col in integer_columns:
        if col in summary.columns:
            summary[col] = summary[col].astype(int)

    if "ce_count" in summary.columns:
        summary["pct_ce"] = (summary["ce_count"] / summary["total_promotor"] * 100).round(0).fillna(0).astype(int)
    else:
        summary["pct_ce"] = 0
    if "ict_count" in summary.columns:
        summary["pct_ict"] = (summary["ict_count"] / summary["total_promotor"] * 100).round(0).fillna(0).astype(int)
    else:
        summary["pct_ict"] = 0
    if "finance_count" in summary.columns:
        summary["pct_finance"] = (summary["finance_count"] / summary["total_promotor"] * 100).round(0).fillna(0).astype(int)
    else:
        summary["pct_finance"] = 0

    def build_warnings(row: pd.Series) -> str:
        warnings = []
        if "ce_count" in row.index:
            if row["ce_count"] == 0:
                warnings.append("Thiếu CE")
            elif row["ce_count"] < 2:
                warnings.append("CE < 2 người")
        if "ict_count" in row.index:
            if row["ict_count"] == 0:
                warnings.append("Thiếu ICT")
            elif row["ict_count"] < 2:
                warnings.append("ICT < 2 người")
        if cols["brand"]:
            if "ce_brand_count" in row.index and row["ce_count"] > 0 and row["ce_brand_count"] < 2:
                warnings.append("CE < 2 brand")
            if "ict_brand_count" in row.index and row["ict_count"] > 0 and row["ict_brand_count"] < 2:
                warnings.append("ICT < 2 brand")
        return ", ".join(warnings) if warnings else "OK"

    summary["warnings"] = summary.apply(build_warnings, axis=1)
    summary["note"] = summary["warnings"].replace(
        {
            "OK": "Không có vấn đề",
        }
    )
    return summary
