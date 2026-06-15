
"""
AI-Powered Classifier using OpenAI GPT or Google Gemini
========================================================
This replaces the rule-based classifier with a REAL AI brain.

Setup:
  Option A (OpenAI): pip install openai
  Option B (Gemini): pip install google-generativeai

  Then set your API key:
  export OPENAI_API_KEY="your-key-here"
  OR
  export GOOGLE_API_KEY="your-key-here"
"""

import os
import json

# ============================================================
# OPTION A: OpenAI GPT Classifier
# ============================================================

def classify_with_openai(document_text):
    """
    Uses OpenAI GPT to classify documents.
    Much smarter than rule-based — handles messy, incomplete documents!
    """
    from openai import OpenAI
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"""You are a document classification agent for Amazon Relay's 
identity verification system.

Classify this document into ONE of these categories:
- DRIVERS_LICENSE
- PASSPORT
- INSURANCE_CERTIFICATE
- COMPLIANCE_FORM
- VEHICLE_REGISTRATION

Also extract all key fields you can find.

Respond in this EXACT JSON format (no other text):
{{
    "document_type": "CATEGORY_NAME",
    "confidence": 95,
    "routing_action": "AUTO_APPROVE or HUMAN_REVIEW or REJECT",
    "extracted_fields": {{
        "field_name": "field_value"
    }},
    "reasoning": "Brief explanation"
}}

Rules for routing_action:
- confidence >= 90: "AUTO_APPROVE"
- confidence 70-89: "HUMAN_REVIEW"  
- confidence < 70: "REJECT"

Document to classify:
---
{document_text}
---"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Cheap and fast! ~$0.0001 per document
        messages=[
            {"role": "system", "content": "You are a document classification expert. Always respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,  # Low temperature = more consistent results
        max_tokens=500
    )
    
    # Parse the response
    result_text = response.choices[0].message.content
    result = json.loads(result_text)
    
    return result


# ============================================================
# OPTION B: Google Gemini Classifier (FREE!)
# ============================================================

def classify_with_gemini(document_text):
    """
    Uses Google Gemini to classify documents.
    FREE tier available — great for students/freshers!
    
    Get your free API key at: https://makersuite.google.com/app/apikey
    """
    import google.generativeai as genai
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')  # Fast and free!
    
    prompt = f"""You are a document classification agent for Amazon Relay's 
identity verification system.

Classify this document into ONE of these categories:
- DRIVERS_LICENSE
- PASSPORT
- INSURANCE_CERTIFICATE
- COMPLIANCE_FORM
- VEHICLE_REGISTRATION

Also extract all key fields you can find.

Respond in this EXACT JSON format (no other text):
{{
    "document_type": "CATEGORY_NAME",
    "confidence": 95,
    "routing_action": "AUTO_APPROVE or HUMAN_REVIEW or REJECT",
    "extracted_fields": {{
        "field_name": "field_value"
    }},
    "reasoning": "Brief explanation"
}}

Rules for routing_action:
- confidence >= 90: "AUTO_APPROVE"
- confidence 70-89: "HUMAN_REVIEW"  
- confidence < 70: "REJECT"

Document to classify:
---
{document_text}
---"""

    response = model.generate_content(prompt)
    
    # Clean and parse response
    result_text = response.text.strip()
    # Remove markdown code blocks if present
    if result_text.startswith("```"):
        result_text = result_text.split("```")[1]
        if result_text.startswith("json"):
            result_text = result_text[4:]
    
    result = json.loads(result_text)
    return result


# ============================================================
# OPTION C: LangChain Agent (Most Advanced - "Agentic AI")
# ============================================================

def classify_with_langchain_agent(document_text):
    """
    Uses LangChain to create a multi-step AGENT that:
    1. Classifies the document
    2. Validates the classification
    3. Extracts fields
    4. Checks for red flags
    5. Makes routing decision
    
    This is the "Agentic AI" approach mentioned in the job description!
    """
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.output_parsers import JsonOutputParser
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
    
    # STEP 1: Initial Classification
    classify_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a document type classifier. Respond with JSON only."),
        ("user", """Classify this document into one of: DRIVERS_LICENSE, PASSPORT, 
INSURANCE_CERTIFICATE, COMPLIANCE_FORM, VEHICLE_REGISTRATION.

Respond as: {{"document_type": "...", "confidence": 0-100, "reasoning": "..."}}

Document: {document}""")
    ])
    
    # STEP 2: Field Extraction (based on Step 1 result)
    extract_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a field extraction specialist. Respond with JSON only."),
        ("user", """This document is a {doc_type}. Extract all relevant fields.

Respond as: {{"extracted_fields": {{"field": "value", ...}}}}

Document: {document}""")
    ])
    
    # STEP 3: Red Flag Check
    validate_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a compliance validator. Check for issues."),
        ("user", """Check this {doc_type} for red flags:
- Expired documents
- Missing required fields
- Inconsistent information
- Suspicious patterns

Respond as: {{"red_flags": ["flag1", ...], "is_valid": true/false, "risk_level": "low/medium/high"}}

Document: {document}
Extracted fields: {fields}""")
    ])
    
    # Execute the agent pipeline
    # Step 1
    classify_chain = classify_prompt | llm
    classification = json.loads(
        classify_chain.invoke({"document": document_text}).content
    )
    
    # Step 2
    extract_chain = extract_prompt | llm
    extraction = json.loads(
        extract_chain.invoke({
            "doc_type": classification['document_type'],
            "document": document_text
        }).content
    )
    
    # Step 3
    validate_chain = validate_prompt | llm
    validation = json.loads(
        validate_chain.invoke({
            "doc_type": classification['document_type'],
            "document": document_text,
            "fields": json.dumps(extraction['extracted_fields'])
        }).content
    )
    
    # Final routing decision
    confidence = classification['confidence']
    if not validation.get('is_valid', True):
        confidence = min(confidence, 60)  # Lower confidence if red flags found
    
    if confidence >= 90:
        routing = "AUTO_APPROVE"
    elif confidence >= 70:
        routing = "HUMAN_REVIEW"
    else:
        routing = "REJECT"
    
    return {
        "document_type": classification['document_type'],
        "confidence": confidence,
        "routing_action": routing,
        "extracted_fields": extraction.get('extracted_fields', {}),
        "reasoning": classification.get('reasoning', ''),
        "red_flags": validation.get('red_flags', []),
        "risk_level": validation.get('risk_level', 'low')
    }


# ============================================================
# USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    sample_doc = """
    DRIVER'S LICENSE
    Full Name: John Smith
    License Number: DL-1234-5678-9012
    Date of Birth: 03/15/1990
    Expiry Date: 03/15/2028
    Class: A
    """
    
    print("Choose your AI backend:")
    print("1. OpenAI GPT (requires API key, ~$0.0001/doc)")
    print("2. Google Gemini (FREE tier available)")
    print("3. LangChain Agent (most advanced, requires OpenAI key)")
    print()
    
    # Uncomment the one you want to use:
    # result = classify_with_openai(sample_doc)
    # result = classify_with_gemini(sample_doc)
    # result = classify_with_langchain_agent(sample_doc)
    
    # print(json.dumps(result, indent=2))
    
    print("Set your API key and uncomment one of the functions above to test!")

