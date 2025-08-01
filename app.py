import streamlit as st
import google.generativeai as genai
import google.ai.generativelanguage as glm
import os
import PIL 
import io
import pdfplumber
import docx
import pandas as pd


GOOGLE_API_KEY= st.secrets['GOOGLE_API_KEY']

genai.configure(api_key=GOOGLE_API_KEY)

# model config
generation_config = {
"temperature": 0.9,
"top_p": 1,
"top_k": 1,
"max_output_tokens": 2048,
}

safety_settings = [
{
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_ONLY_HIGH"
},
{
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_ONLY_HIGH"
},
{
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_ONLY_HIGH"
},
{
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_ONLY_HIGH"
},
]

st.set_page_config(page_title="Gemini-ChatBot", layout = 'wide')

st.title('Gemini-ChatBot')
st.markdown("""
Welcome to Gemini-ChatBot! This interactive chatbot is powered by Google's generative AI.
Feel free to ask anything and enjoy the conversation!
""")

# Using "with" notation
with st.sidebar:
    st.title('Type of input:')
    add_radio = st.radio(
        "Type of input",
        ("Text ✏", "Document 📄"),
        key = 'input_param',
        label_visibility='collapsed'
    )

# Initialize previous_input_type in session_state if it doesn't exist
if "previous_input_type" not in st.session_state:
    st.session_state.previous_input_type = None

# Check if the input type has changed
if st.session_state.previous_input_type != add_radio:
    # Clear the messages
    st.session_state.messages = []
    # Update previous_input_type
    st.session_state.previous_input_type = add_radio

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["parts"][0])


if add_radio == 'Text ✏':
    model = genai.GenerativeModel(model_name="gemini-pro",
                                generation_config=generation_config,
                                safety_settings=safety_settings)
    prompt = st.chat_input("Ask anything")

    if prompt:
        message = prompt
        st.session_state.messages.append({
            "role":"user",
            "parts":[message],
        })
        with st.chat_message("user"):
            st.markdown(prompt)
        response = model.generate_content(st.session_state.messages)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown(response.text)
        st.session_state.messages.append({
            "role":"model",
            "parts":[response.text],
        })

elif add_radio == 'Document 📄':
    st.warning("Please upload a planning document ", icon="🤖")
    model = genai.GenerativeModel('gemini-pro',
                                generation_config=generation_config,
                                safety_settings=safety_settings)

    doc = st.file_uploader("Upload a planning document", type=["pdf", "docx", "txt"])
    # prompt = st.chat_input("Ask a question or extract policies")
    extract_button = st.button("🧠 Extract Policies")


    if doc and extract_button:

        # extract text from given file type (pdf / docx / txt)
        if doc.name.endswith(".pdf"):
            with pdfplumber.open(doc) as pdf:
                doc_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

        elif doc.name.endswith(".docx"):
            docum = docx.Document(doc)
            doc_text = "\n".join([para.text for para in docum.paragraphs])
        
        elif doc.name.endswith(".txt"):
            doc_text = doc.read().decode()

        else:
            st.error("Unsupported file type.")
            st.stop()

        # figure out chunking
        if len(doc) > 10000:
            st.warning("Document is too long — only the first 10,000 characters will be analyzed.")
            doc_text = doc_text[:10000]

        full_prompt = f"""You're a city planning policy expert. The user uploaded a planning document.

                        Extract and list all city planning **policies** mentioned in this document in the following format:

                        Policy Number, Policy Description

                        Make sure each policy is concise and clearly separated by a new line. Example:
                        1, Require 25% affordable housing in new developments
                        2, Limit building height to 5 stories in residential zones

                        # change after fixed chunking by paragraph?

                        Document:
                        \"\"\"
                        {doc_text}
                        \"\"\"
                        """
        
        with st.spinner("Analyzing document and extracting policies..."):
            response = model.generate_content(full_prompt)

        st.success("✅ Policies extracted:")

        st.subheader("📋 Raw Output")
        st.code(response.text, language="markdown")

        st.markdown(response.text)

        # csv / excel download buttons 
        try:
            df = pd.read_csv(io.StringIO(response.text), names=["Policy Number", "Policy Text"])
            st.subheader("📊 Structured Table")
            st.dataframe(df)

            # CSV download
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button("⬇ Download as CSV", csv_buffer.getvalue(),
                            file_name="extracted_policies.csv", mime="text/csv")

            # Excel download
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name="Policies")
            st.download_button("⬇ Download as Excel", excel_buffer.getvalue(),
                            file_name="extracted_policies.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        except Exception as e:
            st.error("⚠ Could not parse Gemini output. Showing text only.")
            st.download_button("⬇ Download as Text", response.text,
                                file_name="extracted_policies.txt", mime="text/plain")
 
              

        # send to Gemini
        # st.session_state.messages[{
        #     "role":"user",
        #     "parts":[full_prompt],
        # }]
        # with st.chat_message("user"):
        #     st.markdown(prompt)
        # response = model.generate_content(st.session_state.messages)
        # with st.chat_message("assistant"):
        #     st.markdown(response.text)
        # st.session_state.messages.append({
        #     "role":"model",
        #     "parts":[response.text],
        # })


        # add filtered policy topics later??