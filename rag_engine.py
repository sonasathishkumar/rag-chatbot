import os
import pdfplumber
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import T5ForConditionalGeneration, AutoTokenizer
import torch

class RAGEngine:
    def __init__(self):
        # Embeddings model (fast, ~25 MB, already cached after first run)
        self.embeddings = HuggingFaceEmbeddings(model_name='paraphrase-MiniLM-L3-v2')
        self.vector_store = None
        self.chunks = []
        self.chat_history = []
        self.loaded_files = []

        # Lazy-loaded — T5 only initialises on the FIRST ask() call
        self._tokenizer = None
        self._model = None

    # ──────────────────────────────────────────────────────────────────────────
    # Lazy model loader
    # ──────────────────────────────────────────────────────────────────────────
    def _ensure_model(self):
        """Download & load Flan-T5 on first use (keeps startup instant)."""
        if self._model is None:
            model_name = "google/flan-t5-base"
            self._tokenizer = AutoTokenizer.from_pretrained(model_name)
            self._model = T5ForConditionalGeneration.from_pretrained(model_name)
            self._model.eval()

    @property
    def model_ready(self) -> bool:
        return self._model is not None

    # ──────────────────────────────────────────────────────────────────────────
    # Document ingestion
    # ──────────────────────────────────────────────────────────────────────────
    def load_pdf(self, pdf_file):
        """Extract text from a PDF file."""
        full_text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        return full_text

    def chunk_text(self, text, chunk_size=1000, overlap=150):
        """Split text with LangChain's RecursiveCharacterTextSplitter."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        return splitter.split_text(text)

    def build_index(self, chunks):
        """Build / update the FAISS vector store."""
        if not chunks:
            return 0
        self.chunks.extend(chunks)
        if self.vector_store is None:
            self.vector_store = FAISS.from_texts(chunks, self.embeddings)
        else:
            self.vector_store.add_texts(chunks)
        return len(chunks)

    # ──────────────────────────────────────────────────────────────────────────
    # Generation
    # ──────────────────────────────────────────────────────────────────────────
    def _generate(self, prompt: str, max_new_tokens: int = 300) -> str:
        """Run Flan-T5 inference directly (no pipeline registry needed)."""
        self._ensure_model()
        inputs = self._tokenizer(
            prompt,
            return_tensors="pt",
            max_length=512,
            truncation=True,
        )
        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                num_beams=4,
                early_stopping=True,
            )
        return self._tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    # ──────────────────────────────────────────────────────────────────────────
    # Question answering
    # ──────────────────────────────────────────────────────────────────────────
    def ask(self, query):
        """Retrieve relevant context then generate an answer locally."""
        if not self.vector_store:
            return {
                "answer": "📄 Please upload a document first from the sidebar.",
                "sources": [],
                "scores": []
            }

        try:
            # 1. Semantic retrieval
            docs_and_scores = self.vector_store.similarity_search_with_score(query, k=4)
            sources = [doc.page_content for doc, _ in docs_and_scores]
            scores  = [max(0.0, 1.0 - float(s) / 2.0) for _, s in docs_and_scores]

            # 2. Build context (cap to keep within T5's 512-token limit)
            context = "\n\n".join(sources[:3])[:1400]

            # 3. Inject recent conversation history (last 2 turns)
            history_text = ""
            if self.chat_history:
                recent = self.chat_history[-2:]
                history_text = "Previous conversation:\n"
                for q, a in recent:
                    history_text += f"Q: {q}\nA: {a}\n"
                history_text += "\n"

            # 4. Compose instruction-style prompt for Flan-T5
            prompt = (
                "Answer the question accurately and concisely based only on the context below.\n\n"
                f"{history_text}"
                f"Context:\n{context}\n\n"
                f"Question: {query}\n\n"
                "Answer:"
            )

            # 5. Generate — model loads here on first call
            answer = self._generate(prompt)

            if not answer:
                answer = (
                    "I couldn't find a specific answer in the documents. "
                    "Try rephrasing your question."
                )

            # 6. Store for follow-up context
            self.chat_history.append((query, answer))

            return {"answer": answer, "sources": sources, "scores": scores}

        except Exception as e:
            return {
                "answer": f"❌ **Error generating answer:**\n{str(e)}",
                "sources": [],
                "scores": []
            }

    def clear_memory(self):
        """Reset the conversation history."""
        self.chat_history = []

    def summarize_document(self, text):
        """Generate a concise summary of the document using the first part of the text."""
        self._ensure_model()
        # Summarize the first 1500 chars to fit within T5's limit
        content_to_summarize = text[:1500]
        prompt = (
            "Summarize the following document concisely:\n\n"
            f"{content_to_summarize}\n\n"
            "Summary:"
        )
        return self._generate(prompt, max_new_tokens=150)
