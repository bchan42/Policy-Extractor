from datetime import datetime
import time
import pandas as pd
from typing import List, Dict

import pdfplumber
import docx
import streamlit as st
import google.generativeai as genai
import io
import fitz


# 1. Configure Gemini API
GOOGLE_API_KEY = st.secrets['GOOGLE_API_KEY']
genai.configure(api_key=GOOGLE_API_KEY)
     

# 2. Extract text from uploaded document (pdf / docx / txt)

# Helper function to extract text from pdf using fitz:
# Increase gap_threshold for larger paragraph chunks
def extract_paragraphs_from_pdf(file_obj, gap_threshold=20):

    doc = fitz.open(stream=file_obj, filetype="pdf")
    paragraphs = []

    for page in doc:
        blocks = page.get_text("blocks")
        blocks = sorted(blocks, key=lambda b: (b[1], b[0]))  # sort by y, then x

        paragraph = ""
        last_bottom = None

        for b in blocks:
            text = b[4].strip()
            top = b[1]

            if not text:
                continue

            if last_bottom is not None and top - last_bottom > gap_threshold:
                if paragraph:
                    paragraphs.append(paragraph.strip())
                    paragraph = text
                else:
                    paragraph = text
            else:
                paragraph += " " + text if paragraph else text

            last_bottom = b[3]

        if paragraph:
            paragraphs.append(paragraph.strip())

    return paragraphs

# input: doc path
# output: list of paragraphs depending on format
def extract_text(doc: str) -> List[str]:

    para_chunks = []

    if doc.name.endswith(".pdf"):
        # with pdfplumber.open(doc) as pdf:
        #     for i, page in enumerate(pdf.pages):
        #         text = page.extract_text()
        #         if text:
        #             paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        #             para_chunks.extend(paragraphs)
        # Try fitz
        pdf_bytes = doc.read()
        pdf_obj = io.BytesIO(pdf_bytes)
        para_chunks = extract_paragraphs_from_pdf(pdf_obj)


    elif doc.name.endswith(".docx"):
        doc_obj = docx.Document(doc)
        para_chunks = [para.text.strip() for para in doc_obj.paragraphs if para.text.strip()]

    elif doc.name.endswith(".txt"):
        content = doc.read().decode()
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        para_chunks = paragraphs

    else:
        st.error("Unsupported file type.")
        st.stop()
    
    return para_chunks
     

# 3. Query Gemini with a text chunk

# input: a paragraph
# output: generated Gemini response
def query_gemini(text):

    model = genai.GenerativeModel(model_name="gemini-2.5-flash-lite")
    prompt = (
    f"""You’re a city planning policy expert. 
    Extract policies related to wildfire resilience and/or mitigation from this text. 
    A policy can be a rule, guideline, goal, or program. 
    Make sure each policy is concise and clearly separated by a new line. 
    If the policy is preceded by a number or label, please include the label in the extracted policy. 
    Do not include explanations, summaries, or additional text. If there are no policies, respond with: NONE. 
    \n{text}"""
    )

    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response else "No response"
    
    except Exception as e:
        return f"Error: {str(e)}"

     

# 4. Process document by paragraph chunks (Iterate thru each paragrpah)

# input: doc path
# output: dictionary of extracted policies
def process_document(doc):

    text_chunks = extract_text(doc)
    total_chunks = len(text_chunks)
    
    # Gemini rate limit: 15 QPM → 1 query every 4 seconds
    delay_per_chunk = 4.1  # Add slight buffer
    estimated_time_sec = total_chunks * delay_per_chunk
    estimated_time_min = estimated_time_sec / 60

    if total_chunks > 1500:
        st.warning("Too many chunks for daily limit (1500/day). Consider splitting the document into fewer paragraphs.")
        return {}

    st.info(f"Reading {total_chunks} paragraphs. Estimated processing time: ~{estimated_time_min:.1f} minutes.")

    # extracted_policies = {}

    # for i, para_text in enumerate(text_chunks):
    #     st.write(f"Processing chunk {i+1}/{total_chunks}...")

    #     extracted_policies[f"Chunk {i+1}"] = query_gemini(para_text)

    #     if i < total_chunks - 1:
    #         time.sleep(delay_per_chunk)

    results = []

    progress_bar = st.progress(0)
    progress_text = st.empty()

    for i, para_text in enumerate(text_chunks):
        progress_text.write(f"Processing paragraph {i + 1}/{total_chunks}...")
        policy = query_gemini(para_text)
        results.append({
            "Paragraph #": i + 1,
            "Paragraph Text": para_text.strip(),
            "Extracted Policy": policy.strip()
        })
        progress_bar.progress((i + 1) / total_chunks)
        if i < total_chunks - 1:
            time.sleep(delay_per_chunk)

    # for i, para_text in enumerate(text_chunks):
    #     st.write(f"Processing paragraph {i+1}/{total_chunks}...")
    #     policy = query_gemini(para_text)
    #     results.append({
    #         "Paragraph #": i + 1,
    #         "Paragraph Text": para_text.strip(),
    #         "Extracted Policy": policy.strip()
    #     })
    #     if i < total_chunks - 1:
    #         time.sleep(delay_per_chunk)

    return pd.DataFrame(results)



# 5. Convert to DataFrame

# input: dictionary of policies
# ouput: excel file
def save_to_excel(data):
    df = pd.DataFrame(data)  # your list of dicts

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='ExtractedPolicies')
        workbook  = writer.book
        worksheet = writer.sheets['ExtractedPolicies']

        # Format for wrapping text
        wrap_format = workbook.add_format({'text_wrap': True})

        # Max width (characters) for any column
        MAX_WIDTH = 60

        # Set column width and apply wrap format
        for i, col in enumerate(df.columns):
            # Calculate max length of column content + header
            max_len = min(max(df[col].astype(str).map(len).max(), len(col)) + 5, MAX_WIDTH)
            worksheet.set_column(i, i, max_len, wrap_format)

        # Optional: freeze header row
        worksheet.freeze_panes(1, 0)

    return output.getvalue()

