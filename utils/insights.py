from typing import Dict, Optional

import pandas as pd

from utils.data import get_blacklist_rows


def get_duplicate_count(df: pd.DataFrame, column: Optional[str]) -> int:
    if not column or column not in df.columns:
        return 0
    duplicated = df[column].astype(str).replace("", pd.NA).dropna()
    return duplicated.duplicated(keep=False).sum()


def get_store_coverage_insights(df: pd.DataFrame, store_summary: pd.DataFrame, cols: Dict[str, Optional[str]]) -> Dict[str, int]:
    metrics = {
        "stores_missing_ce": 0,
        "stores_missing_ict": 0,
        "stores_missing_brand_coverage": 0,
        "stores_with_issues": 0,
    }

    if store_summary.empty:
        return metrics

    if "ce_count" in store_summary.columns:
        metrics["stores_missing_ce"] = int((store_summary["ce_count"] == 0).sum())
    if "ict_count" in store_summary.columns:
        metrics["stores_missing_ict"] = int((store_summary["ict_count"] == 0).sum())
    if "distinct_brand_count" in store_summary.columns:
        metrics["stores_missing_brand_coverage"] = int((store_summary["distinct_brand_count"] < 2).sum())
    if "warnings" in store_summary.columns:
        metrics["stores_with_issues"] = int((store_summary["warnings"] != "OK").sum())

    return metrics


def build_health_score(
    total_stores: int,
    missing_ce: int,
    missing_ict: int,
    missing_brand_coverage: int,
    blacklist_count: int,
    duplicate_mobile: int,
    duplicate_nik: int,
) -> int:
    if total_stores == 0:
        return 0

    coverage_impact = min(100, ((missing_ce + missing_ict + missing_brand_coverage) / max(1, total_stores)) * 60)
    verification_impact = min(100, (blacklist_count / max(1, total_stores * 4)) * 20)
    duplicate_impact = min(100, ((duplicate_mobile + duplicate_nik) / max(1, total_stores * 2)) * 20)
    score = 100 - (coverage_impact + verification_impact + duplicate_impact)
    return max(0, min(100, int(score)))


def build_executive_summary(
    total_stores: int,
    issues: int,
    missing_ict: int,
    missing_ce: int,
    blacklist_count: int,
    duplicate_mobile: int,
    duplicate_nik: int,
) -> str:
    components = [
        f"{total_stores:,} stores are monitored.",
        f"{issues:,} stores require attention.",
    ]

    if missing_ict:
        components.append(f"{missing_ict:,} stores are missing ICT promotors.")
    if missing_ce:
        components.append(f"{missing_ce:,} stores are missing CE promotors.")
    if blacklist_count:
        components.append(f"{blacklist_count:,} blacklist records were detected.")
    if duplicate_mobile:
        components.append(f"{duplicate_mobile:,} duplicate mobile records found.")
    if duplicate_nik:
        components.append(f"{duplicate_nik:,} duplicate NIK records found.")

    return " ".join(components)
