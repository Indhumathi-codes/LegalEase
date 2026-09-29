import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import os
from datetime import date

import requests
import streamlit as st
from dotenv import load_dotenv

from document_utils.formatters import (
    format_docx,
    format_html_preview,
    format_pdf,
    format_txt,
)

load_dotenv()


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CONFIG
# ============================================================

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>

    /* ================================
       MAIN PAGE
    ================================= */

    .stApp {
        background: #0e1117;
        color: #f5f5f5;
    }

    .main .block-container {
        max-width: 820px;
        padding-top: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
        padding-bottom: 3rem;
    }


    /* ================================
       LOGO
    ================================= */

    .logo-area {
        text-align: center;
        margin-top: -10px;
        margin-bottom: 4px;
    }


    /* ================================
       HEADER
    ================================= */

    .title {
        text-align: center;
        font-size: 1.55rem;
        font-weight: 600;
        color: #f5f5f5;
        margin-top: 0;
        margin-bottom: 4px;
    }

    .subtitle {
        text-align: center;
        font-size: 0.80rem;
        color: #9da3ae;
        margin-bottom: 25px;
    }


    /* ================================
       LABELS
    ================================= */

    label {
        color: #d8dbe1 !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
    }


    /* ================================
       SELECT BOX
    ================================= */

    div[data-baseweb="select"] > div {
        background-color: #191c24 !important;
        border: 1px solid #2c303a !important;
        border-radius: 6px !important;
        min-height: 38px !important;
        box-shadow: none !important;
    }

    div[data-baseweb="select"] span {
        color: #eeeeee !important;
        font-size: 0.80rem !important;
    }


    /* ================================
       TEXT INPUT
    ================================= */

    div[data-baseweb="input"] > div {
        background-color: #191c24 !important;
        border: 1px solid #2c303a !important;
        border-radius: 6px !important;
        min-height: 38px !important;
        box-shadow: none !important;
    }

    div[data-baseweb="input"] input {
        color: #eeeeee !important;
        font-size: 0.80rem !important;
    }


    /* ================================
       TEXT AREAS
    ================================= */

    textarea {
        background-color: #191c24 !important;
        color: #eeeeee !important;
        border: 1px solid #2c303a !important;
        border-radius: 6px !important;
        font-size: 0.80rem !important;
        line-height: 1.45 !important;
        box-shadow: none !important;
    }

    textarea:focus,
    input:focus {
        border-color: #3b82f6 !important;
        box-shadow: none !important;
    }

    textarea::placeholder,
    input::placeholder {
        color: #656b76 !important;
    }


    /* ================================
       DATE INPUT
    ================================= */

    div[data-testid="stDateInput"] > div > div {
        background-color: #191c24 !important;
        border: 1px solid #2c303a !important;
        border-radius: 6px !important;
    }

    div[data-testid="stDateInput"] input {
        background-color: #1a1c24 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 1px solid #444 !important;
    }


    /* ================================
       GENERATE BUTTON
    ================================= */

    div[data-testid="stFormSubmitButton"] button {
        background-color: #2563eb !important;
        color: white !important;
        border: 1px solid #2563eb !important;
        border-radius: 6px !important;
        font-size: 0.80rem !important;
        font-weight: 600 !important;
        min-height: 42px !important;
        box-shadow: none !important;
    }

    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #1d4ed8 !important;
        border-color: #1d4ed8 !important;
    }


    /* ================================
       ERROR / ALERT
    ================================= */

    div[data-testid="stAlert"] {
        border-radius: 6px !important;
        font-size: 0.78rem !important;
    }


    /* ================================
       SUCCESS MESSAGE
    ================================= */

    .success-message {
        background: #063b29;
        border: 1px solid #087f5b;
        border-radius: 6px;
        color: #7ff0bf;
        padding: 10px 14px;
        font-size: 0.78rem;
        margin-top: 18px;
        margin-bottom: 18px;
    }


    /* ================================
       DOCUMENT PREVIEW
    ================================= */

    .document-box {
        background: #11141c;
        border: 1px solid #292d37;
        border-radius: 7px;
        padding: 22px;
        margin-top: 10px;
    }

    .legal-preview {
        background: #11141c;
        color: #eeeeee;
        border: none;
        padding: 4px;
        line-height: 1.65;
        font-family: Georgia, serif;
        font-size: 0.90rem;
    }


    /* ================================
       DOWNLOAD BUTTONS
    ================================= */

    div[data-testid="stDownloadButton"] button {
        background-color: #191c24 !important;
        color: #dddddd !important;
        border: 1px solid #2c303a !important;
        border-radius: 6px !important;
        font-size: 0.75rem !important;
        box-shadow: none !important;
    }

    div[data-testid="stDownloadButton"] button:hover {
        background-color: #252934 !important;
        border-color: #3b82f6 !important;
    }


    /* ================================
       TABS
    ================================= */

    button[data-baseweb="tab"] {
        color: #8d929c !important;
        font-size: 0.78rem !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff !important;
    }


    /* ================================
       SUBHEADINGS
    ================================= */

    h2,
    h3 {
        color: #eeeeee !important;
    }


    /* ================================
       FOOTER
    ================================= */

    .footer {
        text-align: center;
        color: #555b66;
        font-size: 0.68rem;
        margin-top: 38px;
        padding-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOGO
# ============================================================

logo_path = PROJECT_ROOT / "assets" / "logo.png"

if logo_path.exists():
    try:
        left, center, right = st.columns([0.5, 2, 0.5])

        with center:
            st.image(
                str(logo_path),
                width=500,
            )

    except Exception:
        pass


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="title">
        AI Legal Document Generator
    </div>

    <div class="subtitle">
        Create professional legal document drafts using AI
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FORM
# ============================================================

with st.form("document_form"):

    document_type = st.selectbox(
        "Document Type",
        [
            "Freelance Work Contract",
            "Employment Contract",
            "Non-Disclosure Agreement (NDA)",
            "Lease Agreement",
            "Service Agreement",
            "General Agreement",
            "Custom",
        ],
    )

    if document_type == "Custom":
        document_type = st.text_input(
            "Custom Document Type",
            placeholder="Enter document type",
        )

    parties = st.text_area(
        "Parties involved",
        placeholder=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),
        height=90,
    )

    terms_text = st.text_area(
        "Terms & conditions",
        placeholder=(
            "Payment within 30 days of invoice;\n"
            "Confidentiality must be maintained;\n"
            "Either party may terminate with 15 days notice"
        ),
        height=140,
    )

    effective_date = st.date_input(
        "Effective Date",
        value=date.today(),
    )

    submitted = st.form_submit_button(
        "Generate Document",
        type="primary",
        use_container_width=True,
    )


# ============================================================
# GENERATE DOCUMENT
# ============================================================

if submitted:

    terms = [
        x.strip()
        for x in terms_text.replace(";", "\n").splitlines()
        if x.strip()
    ]

    if not parties.strip():

        st.error(
            "Please enter the parties involved."
        )

    elif not terms:

        st.error(
            "Please enter at least one term."
        )

    else:

        payload = {
            "document_type": document_type,
            "parties": parties.strip(),
            "terms": terms,
            "effective_date": effective_date.isoformat(),
            "jurisdiction": "Not specified",
            "additional_instructions": "",
        }

        try:

            with st.spinner(
                "Generating document..."
            ):

                response = requests.post(
                    f"{BACKEND_URL}/api/v1/generate",
                    json=payload,
                    timeout=120,
                )

            if response.ok:

                st.session_state.document = response.json()

                st.session_state.edited = (
                    st.session_state.document["content"]
                )

            else:

                try:
                    detail = (
                        response
                        .json()
                        .get(
                            "detail",
                            response.text,
                        )
                    )

                except Exception:
                    detail = response.text

                st.error(
                    f"Backend error "
                    f"({response.status_code}): "
                    f"{detail}"
                )

        except requests.RequestException as exc:

            st.error(
                f"Could not reach FastAPI backend "
                f"at {BACKEND_URL}.\n\n"
                f"Details: {exc}"
            )


# ============================================================
# GENERATED DOCUMENT
# ============================================================

if "document" in st.session_state:

    data = st.session_state.document

    st.markdown(
        """
        <div class="success-message">
            ✅ Document Generated Successfully!
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader(data["title"])

    preview_tab, edit_tab = st.tabs(
        [
            "📄 Preview",
            "✏️ Edit Document",
        ]
    )


    # ========================================================
    # PREVIEW
    # ========================================================

    with preview_tab:

        st.markdown(
            '<div class="document-box">',
            unsafe_allow_html=True,
        )

        st.markdown(
            format_html_preview(
                st.session_state.edited
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


    # ========================================================
    # EDIT
    # ========================================================

    with edit_tab:

        edited_text = st.text_area(
            "Edit the document",
            value=st.session_state.edited,
            height=600,
            key="document_editor",
        )

        st.session_state.edited = edited_text


    # ========================================================
    # DOWNLOADS
    # ========================================================

    st.subheader("Download")

    d1, d2, d3 = st.columns(3)

    edited = st.session_state.edited

    safe_name = "".join(
        ch.lower()
        if ch.isalnum()
        else "_"
        for ch in data["document_type"]
    ).strip("_") or "legal_document"


    with d1:

        st.download_button(
            "📄 Download as .TXT",
            data=format_txt(edited),
            file_name=f"{safe_name}.txt",
            mime="text/plain",
            use_container_width=True,
        )


    with d2:

        st.download_button(
            "📝 Download as .DOCX",
            data=format_docx(
                edited,
                data["document_type"],
            ),
            file_name=f"{safe_name}.docx",
            mime=(
                "application/"
                "vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            use_container_width=True,
        )


    with d3:

        st.download_button(
            "📕 Download as .PDF",
            data=format_pdf(
                edited,
                data["document_type"],
            ),
            file_name=f"{safe_name}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


    st.caption(data["disclaimer"])


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        LegalEase • AI-powered legal document drafting
    </div>
    """,
    unsafe_allow_html=True,
)
