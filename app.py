import streamlit as st
import google.generativeai as genai
import google.ai.generativelanguage as glm
import os
import PIL 
import io
import pdfplumber
import docx
import pandas as pd

##################################################################
# Set up Gemini API

GOOGLE_API_KEY= st.secrets['GOOGLE_API_KEY']

genai.configure(api_key=GOOGLE_API_KEY)

##################################################################

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

##################################################################
# Set up page layout and title

# `st.set_page_config` is used to display the default layout width, the title of the app, and the emoticon in the browser tab.
st.set_page_config(page_title="PolicyExtractor", layout = 'centered', page_icon="")

# Logo and heading

c1, c2 = st.columns([0.30, 1.9],gap="small")

# The snowflake logo will be displayed in the first column, on the left.

with c1:

    st.image("images/logo.gif",use_column_width=True)


# The heading will be on the right.

with c2:

    #st.caption("")
    st.title("Policy Extractor Tool")


# Set up session state via st.session_state so that app interactions don't reset the app.

if not "valid_inputs_received" in st.session_state:
    st.session_state["valid_inputs_received"] = False


##################################################################

# Sidebar
with st.sidebar:
    st.title("🔍 Extract Policies")
    st.markdown("Upload a document and enter any custom instruction if needed.")
    user_note = st.text_area("Optional note to the model (adds to prompt)", placeholder="e.g., Focus on building code requirements")

# # Using "with" notation
# with st.sidebar:
#     st.title('Type of input:')
#     add_radio = st.radio(
#         "Type of input",
#         ("Document 📄"),
#         key = 'input_param',
#         label_visibility='collapsed'
#     )

# # Initialize previous_input_type in session_state if it doesn't exist
# if "previous_input_type" not in st.session_state:
#     st.session_state.previous_input_type = None

# # Check if the input type has changed
# if st.session_state.previous_input_type != add_radio:
#     # Clear the messages
#     st.session_state.messages = []
#     # Update previous_input_type
#     st.session_state.previous_input_type = add_radio

# if "messages" not in st.session_state:
#     st.session_state.messages = []

# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["parts"][0])


# if add_radio == 'Text ✏':
#     model = genai.GenerativeModel(model_name="models/gemini-2.5-pro",
#                                 generation_config=generation_config,
#                                 safety_settings=safety_settings)
#     prompt = st.chat_input("Ask anything")

#     if prompt:
#         message = prompt
#         st.session_state.messages.append({
#             "role":"user",
#             "parts":[message],
#         })
#         with st.chat_message("user"):
#             st.markdown(prompt)
#         response = model.generate_content(st.session_state.messages)
#         with st.chat_message("assistant"):
#             message_placeholder = st.empty()
#             message_placeholder.markdown(response.text)
#         st.session_state.messages.append({
#             "role":"model",
#             "parts":[response.text],
#         })

##################################################################

# TABBED INTERFACE

# Create tabs for Quick Start, Structured, Unstructured, and About sections
StartTab, AboutTab = st.tabs(["Quick Start", "About"])

with AboutTab:

    st.subheader("What is Streamlit?")
    st.markdown(
        "[Streamlit](https://streamlit.io) is a Python library that allows the creation of interactive, data-driven web applications in Python."
    )

    st.subheader("Resources")
    st.markdown(
        """
    - [Streamlit Documentation](https://docs.streamlit.io/)
    - [Cheat sheet](https://docs.streamlit.io/library/cheatsheet)
    - [Book](https://www.amazon.com/dp/180056550X) (Getting Started with Streamlit for Data Science)
    """
    )

    st.subheader("Deploy")
    st.markdown(
        "You can quickly deploy Streamlit apps using [Streamlit Community Cloud](https://streamlit.io/cloud) in just a few clicks."
    )


with StartTab:

    # if add_radio == 'Document 📄':
    st.warning("Please upload a planning document ", icon="🤖")
    model = genai.GenerativeModel('models/gemini-2.5-pro',
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


        # chunk by paragraph
        paragraphs = [p.strip() for p in doc_text.split("\n\n") if p.strip()]
        all_policies = []

        with st.spinner(f"Analyzing {len(paragraphs)} paragraphs..."):
            for i, para in enumerate(paragraphs):
                prompt = f"""You're a city planning policy expert.

                                Extract **any planning policies** mentioned in this paragraph in the following format:

                                Policy Number, Policy Description

                                Make sure each policy is concise and clearly separated by a new line. Example:
                                1, Require 25% affordable housing in new developments
                                2, Limit building height to 5 stories in residential zones

                                If there are no policies, respond with: NONE

                                Paragraph:
                                \"\"\"
                                {para}
                                \"\"\"
                                """
                
                response = model.generate_content(prompt)
                output = response.text.strip()

                if output.upper() != "NONE":
                    all_policies.extend([
                        line.strip() for line in output.splitlines() if line.strip()
                    ])
        
        if all_policies:

            st.success(f"✅ Extracted {len(all_policies)} policies!")

            st.subheader("📋 Policies (Raw)")
            st.code("\n".join(all_policies), language="markdown")


            # csv / excel download buttons 
            try:
                df = pd.read_csv(io.StringIO("\n".join(all_policies)), names=["Policy Number", "Policy Text"])
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
                st.download_button("⬇ Download as Text", "\n".join(all_policies),
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