import os
import traceback
import faiss
import numpy as np
import pdfplumber
import streamlit as st
from sentence_transformers import SentenceTransformer
from groq import Groq, BadRequestError

# Maximum characters sent in a single Groq prompt (well under llama3-8b-8192's
# ~8 000-token context window; 1 token ≈ 4 chars, so 12 000 chars ≈ 3 000 tokens).
MAX_PROMPT_CHARS = 12_000
MODEL = "llama-3.1-8b-instant"   # llama3-8b-8192 was decommissioned by Groq

class RAGEngine:
    def __init__(self):
        # Embeddings model (fast, ~25 MB, already cached after first run)
        self.embedder = SentenceTransformer('paraphrase-MiniLM-L3-v2')
        self.index = None
        self.embeddings = None
        self.chunks = []
        self.chat_history = []
        self.loaded_files = []

        # Groq client — key read from Streamlit secrets
        api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
        self._groq = Groq(api_key=api_key) if api_key else None

    # ──────────────────────────────────────────────────────────────────────────
    # Model readiness
    # ──────────────────────────────────────────────────────────────────────────
    @property
    def model_ready(self) -> bool:
        """True when the Groq client is configured with an API key."""
        return self._groq is not None

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
        """Split text into overlapping chunks using a simple sliding-window approach."""
        chunks = []
        start = 0
        text_len = len(text)
        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunks.append(text[start:end])
            if end == text_len:
                break
            start += chunk_size - overlap
        return chunks

    def build_index(self, chunks):
        """Build / update the FAISS index directly."""
        if not chunks:
            return 0
        self.chunks = chunks
        vecs = self.embedder.encode(chunks, show_progress_bar=False)
        vecs = np.array(vecs).astype('float32')
        dimension = vecs.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(vecs)
        self.embeddings = vecs
        return len(chunks)

    # ──────────────────────────────────────────────────────────────────────────
    # Generation via Groq (llama3-8b-8192)
    # ──────────────────────────────────────────────────────────────────────────
    def _generate(self, system_prompt: str, user_prompt: str) -> str:
        """Call the Groq API and return the assistant reply."""
        print("=" * 50)
        print("=== GROQ CALL START ===")

        if self._groq is None:
            print("=== GROQ CALL ABORTED: no API key ===")
            return "⚠️ GROQ_API_KEY is not configured. Add it to Streamlit secrets."

        # --- Guard: no None / empty content ---
        system_prompt = (system_prompt or "").strip() or "You are a helpful assistant."
        user_prompt   = (user_prompt   or "").strip()
        if not user_prompt:
            print("=== GROQ CALL ABORTED: user_prompt is empty ===")
            return "⚠️ No question or context was provided. Please try again."

        # --- Guard: truncate to stay within token limit ---
        system_prompt = system_prompt[:MAX_PROMPT_CHARS]
        user_prompt   = user_prompt[:MAX_PROMPT_CHARS]

        print(f"Model            : {MODEL}")
        print(f"max_tokens       : 512")
        print(f"System prompt len: {len(system_prompt)} chars")
        print(f"User prompt len  : {len(user_prompt)} chars")
        print(f"User prompt (200): {user_prompt[:200]!r}")
        print("-" * 50)

        try:
            response = self._groq.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=512,
            )
            result = response.choices[0].message.content.strip()
            print(f"Response len     : {len(result)} chars")
            print("=== GROQ CALL SUCCESS ===")
            print("=" * 50)
            return result

        except Exception as e:
            print("=" * 50)
            print(f"=== GROQ CALL FAILED ===")
            print(f"Exception type   : {type(e).__name__}")
            print(f"Exception message: {e}")
            print(f"Status code      : {getattr(e, 'status_code', 'N/A')}")
            print(f"Groq message     : {getattr(e, 'message', 'N/A')}")
            print("--- Full traceback below ---")
            traceback.print_exc()
            print("=" * 50)
            raise  # re-raise so Streamlit / caller also sees the error

    # ──────────────────────────────────────────────────────────────────────────
    # Question answering
    # ──────────────────────────────────────────────────────────────────────────
    def retrieve(self, query, top_k=3):
        """Return (chunk_text, distance) pairs for the top_k nearest chunks."""
        query_vec = self.embedder.encode([query])
        query_vec = np.array(query_vec).astype('float32')
        distances, indices = self.index.search(query_vec, top_k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunks):
                results.append((self.chunks[idx], float(distances[0][i])))
        return results

    def ask(self, query):
        """Retrieve relevant context then generate an answer via Groq."""
        if self.index is None:
            return {
                "answer": "📄 Please upload a document first from the sidebar.",
                "sources": [],
                "scores": []
            }

        try:
            # 1. Semantic retrieval
            results = self.retrieve(query, top_k=4)
            sources = [chunk for chunk, _ in results]
            scores  = [max(0.0, 1.0 - dist / 2.0) for _, dist in results]

            # 2. Build context
            context = "\n\n".join(sources[:3])[:3000]

            # 3. Recent conversation history (last 2 turns)
            history_text = ""
            if self.chat_history:
                recent = self.chat_history[-2:]
                history_text = "Previous conversation:\n"
                for q, a in recent:
                    history_text += f"Q: {q}\nA: {a}\n"
                history_text += "\n"

            # 4. Prompts
            system_prompt = (
                "You are a helpful assistant that answers questions strictly based on "
                "the provided document context. If the answer is not in the context, "
                "say so clearly rather than guessing."
            )
            user_prompt = (
                f"{history_text}"
                f"Context:\n{context}\n\n"
                f"Question: {query}"
            )

            # 5. Generate via Groq
            answer = self._generate(system_prompt, user_prompt)

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
        """Generate a concise summary of the document using Groq.

        Sanitises the raw PDF text before sending to the API:
        - Strips null bytes and ASCII control characters (common in PDFs)
          which cause Groq to return a 400 BadRequestError.
        - Truncates conservatively to 3 000 chars (≈ 750 tokens) to stay
          well within the model's context window.
        Returns a plain-text fallback string on any error so the caller
        (document upload) never crashes.
        """
        if not text or not text.strip():
            return "No text could be extracted from this document."

        # --- Sanitise: remove null bytes + ASCII control chars (except \n \t) ---
        clean = "".join(
            ch for ch in text
            if ch in ("\n", "\t") or (ord(ch) >= 32 and ord(ch) != 127)
        ).strip()

        if not clean:
            return "Document contained only non-printable characters."

        system_prompt = "You are a document summarizer. Provide a clear, concise summary."
        snippet    = clean[:3_000]          # ~750 tokens — very safe ceiling
        user_prompt = f"Summarize the following document concisely:\n\n{snippet}"

        try:
            return self._generate(system_prompt, user_prompt)
        except Exception as e:
            print(f"summarize_document failed: {type(e).__name__}: {e}")
            return "(Auto-summary unavailable — document indexed successfully.)"
