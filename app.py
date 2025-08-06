import streamlit as st
import google.generativeai as genai
import google.ai.generativelanguage as glm
import re
import time

from backend.extract import process_document, save_to_excel

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

# st.title('Policy Extractor Tool')
# st.markdown("""
# Welcome to our wildfire policy extractor tool! Please click the “Drag and Drop” button to upload a planning document. 
#             The document will be scanned using our custom prompt to extract all wildfire-related policies. 
#             A CSV file with the extracted policies will be returned.
# """)
# `st.set_page_config` is used to display the default layout width, the title of the app, and the emoticon in the browser tab.
st.set_page_config(page_title="PolicyExtractor", layout = 'centered', page_icon="")

# Logo and heading

c1, c2 = st.columns([0.30, 1.9],gap="small")

# The snowflake logo will be displayed in the first column, on the left.

with c1:

    st.image("images/logo.gif")


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

    st.markdown(
        "## 📘 How to Use"
    )

    st.markdown(
        """
            1. **Upload** a city planning document (PDF, DOCX, or TXT)
            2. View automatically extracted policies
            3. (Optional) *Ask* questions or *filter* for keywords or topics
            4. **Download** the results as Excel or CSV
        """
        )
    
    st.markdown("---")
    
    st.markdown("## What It Does")
    st.markdown(
        """
            This tool extracts **all policies** from a planning document using Gemini AI.

            You can:
            - See every extracted policy
            - 🔥 **Focus on wildfire-related content** (in progress)
            - 💬 Ask custom questions (in progress)
    """
                )

    
    st.markdown("---")
    st.markdown("# About")

    st.markdown(
        """
            **Policy Extractor** is a tool built with **Google's Gemini 2.0 Flash-Lite**, designed to help city planners and researchers automatically extract policies from municipal planning documents (e.g., CAPs, general plans).
            
            Gemini is a large language model that can be used for a variety of tasks, including text generation, translation, and question answering.
        """
        )
    
    st.markdown(
        """
        The tool processes PDFs, DOCX, or TXT files, page-by-page, using the Gemini API to identify key planning policies, particularly those related to zoning, evacuation, and fire resilience.
        Users can also filter or prompt the model for specific topics.
        """
    )

# Increase sidebar width using custom CSS
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            min-width: 280px;
            width: 280px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


##################################################################

# TABBED INTERFACE

# Create tabs for Quick Start, About sections
StartTab, AboutTab = st.tabs(["Quick Start", "About"])

##################################################################

# About Tab - Information about the project, help guide for API usage (API usage limits could be a separate tab altogether)
# For now it's just info about streamlit :)
with AboutTab:

    st.subheader("What is Policy-Extractor?")
    st.markdown(
        "[Policy Extractor](https://policy-extractor.streamlit.app/) is a web app powered by Google's Gemini AI that automatically extracts policy statements from city planning documents."
    )

    st.markdown(
        """
        The tool processes PDFs, DOCX, or TXT files, paragraphage-by-paragraph to identify key planning policies, particularly those related to zoning, evacuation, and fire resilience.
        Users can also filter or prompt the model for specific topics.
        """
    )

    st.subheader("Resources")
    st.markdown(
        """
    - [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
    - [Streamlit Documentation](https://docs.streamlit.io/)
    - [Github Repository](https://github.com/bchan42/Policy-Extractor)
    """
    )

    # st.subheader("Deploy")
    # st.markdown(
    #     "You can quickly deploy Streamlit apps using [Streamlit Community Cloud](https://streamlit.io/cloud) in just a few clicks."
    # )

##################################################################
# Start Tab - Upload doc and get policies from our basic prompt 
with StartTab:
    st.markdown("""                
        
        Welcome to our policy extraction tool! 
                
        This tool sends a document to Google's Gemini AI, which reads it and returns policies found in the document.
                
        To use our custom prompt, start here and upload your planning document.
                
    """)

    st.warning("Please click the “Drag and Drop” button to upload a planning document.", icon="🤖")
    model = genai.GenerativeModel(model_name="gemini-2.0-flash",
                                generation_config=generation_config,
                                safety_settings=safety_settings)

    doc = st.file_uploader("Choose a file (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])


##################################################################

    # CODE FOR EXTRACTING POLICIES
    if doc:
        df = process_document(doc)

        st.success("Extraction complete! Compare paragraph inputs with extracted policies:")

        # Helpful instructions before showing DataFrame
        st.markdown(
            """
            ℹ️ **Tips for viewing the table below**:
            - Hover over the table to see icons at top-right of the table. 
                - Click the **full-screen** icon to expand the view.
                    - **Double-click** on any cell to view full text if it's cut off.
                - Click the **magnifying glass 🔍** icon to search for specific words.
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



st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<hr style='margin-top: 2rem; margin-bottom: 1rem;' />
<div style='text-align: center;'>
    © 2025 <strong> Policy Extractor</strong> 
    <br>Created by Bernette Chan and Nidhi Shinde
</div>
""", unsafe_allow_html=True)