# RAG-Based Q&A Chatbot

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)
![LangChain](https://img.shields.io/badge/LangChain-Integration-green)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Store-orange)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Models-yellow)

This project is a fully offline, free, and self-hosted RAG (Retrieval-Augmented Generation) Q&A Chatbot. It allows users to upload PDF documents and ask questions about their content, using local vector embeddings and local LLMs.

## Features
- **100% Offline & Free**: Uses open-source HuggingFace models, no API keys required.
- **PDF Upload**: Instantly process multiple PDF documents.
- **Smart Retrieval**: Uses FAISS vector database to retrieve the most relevant chunks.
- **Accurate Answers**: Answers questions specifically based on the context of your documents using flan-t5-base.
- **Sleek UI**: Professional, dark sidebar UI with intuitive navigation and chat interface.
- **Analytics Dashboard**: Tracks document and Q&A session statistics.
- **Source Transparency**: Shows exactly which chunks of text were used to generate each answer.

## How It Works
1. 📄 **Upload PDF documents**: You upload one or more PDFs to the application.
2. ✂️ **Text is split into chunks**: The app reads the documents and splits the text into manageable 500-word chunks.
3. 🔢 **Chunks are converted to embeddings**: Using `sentence-transformers`, chunks are embedded into dense vectors.
4. 💾 **Embeddings stored in FAISS index**: The vectors are added to a local FAISS index for rapid similarity search.
5. ❓ **Your question is embedded**: When you ask a question, it is also embedded using the same model.
6. 🔍 **Similar chunks retrieved**: The system searches FAISS for chunks most similar to your question.
7. 🤖 **LLM generates answer from chunks**: A HuggingFace pipeline (`flan-t5-base`) reads the retrieved chunks and generates a concise, accurate answer.

## Tech Stack
| Component | Technology |
| --- | --- |
| **Embedding Model** | all-MiniLM-L6-v2 |
| **LLM** | google/flan-t5-base |
| **Vector Store** | FAISS (IndexFlatL2) |
| **Chunk Size** | 500 words |
| **Chunk Overlap** | 50 words |
| **Top-K Retrieval** | 3 chunks |
| **Max Answer Length** | 200 tokens |

## How to run locally
1. Clone the repository and navigate to the project directory.
2. Ensure you have Python 3.10 installed.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Generate a sample PDF to test with:
   ```bash
   python create_sample.py
   ```
5. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
6. Open your browser to http://localhost:8501.

## How to run with Docker
1. Build the Docker image:
   ```bash
   docker build -t rag-chatbot .
   ```
2. Run the container:
   ```bash
   docker run -p 8501:8501 rag-chatbot
   ```

## Screenshots
*(Add screenshots here)*

## Author
**Sona S**
- Role: B.Tech AI & Data Science @ Karpagam College of Engineering
- LinkedIn: [sonasathishkumar](https://linkedin.com/in/sonasathishkumar)
- GitHub: [sonasathishkumar](https://github.com/sonasathishkumar)
