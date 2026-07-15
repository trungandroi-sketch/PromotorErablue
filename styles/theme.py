import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
            :root {
                color-scheme: light;
                font-family: Inter, system-ui, sans-serif;
            }

            .stApp {
                background: #f2f5f8;
            }

            .dashboard-header {
                border-radius: 24px;
                padding: 24px 28px;
                background: #ffffff;
                box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
                margin-bottom: 20px;
            }

            .dash-title {
                margin: 0;
                font-size: 1.95rem;
                font-weight: 700;
                letter-spacing: -0.02em;
            }

            .dash-subtitle {
                margin: 8px 0 0;
                color: #475569;
                font-size: 0.95rem;
                line-height: 1.6;
            }

            .metric-card,
            .status-card,
            .insight-card,
            .blacklist-card,
            .filter-card,
            .export-card {
                background: #ffffff;
                border-radius: 20px;
                padding: 20px;
                box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
                border: 1px solid rgba(148, 163, 184, 0.12);
            }

            .metric-card:hover,
            .filter-card:hover,
            .blacklist-card:hover,
            .export-card:hover {
                box-shadow: 0 16px 32px rgba(15, 23, 42, 0.08);
            }

            .metric-title {
                font-size: 0.925rem;
                color: #475569;
                margin-bottom: 8px;
                font-weight: 600;
            }

            .metric-value {
                font-size: 2.3rem;
                font-weight: 700;
                margin-bottom: 4px;
                color: #0f172a;
            }

            .metric-note {
                font-size: 0.88rem;
                color: #64748b;
            }

            .card-label {
                color: #94a3b8;
                font-size: 0.85rem;
            }

            .section-title {
                font-size: 1.1rem;
                margin-bottom: 16px;
                color: #0f172a;
                font-weight: 700;
            }

            .section-subtitle {
                font-size: 0.95rem;
                color: #64748b;
                margin-bottom: 14px;
            }

            .alert-banner {
                border-radius: 18px;
                padding: 18px 22px;
                background: #fef3c7;
                color: #92400e;
                border: 1px solid #facc15;
            }

            .health-score {
                border-radius: 18px;
                padding: 20px;
                background: linear-gradient(90deg, #e0f2fe 0%, #eff6ff 100%);
                border: 1px solid rgba(59, 130, 246, 0.14);
            }

            .small-text {
                color: #64748b;
                font-size: 0.88rem;
            }

            .status-strip {
                border-radius: 16px;
                background: #ffffff;
                padding: 14px 18px;
                box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
                margin-bottom: 18px;
            }

            .status-pill {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                border-radius: 999px;
                padding: 8px 14px;
                font-size: 0.88rem;
                font-weight: 600;
            }

            .status-pill.connected {
                background: #dbeafe;
                color: #1d4ed8;
            }

            .status-pill.warning {
                background: #fef3c7;
                color: #92400e;
            }

            .status-pill.error {
                background: #fee2e2;
                color: #b91c1c;
            }

            .small-button {
                border-radius: 999px !important;
                padding: 0.65rem 1rem !important;
                font-weight: 700 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
