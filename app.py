import streamlit as st
import google.generativeai as genai
import google.ai.generativelanguage as glm
import os
import PIL 
import io
import pdfplumber
import docx
import pandas as pd

from backend.extract import process_document, save_to_excel


# st.markdown("""
#     <style>
#         /* Reduce padding */
#         .block-container {
#             padding-top: 2rem;
#             padding-bottom: 2rem;
#             padding-left: 2rem;
#             padding-right: 2rem;
#         }

#         /* Improve font */
#         html, body, [class*="css"] {
#             font-family: 'Segoe UI', sans-serif;
#             font-size: 16px;
#             color: #333333;
#         }

#         /* Button styling */
#         .stButton button {
#             background-color: #357ABD;
#             color: white;
#             border-radius: 8px;
#             padding: 0.6em 1.2em;
#             font-size: 16px;
#             border: none;
#         }

#         .stButton button:hover {
#             background-color: #285A8C;
#         }

#         /* Table tweaks */
#         .css-1d391kg {  /* makes dataframe header bold and clean */
#             font-weight: 600;
#         }
#     </style>
# """, unsafe_allow_html=True)



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

st.set_page_config(page_title="PolicyExtractor", layout = 'wide')

st.title('Policy Extractor Tool')
st.markdown("""
Welcome to our wildfire policy extractor tool! Please click the “Drag and Drop” button to upload a planning document. 
            The document will be scanned using our custom prompt to extract all wildfire-related policies. 
            A CSV file with the extracted policies will be returned.
""")

# Sidebar
with st.sidebar:
    st.title("🔍 Extract Policies")
    # st.markdown("Upload a document and enter any custom instruction if needed.")
    # user_note = st.text_area("Optional note to the model (adds to prompt)", placeholder="e.g., Focus on building code requirements")



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


# # if add_radio == 'Text ✏':
# #     model = genai.GenerativeModel(model_name="models/gemini-2.5-pro",
# #                                 generation_config=generation_config,
# #                                 safety_settings=safety_settings)
# #     prompt = st.chat_input("Ask anything")

# #     if prompt:
# #         message = prompt
# #         st.session_state.messages.append({
# #             "role":"user",
# #             "parts":[message],
# #         })
# #         with st.chat_message("user"):
# #             st.markdown(prompt)
# #         response = model.generate_content(st.session_state.messages)
# #         with st.chat_message("assistant"):
# #             message_placeholder = st.empty()
# #             message_placeholder.markdown(response.text)
# #         st.session_state.messages.append({
# #             "role":"model",
# #             "parts":[response.text],
# #         })

            

#     # send to Gemini
#     # st.session_state.messages[{
#     #     "role":"user",
#     #     "parts":[full_prompt],
#     # }]
#     # with st.chat_message("user"):
#     #     st.markdown(prompt)
#     # response = model.generate_content(st.session_state.messages)
#     # with st.chat_message("assistant"):
#     #     st.markdown(response.text)
#     # st.session_state.messages.append({
#     #     "role":"model",
#     #     "parts":[response.text],
#     # })


#     # add filtered policy topics later??



doc = st.file_uploader("Upload a planning document", type=["pdf", "docx", "txt"])

if doc:
    df = process_document(doc)

    st.success("Extraction complete! Compare chunk inputs with extracted policies:")

    # Helpful instructions before showing DataFrame
    st.markdown(
        """
        ℹ️ **Tips for viewing the table below**:
        - Hover over the table to see icons at top-right of the table. 
        - Click the **full-screen** icon to expand the view.
        - **Double-click** on any cell to view full text if it's cut off.
        - - Click the **magnifying glass 🔍** icon to search for specific words.
        - Click the **download** icon to download the data as a CSV file. 
        """
    )

    # Display DataFrame directly (scrollable, clean layout)
    st.dataframe(df, use_container_width=True)

    # Allow download as Excel
    excel_file = save_to_excel(df)
    st.download_button(
        label="Download Extracted Policies (.xlsx)",
        data=excel_file,
        file_name="extracted_policies.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
