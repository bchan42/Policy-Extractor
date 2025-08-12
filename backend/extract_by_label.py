from datetime import datetime
import time
import pandas as pd
from typing import List, Dict

import pdfplumber
import docx
import streamlit as st
import google.generativeai as genai
import io
import pymupdf
import re

##################################################################
# 1. Configure Gemini API
GOOGLE_API_KEY = st.secrets['GOOGLE_API_KEY']
genai.configure(api_key=GOOGLE_API_KEY)

##################################################################
# 2. Extract text from uploaded document (pdf / docx / txt)

# This function extracts pages from pdfs
def extract_text_with_page_numbers(file_obj):
    doc = pymupdf.open(stream=file_obj, filetype="pdf")
    page_texts = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        page_texts.append({
            "page_num": page_num,
            "text": text
        })

    return page_texts

# This function cleans pages from pdfs
def clean_page_text(page_text):
    lines = page_text.splitlines()
    cleaned_lines = []

    for line in lines:
        # Remove page headers/footers:
        # - Lines like "Page II-28" or "Page 3" (case-insensitive)
        # - Lines that are just dates (simple YYYY or MM DD YYYY pattern)
        # - Lines that are empty or whitespace only
        if re.match(r"^\s*Page\s+[A-Z]*-?\d+\s*$", line, re.IGNORECASE):
            continue
        if re.match(r"^\s*\d{4}\s*$", line):  # just a year line
            continue
        if re.match(r"^\s*[A-Za-z]{3,9}\s+\d{1,2},\s*\d{4}\s*$", line):  # e.g. June 25, 2002
            continue
        if not line.strip():
            continue

        cleaned_lines.append(line.strip())

    # Merge lines that don't end with punctuation to avoid broken sentences
    merged_text = ""
    for i, line in enumerate(cleaned_lines):
        if i == len(cleaned_lines) - 1:
            merged_text += line
        else:
            if re.search(r"[.?!:]$", line):
                merged_text += line + "\n"
            else:
                merged_text += line + " "

    # Normalize spaces
    merged_text = re.sub(r"\s+", " ", merged_text)
    merged_text = re.sub(r" \n ", "\n", merged_text)

    return merged_text.strip()

# Clean all pages in pdf
def clean_all_pages(page_texts):
    cleaned_pages = []
    for page in page_texts:
        cleaned = clean_page_text(page["text"])
        cleaned_pages.append(cleaned)
    # Join all pages into one big text with double newlines between pages
    full_text = "\n\n".join(cleaned_pages)
    return full_text


# This function extracts text from different document types
def extract_text(doc: str) -> List[str]:

    chunks = []

    if doc.name.endswith(".pdf"):
        # with pdfplumber.open(doc) as pdf:
        #     for i, page in enumerate(pdf.pages):
        #         text = page.extract_text()
        #         if text:
        #             paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        #             para_chunks.extend(paragraphs)
        # Extract chunks by paragraph
        # pdf_bytes = doc.read()
        # pdf_obj = io.BytesIO(pdf_bytes)
        # para_chunks = extract_paragraphs_from_pdf(pdf_obj)

        # Extract chunks page-by-page
        pdf_bytes = doc.read()
        pdf_obj = io.BytesIO(pdf_bytes)

        # Step 1: Extract raw page texts
        page_texts = extract_text_with_page_numbers(pdf_obj)

        # Step 2: Clean pages individually and create cleaned chunks
        cleaned_chunks = []
        for page in page_texts:
            cleaned_text = clean_page_text(page["text"])
            if cleaned_text:  # skip empty pages
                cleaned_chunks.append((page["page_num"], cleaned_text))

        # chunks = [(page["page_number"], page["text"]) for page in page_texts if page["text"]]
        return cleaned_chunks


    elif doc.name.endswith(".docx"):
        doc_obj = docx.Document(doc)
        chunks = [para.text.strip() for para in doc_obj.paragraphs if para.text.strip()]
        return chunks

    elif doc.name.endswith(".txt"):
        content = doc.read().decode()
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        chunks = paragraphs
        return chunks

    else:
        st.error("Unsupported file type.")
        st.stop()

##################################################################
# 3. Find policy labels by doing a regex search

# Generate a regex string
def generate_broad_regex(s):
    parts = re.findall(r'\w+|\d+|[^\w\s]+|\s+', s)
    regex_parts = []
    for part in parts:
        if part.isspace():
            regex_parts.append(r'\s+')
        elif re.fullmatch(r'\d+(\.\d+)*', part):
            regex_parts.append(r'[\d\.]+')
        elif re.fullmatch(r'\w+', part):
            regex_parts.append(r'\w+')
        else:
            regex_parts.append(re.escape(part))
    return ''.join(regex_parts)

def find_policy_labels(text, label_patterns):
    combined_regex = '|'.join(generate_broad_regex(label) for label in label_patterns)
    pattern = re.compile(combined_regex, re.IGNORECASE)
    matches = pattern.findall(text)
    found_labels = sorted(set(match.strip() for match in matches))
    return found_labels

##################################################################
# 4. Query Gemini by defining a policy based on user input (policy labels)

def query_gemini_policy_labels(page_text, policy_labels):

    labels_list = '\n'.join(f"- {label}" for label in policy_labels)

    model = genai.GenerativeModel(model_name="gemini-2.5-flash-lite")

    prompt = f"""You are a city planning policy expert.
            The following page contains multiple policies. The policies are introduced
            by labels as defined in this list: {labels_list}

            Please extract each policy preceded by these labels. 
            Return the label along with the corresponding policy text.
            If no matching policies are found, output ONLY: NONE

            Page: {page_text}
            """
   
    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response else "No response"
    
    except Exception as e:
        return f"Error: {str(e)}"
    
##################################################################
# 5. Run the prompt on the document

def process_document_with_labels(doc, policy_labels):

    # Try extracting page-by-page
    text_chunks = extract_text_with_page_numbers(doc)
    page_chunks = [(p["page_num"], p["text"]) for p in text_chunks if p["text"]]
    total_chunks = len(text_chunks)
    
    # Gemini rate limit: 15 QPM → 1 query every 4 seconds
    delay_per_chunk = 4.1  # Add slight buffer
    estimated_time_sec = total_chunks * delay_per_chunk
    estimated_time_min = estimated_time_sec / 60

    if total_chunks > 1000:
        st.warning("Too many chunks for daily limit (1000/day). Consider splitting the document.")
        return {}

    # Trying to read in pages instead of paragraphs. Change to paragraphs if needed
    st.info(f"Reading {total_chunks} pages. Estimated processing time: ~{estimated_time_min:.1f} minutes.")

    results = []

    progress_bar = st.progress(0)
    progress_text = st.empty()

    # Change back to --> for i, para_text in enumerate(text_chunks) if you don't want to go page-by-page
    for i, (page_number,para_text) in enumerate(page_chunks):
        # Trying to read in pages instead of paragraphs. Change to paragraphs if needed
        progress_text.write(f"Processing page {i + 1}/{total_chunks}...")
        found_labels = find_policy_labels(para_text, policy_labels)
        if not found_labels:
            print("No policy labels found on this page.")
            continue
        policy = query_gemini_policy_labels(para_text, found_labels) 
        results.append({
            "Page #": page_number,
            "Page Text": para_text.strip(),
            "Extracted Policy": policy.strip()
        })
        progress_bar.progress((i + 1) / total_chunks)
        if i < total_chunks - 1:
            time.sleep(delay_per_chunk)

    return pd.DataFrame(results)

##################################################################
# END 