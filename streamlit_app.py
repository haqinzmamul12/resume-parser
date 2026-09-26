# streamlit_app.py
"""Enhanced Streamlit UI for the Resume Parser.
It mirrors the FastAPI `/parse` pipeline but presents the extracted
information in a clean, card‑like layout instead of raw JSON.
"""

import streamlit as st
import tempfile
import os
import json

# Local imports – adjust if the script location changes
from modules.resume.unstructured import UnstructuredResumeParser
from modules.resume.extractor import ResumeExtractor
from modules.llm.model import extract_resume

# ---------------------------------------------------------------------------
# Page configuration & custom CSS for card‑style containers
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Resume Parser", layout="wide")

# Simple CSS to give a card look to containers
card_css = """
    .card {
        background: #f9f9f9;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        margin-top: 0.75rem;
        margin-bottom: 0.5rem;
    }
"""
st.markdown(f"<style>{card_css}</style>", unsafe_allow_html=True)

st.title("📄 Resume Parser")
st.caption("Upload a PDF resume to view the extracted information in a beautiful layout.")

uploaded_file = st.file_uploader("Choose a PDF resume", type=["pdf"])

if uploaded_file is not None:
    # ---------------------------------------------------------------
    # Save the uploaded PDF to a temporary file – required for the
    # existing extraction pipeline.
    # ---------------------------------------------------------------
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        temp_path = temp_file.name

    try:
        # ---------- Extraction pipeline --------------------------------
        extractor = ResumeExtractor(temp_path)
        image_paths = extractor.extract_images()
        parser = UnstructuredResumeParser(image_paths)
        extracted = parser.extract()
        markdown = "\n".join(item.get("markdown", "") for item in extracted)
        result = extract_resume(markdown)

        # ---------- Handle fallback raw_response ----------------------
        if isinstance(result, dict) and "raw_response" in result:
            try:
                result = json.loads(result["raw_response"])
            except Exception:
                st.error("Failed to parse the raw LLM response.")
                result = {}

        # ---------- Render sections -----------------------------------
        # Basic info (name, email, phone, linkedin, github)
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            col1.metric("Name", result.get("name") or "-")
            col2.metric("Email", result.get("email") or "-")
            col3.metric("Phone", result.get("phone") or "-")
            if result.get("linkedin"):
                st.markdown(f"**LinkedIn:** [{result['linkedin']}]({result['linkedin']})")
            if result.get("github"):
                st.markdown(f"**GitHub:** [{result['github']}]({result['github']})")
            st.markdown("</div>", unsafe_allow_html=True)

        # Address (if present)
        address = result.get("address")
        if address and any(address.values()):
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.subheader("Address")
                parts = [address.get("city"), address.get("state"), address.get("country"), address.get("pincode")]
                st.write(", ".join([p for p in parts if p]))
                st.markdown("</div>", unsafe_allow_html=True)

        # Skills
        skills = result.get("skills")
        if skills:
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.subheader("Skills")
                # Render each skill as a small badge
                badge_md = " ".join([f"`{skill}`" for skill in skills])
                st.markdown(badge_md)
                st.markdown("</div>", unsafe_allow_html=True)

        # Helper to render a list of objects (work, education, projects, certs)
        def render_list(title, items, field_order):
            if not items:
                return
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.subheader(title)
                for idx, entry in enumerate(items, 1):
                    st.markdown(f"**{idx}. {entry.get(field_order[0], '')}**")
                    for f in field_order[1:]:
                        val = entry.get(f)
                        if val:
                            # For dates we keep the raw string
                            st.markdown(f"- **{f.replace('_',' ').title()}:** {val}")
                    st.markdown("---")
                st.markdown("</div>", unsafe_allow_html=True)

        # Work Experience
        render_list(
            "Work Experience",
            result.get("work_experience"),
            ["company", "position", "start_date", "end_date"],
        )

        # Education
        render_list(
            "Education",
            result.get("education"),
            ["degree", "major", "institution", "start_date", "end_date"],
        )

        # Projects (now a single "date" field)
        render_list(
            "Projects",
            result.get("projects"),
            ["title", "description", "date"],
        )

        # Certifications
        render_list(
            "Certifications",
            result.get("certifications"),
            ["name", "issuing_organization", "issue_date", "expiry_date"],
        )

    except Exception as exc:
        st.error(f"An error occurred while parsing the resume: {exc}")
    finally:
        # Clean‑up temporary files regardless of success / failure
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if "image_paths" in locals():
            for img in image_paths:
                if os.path.exists(img):
                    os.remove(img)
else:
    st.info("Upload a PDF file to begin parsing.")
