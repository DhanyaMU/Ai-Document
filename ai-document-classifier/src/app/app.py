

import streamlit as st
import re
import json
import time
import os
from datetime import datetime
from faker import Faker
import random
import pandas as pd

# Load environment variables (your API key)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

fake = Faker()

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="AI Document Classifier | Relay Product Excellence",
    page_icon="📄",
    layout="wide"
)

# ============================================================
# GEMINI AI SETUP
# ============================================================
GEMINI_AVAILABLE = False
genai = None

try:
    import google.generativeai as genai_module
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        genai_module.configure(api_key=api_key)
        genai = genai_module
        GEMINI_AVAILABLE = True
except ImportError:
    pass

# ============================================================
# EXTRACTION TEMPLATES
# ============================================================
EXTRACTION_TEMPLATES = {
    "DRIVERS_LICENSE": {
        "fields_to_extract": ["full_name", "license_number", "date_of_birth",
                              "expiry_date", "class", "address", "restrictions"],
        "key_indicators": ["driver's license", "dmv", "license number", "class",
                          "endorsements", "motor vehicle"]
    },
    "PASSPORT": {
        "fields_to_extract": ["full_name", "passport_number", "nationality",
                              "date_of_birth", "expiry_date", "issuing_authority"],
        "key_indicators": ["passport", "nationality", "machine readable zone",
                          "issuing authority", "department of state"]
    },
    "INSURANCE_CERTIFICATE": {
        "fields_to_extract": ["company_name", "policy_number", "insured_name",
                              "effective_date", "expiration_date", "coverage_amount"],
        "key_indicators": ["certificate of insurance", "policy number", "coverage",
                          "bodily injury", "property damage", "insured"]
    },
    "COMPLIANCE_FORM": {
        "fields_to_extract": ["carrier_name", "usdot_number", "mc_number",
                              "authority_status", "overall_rating", "safety_record"],
        "key_indicators": ["compliance", "fmcsa", "usdot", "mc number",
                          "operating authority", "safety record", "carrier"]
    },
    "VEHICLE_REGISTRATION": {
        "fields_to_extract": ["registration_number", "vin", "make", "model",
                              "year", "owner_name", "plate_number", "expiry_date"],
        "key_indicators": ["vehicle registration", "vin", "registration no",
                          "plate number", "gvwr", "fuel type"]
    }
}

# ============================================================
# GEMINI AI CLASSIFIER (The Real Brain!)
# ============================================================
def classify_with_gemini(document_text):
    """Uses Google Gemini AI to classify documents"""
    if not GEMINI_AVAILABLE:
        return None

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""You are a document classification agent for Amazon Relay's identity verification system.

Your job:
1. Classify the document into EXACTLY one of these categories:
   - DRIVERS_LICENSE
   - PASSPORT
   - INSURANCE_CERTIFICATE
   - COMPLIANCE_FORM
   - VEHICLE_REGISTRATION

2. Extract all key fields you can find.

3. Provide a confidence score (0-100).

4. Determine routing action:
   - confidence >= 90: "AUTO_APPROVE"
   - confidence 70-89: "HUMAN_REVIEW"
   - confidence < 70: "REJECT"

5. Check for any red flags (expired documents, missing info, inconsistencies).

RESPOND WITH ONLY VALID JSON, NO OTHER TEXT:
{{
    "document_type": "CATEGORY_NAME",
    "confidence": 95,
    "routing_action": "AUTO_APPROVE",
    "extracted_fields": {{
        "field_name": "field_value"
    }},
    "reasoning": "Brief explanation of classification",
    "red_flags": []
}}

Here is the document to classify:
---
{document_text}
---"""

        response = model.generate_content(prompt)
        result_text = response.text.strip()

        # Clean up response - remove markdown code blocks if present
        if result_text.startswith("```"):
            lines = result_text.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            result_text = "\n".join(lines)

        result = json.loads(result_text)
        result['method'] = 'GEMINI AI'
        return result

    except Exception as e:
        st.warning(f"Gemini AI error: {str(e)}. Falling back to rule-based classifier.")
        return None


# ============================================================
# RULE-BASED CLASSIFIER (Backup)
# ============================================================
def classify_rule_based(document_text):
    """Classifies document using keyword matching (backup method)"""
    text_lower = document_text.lower()
    scores = {}

    for doc_type, template in EXTRACTION_TEMPLATES.items():
        score = 0
        matched_keywords = []
        for keyword in template['key_indicators']:
            if keyword.lower() in text_lower:
                score += 1
                matched_keywords.append(keyword)
        scores[doc_type] = {
            "score": score,
            "total_keywords": len(template['key_indicators']),
            "matched": matched_keywords
        }

    best_type = max(scores, key=lambda x: scores[x]['score'])
    best_score = scores[best_type]['score']
    total_possible = scores[best_type]['total_keywords']
    confidence = min(int((best_score / total_possible) * 100), 99)

    if confidence >= 90:
        routing = "AUTO_APPROVE"
    elif confidence >= 70:
        routing = "HUMAN_REVIEW"
    else:
        routing = "REJECT"

    return {
        "document_type": best_type,
        "confidence": confidence,
        "routing_action": routing,
        "matched_keywords": scores[best_type]['matched'],
        "all_scores": {k: v['score'] for k, v in scores.items()},
        "extracted_fields": extract_fields_regex(document_text, best_type),
        "reasoning": f"Matched {best_score}/{total_possible} keywords for {best_type}",
        "red_flags": [],
        "method": "RULE-BASED"
    }


# ============================================================
# FIELD EXTRACTOR (Regex-based)
# ============================================================
def extract_fields_regex(document_text, document_type):
    """Extracts key fields using regex patterns"""
    extracted = {}
    text = document_text.strip()

    patterns = {
        "DRIVERS_LICENSE": {
            "full_name": r"Full Name:\s*(.+)",
            "license_number": r"License Number:\s*(.+)",
            "date_of_birth": r"Date of Birth:\s*(.+)",
            "expiry_date": r"Expiry Date:\s*(.+)",
            "class": r"Class:\s*(.+)",
            "address": r"Address:\s*(.+)",
            "restrictions": r"Restrictions:\s*(.+)"
        },
        "PASSPORT": {
            "surname": r"Surname:\s*(.+)",
            "given_names": r"Given Names:\s*(.+)",
            "passport_number": r"Passport No:\s*(.+)",
            "nationality": r"Nationality:\s*(.+)",
            "date_of_birth": r"Date of Birth:\s*(.+)",
            "date_of_expiry": r"Date of Expiry:\s*(.+)",
            "issuing_authority": r"Issuing Authority:\s*(.+)"
        },
        "INSURANCE_CERTIFICATE": {
            "insurance_company": r"Insurance Company:\s*(.+)",
            "policy_number": r"Policy Number:\s*(.+)",
            "insured_name": r"Name:\s*(.+)",
            "effective_date": r"Effective Date:\s*(.+)",
            "expiration_date": r"Expiration Date:\s*(.+)",
            "vehicles_covered": r"VEHICLES COVERED:\s*(.+)",
            "drivers_covered": r"DRIVERS COVERED:\s*(.+)"
        },
        "COMPLIANCE_FORM": {
            "carrier_name": r"Carrier Name:\s*(.+)",
            "usdot_number": r"USDOT Number:\s*(.+)",
            "mc_number": r"MC Number:\s*(.+)",
            "authority_type": r"Authority Type:\s*(.+)",
            "authority_status": r"Authority Status:\s*(.+)",
            "overall_rating": r"Overall Rating:\s*(.+)",
            "out_of_service_rate": r"Out-of-Service Rate:\s*(.+)"
        },
        "VEHICLE_REGISTRATION": {
            "registration_number": r"Registration No:\s*(.+)",
            "vin": r"VIN:\s*(.+)",
            "year": r"Year:\s*(.+)",
            "make": r"Make:\s*(.+)",
            "model": r"Model:\s*(.+)",
            "owner_name": r"Name:\s*(.+)",
            "plate_number": r"Plate Number:\s*(.+)",
            "state": r"State:\s*(.+)"
        }
    }

    if document_type in patterns:
        for field_name, pattern in patterns[document_type].items():
            match = re.search(pattern, text)
            if match:
                extracted[field_name] = match.group(1).strip()
            else:
                extracted[field_name] = None

    return extracted


# ============================================================
# MAIN CLASSIFY FUNCTION
# ============================================================
def classify_document(document_text, use_ai=True):
    """Tries Gemini AI first, falls back to rule-based if unavailable."""
    if use_ai and GEMINI_AVAILABLE:
        result = classify_with_gemini(document_text)
        if result:
            return result

    # Fallback to rule-based
    return classify_rule_based(document_text)


# ============================================================
# SAMPLE DOCUMENT GENERATORS
# ============================================================
def generate_sample_document(doc_type):
    """Generates a sample document for testing"""
    if doc_type == "Driver's License":
        name = fake.name()
        return f"""
-------------------------------------------
      STATE DEPARTMENT OF MOTOR VEHICLES
           DRIVER'S LICENSE
-------------------------------------------

Full Name:        {name}
License Number:   DL-{fake.bothify('####-####-####')}
Date of Birth:    {fake.date_of_birth(minimum_age=18, maximum_age=65).strftime('%m/%d/%Y')}
Address:          {fake.address().replace(chr(10), ', ')}

Issue Date:       {fake.date_between(start_date='-5y', end_date='-1y').strftime('%m/%d/%Y')}
Expiry Date:      {fake.date_between(start_date='+1y', end_date='+5y').strftime('%m/%d/%Y')}

Class:            {random.choice(['A', 'B', 'C', 'D'])}
Restrictions:     {random.choice(['None', 'Corrective Lenses', 'Daylight Only'])}
Endorsements:     {random.choice(['None', 'Hazmat', 'Tanker', 'Double/Triple'])}

Sex:              {random.choice(['M', 'F'])}
Height:           {random.randint(5,6)}'{random.randint(0,11)}"
Eye Color:        {random.choice(['BRN', 'BLU', 'GRN', 'HZL'])}

-------------------------------------------
This license is property of the State DMV.
Must be carried while operating a motor vehicle.
-------------------------------------------
"""
    elif doc_type == "Passport":
        name = fake.name()
        return f"""
+--------------------------------------+
|         UNITED STATES OF AMERICA      |
|              PASSPORT                  |
+--------------------------------------+

Surname:          {name.split()[-1].upper()}
Given Names:      {name.split()[0].upper()}
Nationality:      {fake.country()}

Passport No:      {fake.bothify('??#######').upper()}
Date of Birth:    {fake.date_of_birth(minimum_age=18, maximum_age=70).strftime('%d %b %Y')}
Sex:              {random.choice(['M', 'F'])}
Place of Birth:   {fake.city()}, {fake.state()}

Date of Issue:    {fake.date_between(start_date='-8y', end_date='-1y').strftime('%d %b %Y')}
Date of Expiry:   {fake.date_between(start_date='+1y', end_date='+8y').strftime('%d %b %Y')}
Issuing Authority: U.S. Department of State

Machine Readable Zone:
P<USA{name.split()[-1].upper()}<<{name.split()[0].upper()}<<<<<<<<<<<<<<<

+--------------------------------------+
|  This document is government property |
+--------------------------------------+
"""
    elif doc_type == "Insurance Certificate":
        company = fake.company()
        return f"""
+--------------------------------------+
|     CERTIFICATE OF INSURANCE          |
|     Commercial Auto Policy            |
+--------------------------------------+

Insurance Company:    {random.choice(['State Farm', 'GEICO', 'Progressive', 'Allstate'])}
Policy Number:        POL-{fake.bothify('###-###-####')}

NAMED INSURED:
Name:                 {company}
DBA:                  {company} Trucking LLC
Address:              {fake.address().replace(chr(10), ', ')}

POLICY PERIOD:
Effective Date:       {fake.date_between(start_date='-1y', end_date='-1m').strftime('%m/%d/%Y')}
Expiration Date:      {fake.date_between(start_date='+1m', end_date='+1y').strftime('%m/%d/%Y')}

COVERAGES:
- Bodily Injury:        ${random.choice(['500,000', '1,000,000'])} per occurrence
- Property Damage:      ${random.choice(['100,000', '250,000'])} per occurrence
- Cargo Coverage:       ${random.choice(['50,000', '100,000'])}
- Combined Single Limit: ${random.choice(['1,000,000', '2,000,000'])}

VEHICLES COVERED:       {random.randint(1, 25)} vehicles
DRIVERS COVERED:        {random.randint(1, 40)} drivers

Certificate Holder:     Amazon Relay Transportation
"""
    elif doc_type == "Compliance Form":
        company = fake.company()
        return f"""
==========================================
FEDERAL MOTOR CARRIER SAFETY ADMINISTRATION
CARRIER COMPLIANCE VERIFICATION FORM
==========================================

SECTION A: CARRIER INFORMATION
-----------------------------------------
Carrier Name:         {company}
USDOT Number:         {fake.bothify('#######')}
MC Number:            MC-{fake.bothify('######')}
EIN:                  {fake.bothify('##-#######')}

SECTION B: OPERATING AUTHORITY
-----------------------------------------
Authority Type:       {random.choice(['Common', 'Contract', 'Broker'])}
Authority Status:     {random.choice(['Active', 'Active - Conditional'])}
Interstate:           {random.choice(['Yes', 'No'])}

SECTION C: SAFETY RECORD
-----------------------------------------
Total Inspections (12 mo):    {random.randint(5, 100)}
Out-of-Service Rate:          {random.uniform(0, 35):.1f}%
Crash Rate (per million mi):  {random.uniform(0, 3):.2f}
Driver Fitness Violations:    {random.randint(0, 15)}
HOS Violations:               {random.randint(0, 25)}

SECTION D: COMPLIANCE STATUS
-----------------------------------------
Overall Rating:       {random.choice(['Satisfactory', 'Conditional', 'Unsatisfactory'])}
Last Review Date:     {fake.date_between(start_date='-2y', end_date='-1m').strftime('%m/%d/%Y')}
Next Review Due:      {fake.date_between(start_date='+1m', end_date='+1y').strftime('%m/%d/%Y')}
==========================================
"""
    else:  # Vehicle Registration
        return f"""
+--------------------------------------+
|    DEPARTMENT OF MOTOR VEHICLES        |
|    VEHICLE REGISTRATION CERTIFICATE    |
+--------------------------------------+

Registration No:      {fake.bothify('???-####').upper()}
VIN:                  {fake.bothify('#?#??##?#??######').upper()}

VEHICLE INFORMATION:
- Year:             {random.randint(2018, 2025)}
- Make:             {random.choice(['Freightliner', 'Kenworth', 'Peterbilt', 'Volvo'])}
- Model:            {random.choice(['Cascadia', 'T680', '579', 'VNL'])}
- Type:             {random.choice(['Tractor', 'Straight Truck', 'Semi-Trailer'])}
- Color:            {random.choice(['White', 'Black', 'Silver', 'Red'])}
- GVWR:             {random.choice(['26,001', '33,000', '80,000'])} lbs
- Fuel Type:        {random.choice(['Diesel', 'CNG', 'Electric'])}

REGISTERED OWNER:
Name:                 {fake.company()} Trucking Inc.
Address:              {fake.address().replace(chr(10), ', ')}

REGISTRATION PERIOD:
Effective:            {fake.date_between(start_date='-1y', end_date='-1m').strftime('%m/%d/%Y')}
Expires:              {fake.date_between(start_date='+1m', end_date='+1y').strftime('%m/%d/%Y')}

Plate Number:         {fake.bothify('???-####').upper()}
State:                {fake.state()}

+--------------------------------------+
|  VALID ONLY WITH CURRENT PLATES       |
+--------------------------------------+
"""


# ============================================================
# STREAMLIT APP UI
# ============================================================

# --- HEADER ---
st.title("AI Document Classifier")
st.markdown("**Relay Product Excellence | Identity Verification System**")

# Show AI status
if GEMINI_AVAILABLE:
    st.success("Gemini AI is connected and ready!")
else:
    st.warning("Gemini AI not connected. Using rule-based classifier. Add your API key to .env file to enable AI.")

st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Settings")

    use_ai = st.toggle("Use Gemini AI", value=True, disabled=not GEMINI_AVAILABLE)

    confidence_threshold_high = st.slider(
        "Auto-Approve Threshold (%)", 80, 99, 90
    )
    confidence_threshold_low = st.slider(
        "Reject Threshold (%)", 30, 79, 70
    )

    st.markdown("---")
    st.header("Session Stats")

    if 'history' not in st.session_state:
        st.session_state.history = []

    total = len(st.session_state.history)
    auto_approved = sum(1 for h in st.session_state.history if h['routing'] == 'AUTO_APPROVE')
    human_review = sum(1 for h in st.session_state.history if h['routing'] == 'HUMAN_REVIEW')
    rejected = sum(1 for h in st.session_state.history if h['routing'] == 'REJECT')

    st.metric("Total Processed", total)
    col1, col2, col3 = st.columns(3)
    col1.metric("Auto", auto_approved)
    col2.metric("Review", human_review)
    col3.metric("Reject", rejected)

    if total > 0:
        st.metric("Auto-Approval Rate", f"{auto_approved/total*100:.0f}%")

    st.markdown("---")
    st.header("AI Method")
    if GEMINI_AVAILABLE and use_ai:
        st.info("Using: Gemini 2.5 Flash AI")
    else:
        st.info("Using: Rule-Based (Keyword Matching)")

# --- MAIN CONTENT ---
tab1, tab2, tab3 = st.tabs(["Classify Document", "Test with Samples", "History"])

# --- TAB 1: CLASSIFY ---
with tab1:
    st.subheader("Upload or Paste a Document")

    input_method = st.radio(
        "Choose input method:",
        ["Paste Text", "Upload File"],
        horizontal=True
    )

    document_text = ""

    if input_method == "Paste Text":
        document_text = st.text_area(
            "Paste your document content here:",
            height=300,
            placeholder="Paste the text content of your document here..."
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload a document (.txt, .pdf, .csv)",
            type=['txt', 'pdf', 'csv']
        )
        if uploaded_file:
            if uploaded_file.name.endswith('.txt') or uploaded_file.name.endswith('.csv'):
                document_text = uploaded_file.read().decode('utf-8')
            elif uploaded_file.name.endswith('.pdf'):
                try:
                    from PyPDF2 import PdfReader
                    import io
                    pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
                    document_text = ""
                    for page in pdf_reader.pages:
                        document_text += page.extract_text() + " "
                except Exception as e:
                    st.error(f"Error reading PDF: {e}")
                    document_text = ""
            st.text_area("File Content:", document_text, height=200, disabled=True)

    if st.button("Classify Document", type="primary", use_container_width=True):
        if document_text.strip():
            with st.spinner("AI is analyzing the document..."):
                start_time = time.time()
                result = classify_document(document_text, use_ai=use_ai)
                processing_time = time.time() - start_time

            # --- RESULTS ---
            st.markdown("---")
            st.subheader("Classification Results")

            # Method badge
            method = result.get('method', 'UNKNOWN')
            if method == 'GEMINI AI':
                st.caption("Classified by: Gemini 2.5 Flash AI")
            else:
                st.caption("Classified by: Rule-Based Engine")

            # Top metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Document Type", result['document_type'].replace('_', ' ').title())
            with col2:
                st.metric("Confidence", f"{result['confidence']}%")
            with col3:
                st.metric("Routing", result['routing_action'].replace('_', ' '))
            with col4:
                st.metric("Processing Time", f"{processing_time:.2f}s")

            # Confidence bar
            st.progress(result['confidence'] / 100)

            # Routing explanation
            if result['routing_action'] == "AUTO_APPROVE":
                st.success("HIGH CONFIDENCE - Document auto-approved for processing.")
            elif result['routing_action'] == "HUMAN_REVIEW":
                st.warning("MEDIUM CONFIDENCE - Routed to human reviewer for verification.")
            else:
                st.error("LOW CONFIDENCE - Document rejected. Please re-upload a clearer version.")

            # AI Reasoning
            if result.get('reasoning'):
                st.subheader("AI Reasoning")
                st.info(result['reasoning'])

            # Red Flags
            if result.get('red_flags') and len(result['red_flags']) > 0:
                st.subheader("Red Flags Detected")
                for flag in result['red_flags']:
                    st.error(f"- {flag}")

            # Extracted fields
            st.subheader("Extracted Fields")
            fields = result.get('extracted_fields', {})
            if fields:
                fields_data = []
                for k, v in fields.items():
                    if v is not None:
                        fields_data.append({
                            "Field": k.replace('_', ' ').title(),
                            "Value": str(v)
                        })
                if fields_data:
                    fields_df = pd.DataFrame(fields_data)
                    st.table(fields_df)
                else:
                    st.write("No fields extracted.")
            else:
                st.write("No fields extracted.")

            # Save to history
            st.session_state.history.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": result['document_type'],
                "confidence": result['confidence'],
                "routing": result['routing_action'],
                "method": method,
                "processing_time": f"{processing_time:.2f}s",
                "fields_extracted": len([v for v in fields.values() if v]) if fields else 0
            })
        else:
            st.error("Please paste or upload a document first!")

# --- TAB 2: TEST WITH SAMPLES ---
with tab2:
    st.subheader("Generate and Test Sample Documents")
    st.markdown("Click a button to generate a random document and classify it instantly!")

    doc_types = ["Driver's License", "Passport", "Insurance Certificate",
                 "Compliance Form", "Vehicle Registration"]

    selected_type = st.selectbox("Select document type to generate:", doc_types)

    if st.button("Generate and Classify", type="primary", use_container_width=True):
        sample = generate_sample_document(selected_type)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Generated Document")
            st.text_area("Document Content:", sample, height=400, disabled=True)

        with col2:
            st.subheader("Classification Result")

            with st.spinner("AI is classifying..."):
                start_time = time.time()
                result = classify_document(sample, use_ai=use_ai)
                processing_time = time.time() - start_time

            # Method badge
            method = result.get('method', 'UNKNOWN')
            if method == 'GEMINI AI':
                st.caption("Classified by: Gemini 2.5 Flash AI")
            else:
                st.caption("Classified by: Rule-Based Engine")

            st.metric("Type", result['document_type'].replace('_', ' ').title())
            st.metric("Confidence", f"{result['confidence']}%")
            st.metric("Time", f"{processing_time:.2f}s")
            st.progress(result['confidence'] / 100)

            if result['routing_action'] == "AUTO_APPROVE":
                st.success("Routing: AUTO APPROVE")
            elif result['routing_action'] == "HUMAN_REVIEW":
                st.warning("Routing: HUMAN REVIEW")
            else:
                st.error("Routing: REJECT")

            # AI Reasoning
            if result.get('reasoning'):
                st.markdown("**AI Reasoning:**")
                st.info(result['reasoning'])

            # Red Flags
            if result.get('red_flags') and len(result['red_flags']) > 0:
                st.markdown("**Red Flags:**")
                for flag in result['red_flags']:
                    st.error(f"- {flag}")

            # Extracted Fields
            st.markdown("**Extracted Fields:**")
            fields = result.get('extracted_fields', {})
            if fields:
                for k, v in fields.items():
                    if v:
                        st.write(f"- **{k.replace('_', ' ').title()}**: {v}")

            # Save to history
            st.session_state.history.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": result['document_type'],
                "confidence": result['confidence'],
                "routing": result['routing_action'],
                "method": method,
                "processing_time": f"{processing_time:.2f}s",
                "fields_extracted": len([v for v in fields.values() if v]) if fields else 0
            })

# --- TAB 3: HISTORY ---
with tab3:
    st.subheader("Classification History")

    if st.session_state.history:
        history_df = pd.DataFrame(st.session_state.history)
        st.dataframe(history_df, use_container_width=True)

        # Summary stats
        st.markdown("---")
        st.subheader("Performance Summary")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Documents", len(history_df))
        with col2:
            st.metric("Avg Confidence", f"{history_df['confidence'].mean():.1f}%")
        with col3:
            auto_rate = (history_df['routing'] == 'AUTO_APPROVE').mean() * 100
            st.metric("Auto-Approval Rate", f"{auto_rate:.0f}%")
        with col4:
            ai_rate = (history_df['method'] == 'GEMINI AI').mean() * 100
            st.metric("AI-Powered Rate", f"{ai_rate:.0f}%")

        if st.button("Clear History"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("No documents classified yet. Go to 'Classify Document' tab to start!")

# --- FOOTER ---
st.markdown("---")
st.markdown(
    "Built by **Dhanya** | Relay Product Excellence Portfolio Project | "
    "Powered by Python + Streamlit + Google Gemini AI"
)
