import os
import pdfplumber
from groq import Groq
from dotenv import load_dotenv
import streamlit as st

# Load API key
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# -----------------------------
# PDF TEXT EXTRACTION
# -----------------------------
def extract_text(uploaded_file, max_chars=3000):
    text = ""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        text = text.replace("\n", " ").strip()
        return text[:max_chars] if text else "Not Available"

    except Exception as e:
        return f"Error: {str(e)}"


# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="AI DDR Generator", layout="wide")

st.title("🏗️ AI DDR Report Generator")
st.markdown("Upload inspection and thermal reports to generate a professional DDR.")

inspection_file = st.file_uploader("📄 Upload Inspection PDF", type=["pdf"])
thermal_file = st.file_uploader("🌡️ Upload Thermal PDF (Optional)", type=["pdf"])

if st.button("🚀 Generate DDR Report"):

    if not inspection_file:
        st.error("Please upload inspection report.")
    else:
        with st.spinner("Processing..."):

            inspection_text = extract_text(inspection_file)
            thermal_text = extract_text(thermal_file, 1000) if thermal_file else "Not Available"

            # Confidence Score Logic
            confidence = 50
            if inspection_text != "Not Available":
                confidence += 30
            if thermal_text != "Not Available":
                confidence += 20

            # PROMPT
            prompt = f"""
You are an expert civil engineering inspection assistant.

Generate a professional Detailed Defect Report (DDR).

Inspection Data:
{inspection_text}

Thermal Data:
{thermal_text}

Rules:
- Do NOT assume anything
- Missing data → "Not Available"
- Use structured format

Include:

1. Executive Summary
2. Overview
3. Inspection Findings
4. Thermal Analysis
5. Defects Identified (with IDs)
6. Risk Assessment (Severity + Likelihood)
7. Recommendations

Also include:
- AI Confidence Score: {confidence}%
"""

            # AI CALL
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": "You generate professional engineering reports."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            result = response.choices[0].message.content

            # Add AI note
            final_output = f"""
DETAILED DEFECT REPORT (DDR)

This report is generated using AI-assisted analysis.

AI Confidence Score: {confidence}%

{result}
"""

            # DISPLAY
            st.success("✅ Report Generated!")
            st.markdown(final_output)

            # DOWNLOAD
            st.download_button(
                label="📥 Download Report",
                data=final_output,
                file_name="DDR_Report.txt",
                mime="text/plain"
            )