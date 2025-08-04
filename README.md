# Policy Extraction Web App

[**Live App →**](https://chat-gemini-pro.streamlit.app/)

Policy Extractor is a tool built with Google's Gemini Pro, designed to help city planners and researchers automatically extract policies from municipal planning documents (e.g., CAPs, general plans). Gemini is a large language model that can be used for a variety of tasks, including text generation, translation, and question answering.

The tool processes PDFs, DOCX, or TXT files, page-by-page, using the Gemini API to identify key planning policies, particularly those related to zoning, evacuation, and fire resilience. Users can also filter or prompt the model for specific topics.

---

## Getting Started

To get started, you just need to click on this web app [Policy-Extractor](https://chat-gemini-pro.streamlit.app/).


In the case that the API Key needs to be renewed, follow the steps below:

1. Clone the Repository

```bash
git clone https://github.com/bchan42/Policy-Extractor.git
cd Policy-Extractor
```

2. Set Up Google Gemini Key
* Create a Google Cloud project and enable the Generative Language API
* Generate an API key by following [these instructions](https://makersuite.google.com/app/apikey).

3. Add your API Key into the code
* Create a `.streamlit/secrets.toml` file and add your key:
```bash
GOOGLE_API_KEY = "YOUR-API-KEY-HERE"
```

## Features

**Policy-Extractor** has a number of features that make it a powerful policy extractor tool. These features include:

* 🔥 Wildfire policy extraction from planning documents
* PDF, DOCX, and TXT support
* Topic filtering via optional prompt input
* Gemini Pro API integration for high-quality output
* Clean, minimal Streamlit web interface

## Documentation

For more information on **Policy-Extractor**, please see the following resources:

* [Gemini documentation](https://deepmind.google/technologies/gemini/#introduction)

## License

Chat-Gemini is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for more information.

This project was adapted in part from hrishi-008/Chat-Gemini, which provided a helpful starting template for building Gemini-powered apps in Streamlit.