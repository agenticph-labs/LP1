#!/usr/bin/env python3
"""streamlit_ui.py — Web UI for the Client Intake & Project Scoping Pipeline.

Usage:
    streamlit run streamlit_ui.py
"""

from __future__ import annotations

import re
import uuid

import streamlit as st

# ── Reuse the pipeline module ──────────────────────────────────────────
from client_intake_pipeline import (
    ClientRecord,
    _render_markdown,
    classify,
    generate_scopes,
    output,
    validate,
)

st.set_page_config(
    page_title="Client Intake & Scoping",
    page_icon="📋",
    layout="wide",
)

# ── Helpers ────────────────────────────────────────────────────────────


def _run_pipeline_on_single(record: ClientRecord) -> str:
    """Run the full pipeline on a single ClientRecord and return the
    rendered markdown scope document."""
    records = [record]
    valid, errors = validate(records)
    if not valid:
        return f"**Validation error:** {errors[0]['error'] if errors else 'Unknown'}"
    classifications = classify(valid)
    scopes = generate_scopes(valid, classifications)
    # Write to disk so the output/ directory stays in sync
    output(scopes)
    return _render_markdown(scopes[0])


# ── Industry / Size pick-lists ────────────────────────────────────────

INDUSTRIES = [
    "Manufacturing",
    "Healthcare",
    "Finance / Insurance",
    "Retail / E-commerce",
    "Technology / SaaS",
    "Services / Consulting",
    "Education",
    "Real Estate / Construction",
    "Food & Beverage",
    "Non-profit",
    "Other",
]

SIZES = [
    "Solo (1 employee)",
    "Small (2–10 employees)",
    "Small (10–50 employees)",
    "Mid-size (50–100 employees)",
    "Mid-size (100–500 employees)",
    "Enterprise (500+ employees)",
]

# ── UI ─────────────────────────────────────────────────────────────────

st.title("📋 Client Intake & Project Scoping")
st.markdown("Enter client information below and generate a structured project scope document.")

# ── Demo data presets ──
SAMPLE_PRESETS = {
    "🔧 Acme Manufacturing (Digitization)": {
        "name": "Acme Manufacturing Corp",
        "industry": "Manufacturing",
        "size": "Enterprise (500+ employees)",
        "location": "Chicago, IL",
        "website": "https://acme-manufacturing.example.com",
        "need": "We need to digitize our supply chain tracking. Currently using spreadsheets "  # noqa: E501
        "and paper forms. Want real-time inventory visibility and automated purchase order generation.",  # noqa: E501
        "research_notes": "Competitors have adopted ERP solutions. Company has legacy "  # noqa: E501
        "mainframe systems. Budget estimated at $150K–$250K. IT team of 8.",
    },
    "🏥 BrightPath Healthcare (Patient Portal)": {
        "name": "BrightPath Healthcare",
        "industry": "Healthcare",
        "size": "Mid-size (100–500 employees)",
        "location": "Austin, TX",
        "website": "https://brightpath-health.example.com",
        "need": "Looking for a patient portal and appointment scheduling system integrated "  # noqa: E501
        "with their existing EHR. Need HIPAA compliance and mobile access.",
        "research_notes": "Currently using Athenahealth but want more customization. "  # noqa: E501
        "IT team of 5. Timeline 6–9 months. Budget $200K–$350K.",
    },
    "🪴 GreenLeaf Landscaping (Website + CRM)": {
        "name": "GreenLeaf Landscaping",
        "industry": "Services / Consulting",
        "size": "Small (10–50 employees)",
        "location": "Portland, OR",
        "website": "",
        "need": "Need a simple website with booking capability. Also want CRM for client "  # noqa: E501
        "management and automated follow-up emails after service visits.",
        "research_notes": "No current digital presence besides Google My Business. "  # noqa: E501
        "Budget under $30K. Owner wants something live in 2 months.",
    },
    "💰 Pinnacle Financial (KYC Automation)": {
        "name": "Pinnacle Financial Group",
        "industry": "Finance / Insurance",
        "size": "Mid-size (100–500 employees)",
        "location": "New York, NY",
        "website": "https://pinnacle-fin.example.com",
        "need": "We need to automate our client onboarding and KYC/AML compliance checks. "  # noqa: E501
        "Manual processes are slowing down account openings by 2–3 weeks.",
        "research_notes": "Regulated by SEC and FINRA. Current process uses PDF forms "  # noqa: E501
        "and email. Want integration with Clear and Onfido for identity verification. Budget $300K+.",  # noqa: E501
    },
    "🛍️ TidePool Retail (E-commerce)": {
        "name": "TidePool Retail",
        "industry": "Retail / E-commerce",
        "size": "Small (10–50 employees)",
        "location": "Santa Monica, CA",
        "website": "https://tidepool-retail.example.com",
        "need": "Want to build an e-commerce website with inventory management, payment processing, "  # noqa: E501
        "and shipping integration. Currently selling on Etsy only.",
        "research_notes": "Etsy store has 15K+ sales. Ready to move to own platform. "  # noqa: E501
        "Shopify vs custom build under evaluation. Budget $40K–$80K.",
    },
}

# Track selected preset globally
selected_preset = st.selectbox(
    "🎯 Quick Demo — Load a sample client",
    options=[""] + list(SAMPLE_PRESETS.keys()),
    help="Select a pre-built client profile to auto-fill the form below.",
)
preset = SAMPLE_PRESETS[selected_preset] if selected_preset else None

with st.form("intake_form"):
    col1, col2 = st.columns(2)

    with col1:
        # Pre-fill from preset if selected
        if selected_preset:
            name = st.text_input("Client Name *", value=preset["name"])
            _ind_idx = (INDUSTRIES.index(preset["industry"]) + 1
                       if preset["industry"] in INDUSTRIES else 0)
            industry = st.selectbox("Industry *", options=[""] + INDUSTRIES, index=_ind_idx)
            _sz_idx = SIZES.index(preset["size"]) + 1 if preset["size"] in SIZES else 0
            size = st.selectbox("Company Size *", options=[""] + SIZES, index=_sz_idx)
            location = st.text_input("Location", value=preset["location"])
        else:
            name = st.text_input("Client Name *", placeholder="e.g. Acme Manufacturing Corp")
            industry = st.selectbox("Industry *", options=[""] + INDUSTRIES)
            size = st.selectbox("Company Size *", options=[""] + SIZES)
            location = st.text_input("Location", placeholder="e.g. Chicago, IL")

    with col2:
        if selected_preset:
            website = st.text_input("Website", value=preset["website"])
            need = st.text_area("Client Need *", value=preset["need"], height=100)
            research_notes = st.text_area("Research Notes", value=preset["research_notes"],
                                        height=100)
        else:
            website = st.text_input("Website", placeholder="https://...")
            need = st.text_area("Client Need *",
                            placeholder="Describe the client's problem statement...",
                            height=100)
            research_notes = st.text_area("Research Notes",
                                    placeholder="Background, budget, competitors, timeline...",
                                    height=100)

    submitted = st.form_submit_button("🚀 Generate Scope Document",
                                type="primary", use_container_width=True)

# ── Auto-run if preset selected (on initial load via query param or first visit) ──
if submitted or (selected_preset and "auto_run" not in st.session_state):
    st.session_state.auto_run = True
    if not submitted and selected_preset:
        # First load with a preset — auto-submit
        st.rerun()

if submitted:
    missing = []
    if not name.strip():
        missing.append("Name")
    if not industry.strip():
        missing.append("Industry")
    if not size.strip():
        missing.append("Size")
    if not need.strip():
        missing.append("Need")

    if missing:
        st.error(f"Please fill in the following required field(s): {', '.join(missing)}")
    else:
        client_id = f"CLT-{uuid.uuid4().hex[:4].upper()}"
        record = ClientRecord(
            id=client_id,
            name=name.strip(),
            industry=industry.strip(),
            size=size.strip(),
            location=location.strip() or "TBD",
            website=website.strip() or "",
            need=need.strip(),
            research_notes=research_notes.strip() or "No research notes provided.",
        )

        with st.spinner("Running pipeline (ingest → validate → classify → scope → output)..."):
            markdown = _run_pipeline_on_single(record)

        st.success(f"Scope document generated! (Client ID: {client_id})")
        st.markdown("---")
        st.markdown(markdown)

        # ── Download button ──
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", record.name.lower().replace(" ", "_"))
        filename = f"{record.id}_{safe_name}.md"
        st.download_button(
            label="📥 Download Scope Document (.md)",
            data=markdown,
            file_name=filename,
            mime="text/markdown",
            use_container_width=True,
        )
