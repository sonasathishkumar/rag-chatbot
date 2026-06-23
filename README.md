<div align="center">

# 🤖 RAG-Based Q&A Chatbot

### AI-Powered Document Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com)
[![FAISS](https://img.shields.io/badge/FAISS-0467DF?style=for-the-badge&logo=meta&logoColor=white)](https://faiss.ai)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-FF4B4B?style=for-the-badge)](https://rag-chatbot-document.streamlit.app)

<br/>

> **Upload any PDF → Ask questions → Get instant AI-powered answers**

<br/>

[🌐 Try Live Demo](https://rag-chatbot-document.streamlit.app) &nbsp;·&nbsp; [🐙 View Code](https://github.com/sonasathishkumar/rag-chatbot) &nbsp;·&nbsp; [💼 LinkedIn](https://www.linkedin.com/in/sona-sathishkumar/)

<br/>

</div>

---

## 📌 What is this?

**RAG-Based Q&A Chatbot** is an enterprise-grade document intelligence application that uses **Retrieval-Augmented Generation (RAG)** to answer questions from your PDF documents accurately and instantly.

Unlike traditional chatbots that make up answers, this system **grounds every response in your actual documents** — providing source-backed, accurate answers with zero hallucinations.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 📄 **PDF Upload** | Upload multiple PDF documents up to 200MB each |
| 🔍 **Semantic Search** | FAISS vector search finds the most relevant context |
| 🤖 **RAG Pipeline** | Every answer is grounded in your document content |
| 📎 **Source Citations** | Every answer shows exactly which source chunk was used |
| 📊 **Analytics Dashboard** | Track questions asked, document usage, and session stats |
| 📋 **Document Library** | Manage and view all uploaded documents with chunk counts |
| 💬 **Chat History** | Full conversation history maintained per session |
| 🎯 **Confidence Scoring** | Semantic similarity score shown for each answer |
| 🌙 **Professional UI** | Dark navy sidebar with clean white card design |
| 🐳 **Docker Ready** | One-command deployment with Docker |

---

## 🌐 Live Demo

<div align="center">

### 👉 [https://rag-chatbot-document.streamlit.app](https://rag-chatbot-document.streamlit.app)

</div>

### How to test in 30 seconds:
1. Open the live demo link above
2. In the sidebar, upload any PDF document
3. Wait for **"✅ Ready to chat"** status
4. Go to **💬 Chat** page
5. Type: *"Summarize the main points"*
6. See your AI-powered answer with sources!

---

## ⚙️ How RAG Works
┌─────────────────────────────────────────────────────────────┐

│                        RAG PIPELINE                          │

├─────────────────────────────────────────────────────────────┤

│                                                              │

│  📄 PDF Upload                                               │

│       ↓                                                      │

│  ✂️  Text Chunking  (500 words per chunk, 50 word overlap)   │

│       ↓                                                      │

│  🔢  Embedding Generation  (all-MiniLM-L6-v2 model)         │

│       ↓                                                      │

│  💾  FAISS Vector Index  (stored in memory)                  │

│       ↓                                                      │

│  ❓  User Question → Converted to embedding                  │

│       ↓                                                      │

│  🔍  Top-3 Most Similar Chunks Retrieved                     │

│       ↓                                                      │

│  🤖  Extractive Answer Generated from Context                │

│       ↓                                                      │

│  💬  Answer + Source Citations Displayed                     │

│                                                              │

└─────────────────────────────────────────────────────────────┘

---

## 🛠 Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.10 | Core programming language |
| **Streamlit** | 1.28+ | Interactive web UI framework |
| **LangChain** | 0.1+ | RAG pipeline orchestration |
| **FAISS** | 1.7.4 | High-speed vector similarity search |
| **Sentence Transformers** | 2.2+ | Semantic text embeddings |
| **pdfplumber** | 0.9+ | PDF text extraction |
| **PyPDF2** | 3.0+ | PDF file handling |
| **Plotly** | 5.17+ | Interactive analytics charts |
| **ReportLab** | 4.0+ | PDF report generation |
| **Docker** | Latest | Containerized deployment |

---

## 📁 Project Structure
rag-chatbot/

│

├── 📄 app.py                    ← Main Streamlit application (UI)

├── 🧠 rag_engine.py             ← RAG pipeline (embed, index, retrieve)

├── 🔐 auth.py                   ← Authentication module

├── 📋 requirements.txt          ← Python dependencies

├── 🐳 Dockerfile                ← Docker configuration

├── 📝 README.md                 ← Project documentation

├── 🔧 create_sample.py          ← Sample PDF generator

│

├── .streamlit/

│   └── config.toml              ← Streamlit server configuration

│

└── sample_docs/

└── sample.pdf               ← Sample PDF for testing

---

## 💻 Run Locally

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Git

### Step 1 — Clone the repository
```bash
git clone https://github.com/sonasathishkumar/rag-chatbot.git
cd rag-chatbot
```

### Step 2 — Install all dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Run the Streamlit app
```bash
streamlit run app.py
```

### Step 4 — Open in browser
http://localhost:8501

### Step 5 — Test the chatbot
- Upload `sample_docs/sample.pdf` from the sidebar
- Ask: *"What are the key findings?"*
- See the AI answer with sources!

---

## 🐳 Run with Docker

### Build the Docker image
```bash
docker build -t rag-chatbot .
```

### Run the container
```bash
docker run -p 8501:8501 rag-chatbot
```

### Open in browser
http://localhost:8501

---

## 📊 Pages & Navigation

### 💬 Chat Page
- Real-time Q&A with your documents
- Source citations shown for every answer
- Example question chips for quick start
- Full conversation history

### 📄 Documents Page
- View all uploaded documents
- See chunk count per document
- Document indexing status
- Chunks per document chart

### 📊 Analytics Page
- Total questions asked this session
- Average response time
- Source document usage pie chart
- Recent questions table
- Top query keywords

### ℹ️ About Page
- Project overview and architecture
- How RAG works step by step
- Full tech stack details
- Technical specifications table

---

## 🔧 Configuration

### Streamlit Server Config
Edit `.streamlit/config.toml`:
```toml
[server]
port = 8501
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

### RAG Engine Settings
Edit `rag_engine.py` to customize:
```python
chunk_size = 500          # Words per chunk
overlap = 50              # Overlap between chunks
top_k = 3                 # Chunks retrieved per query
model = "all-MiniLM-L6-v2"  # Embedding model
```

---

## 📈 Performance Specs

| Metric | Value |
|---|---|
| **Embedding Model** | all-MiniLM-L6-v2 |
| **Model Size** | ~90 MB |
| **Vector Store** | FAISS IndexFlatL2 |
| **Chunk Size** | 500 words |
| **Chunk Overlap** | 50 words |
| **Top-K Retrieval** | 3 chunks |
| **Avg Response Time** | < 2 seconds |
| **Max File Size** | 200 MB per PDF |
| **Supported Format** | PDF |

---

## 🎯 Real-World Use Cases
📚 Research Papers    → Ask questions about academic papers instantly

📋 Business Reports   → Extract key insights from lengthy reports

📖 Technical Manuals  → Find specific information in documentation

💼 Legal Documents    → Query contracts and legal text quickly

🏥 Medical Records    → Analyze and summarize medical documents

📰 News Articles      → Summarize and query news content

📘 Study Materials    → Q&A from textbooks and study guides

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m "Add amazing feature"`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request
