📁 Policy-Extractor/
├── app.py                  ← main file to run
│
├── 📁 frontend/            ← UI-related code: website layout, chat UI
│
├── 📁 backend/             ← processing and LLM logic
│   ├── extract.py          ← doc reading, chunking, prompt generation to extract
│   ├── chatbot.py          ← set up chatbot for user to ask questions
│   └── filters.py          ← ??: keyword filtering, topic modeling
│
├── .streamlit/
│   └── secrets.toml        ← store API key
│
├── requirements.txt
│
└── README.md
