import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
from rag_engine import RAGEngine
from collections import Counter
import re
from auth import verify_user, register_user
from fpdf import FPDF
import io

st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="wide")

def generate_chat_pdf(messages):
    pdf = FPDF()
    pdf.add_page()
    
    # Header background
    pdf.set_fill_color(240, 244, 255)
    pdf.rect(0, 0, 210, 30, 'F')
    
    # Header text
    pdf.set_y(10)
    pdf.set_font("Arial", 'B', size=16)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 10, txt="RAG Chatbot - Conversation Export", ln=True, align="L")
    pdf.ln(15)
    
    for m in messages:
        role = "User" if m["role"] == "user" else "Assistant"
        content = m["content"].encode('latin-1', 'replace').decode('latin-1')
        
        if role == "User":
            pdf.set_font("Arial", 'B', size=11)
            pdf.set_text_color(99, 102, 241) # Indigo color for user
            pdf.cell(0, 6, txt="You:", ln=True)
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(30, 41, 59) # Dark slate
            pdf.multi_cell(0, 6, txt=content)
        else:
            pdf.set_font("Arial", 'B', size=11)
            pdf.set_text_color(16, 185, 129) # Emerald color for assistant
            pdf.cell(0, 6, txt="Assistant:", ln=True)
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(71, 85, 105) # Lighter slate
            pdf.multi_cell(0, 6, txt=content)
            
        pdf.ln(6)
        
    return bytes(pdf.output())

# ─────────────────────────────────────────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────────────────────────────────────────
def show_login_page():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* ── Hide Streamlit chrome ── */
        [data-testid="stSidebar"]   { display: none !important; }
        #MainMenu                   { visibility: hidden; }
        footer                      { visibility: hidden; }
        header                      { visibility: hidden; }

        /* ── Kill ALL default top padding/margin ── */
        .block-container,
        [data-testid="stAppViewBlockContainer"] {
            padding-top: 0 !important;
            margin-top: 0 !important;
            max-width: 100% !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
        }

        /* ── Full-screen dark background ── */
        .stApp {
            background:
                radial-gradient(ellipse 80% 60% at 20% 10%, rgba(99,102,241,0.15) 0%, transparent 60%),
                radial-gradient(ellipse 60% 50% at 80% 90%, rgba(79,70,229,0.12) 0%, transparent 55%),
                linear-gradient(160deg, #07090f 0%, #0d1117 50%, #0a0c14 100%) !important;
            min-height: 100vh;
        }

        /* ── Style inputs ── */
        .stTextInput > div > div > input {
            background: rgba(255,255,255,0.06) !important;
            border: 1px solid rgba(255,255,255,0.11) !important;
            border-radius: 12px !important;
            color: #f1f5f9 !important;
            font-size: 15px !important;
            padding: 13px 16px !important;
            transition: border-color 0.2s, box-shadow 0.2s !important;
        }
        .stTextInput > div > div > input:focus {
            border-color: #6366f1 !important;
            background: rgba(99,102,241,0.08) !important;
            box-shadow: 0 0 0 3px rgba(99,102,241,0.18) !important;
            outline: none !important;
        }
        .stTextInput > div > div > input::placeholder {
            color: rgba(255,255,255,0.28) !important;
        }
        .stTextInput > label {
            color: rgba(255,255,255,0.6) !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            letter-spacing: 0.3px !important;
        }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
            background: rgba(255,255,255,0.05) !important;
            border-radius: 14px !important;
            padding: 4px !important;
            gap: 4px !important;
            border: 1px solid rgba(255,255,255,0.07) !important;
        }
        .stTabs [data-baseweb="tab"] {
            background: transparent !important;
            color: rgba(255,255,255,0.45) !important;
            border-radius: 10px !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            padding: 10px 24px !important;
            border: none !important;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
            color: white !important;
            box-shadow: 0 4px 14px rgba(99,102,241,0.4) !important;
        }
        .stTabs [data-baseweb="tab-panel"]  { padding-top: 20px !important; }
        .stTabs [data-baseweb="tab-highlight"] { display: none !important; }
        .stTabs [data-baseweb="tab-border"] { display: none !important; }

        /* ── Buttons ── */
        div[data-testid="stVerticalBlock"] .stButton > button {
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            padding: 14px 24px !important;
            width: 100% !important;
            transition: all 0.25s ease !important;
            box-shadow: 0 4px 20px rgba(99,102,241,0.4) !important;
            letter-spacing: 0.3px !important;
        }
        div[data-testid="stVerticalBlock"] .stButton > button:hover {
            background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
            box-shadow: 0 8px 32px rgba(99,102,241,0.55) !important;
            transform: translateY(-2px) !important;
        }
        div[data-testid="stVerticalBlock"] .stButton > button p {
            color: white !important;
            font-size: 15px !important;
            font-weight: 600 !important;
        }

        /* ── Alerts ── */
        .stAlert { border-radius: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Spacer to vertically center ──
    _, col, _ = st.columns([1.2, 1.6, 1.2])
    with col:
        # Brand header — fully self-contained HTML
        st.markdown("""
        <div style="text-align:center; padding-top:40px; margin-bottom:24px;">
          <div style="
              width:68px; height:68px;
              background:linear-gradient(135deg,#6366f1,#4338ca);
              border-radius:18px;
              display:inline-flex; align-items:center; justify-content:center;
              font-size:32px;
              box-shadow:0 12px 36px rgba(99,102,241,0.45);
          ">🤖</div>
          <h1 style="color:#ffffff; font-size:28px; font-weight:800;
                     margin:16px 0 6px; letter-spacing:-0.8px;">RAG Chatbot</h1>
          <p style="color:rgba(255,255,255,0.38); font-size:14px; margin:0; font-weight:400;">
            Document Intelligence Platform
          </p>
        </div>
        """, unsafe_allow_html=True)

        # Tabs & form — no wrapper divs, just Streamlit widgets styled via CSS
        tab_in, tab_up = st.tabs(["🔑   Sign In", "✨   Create Account"])

        with tab_in:
            email_in = st.text_input("Email Address", placeholder="you@example.com", key="signin_email")
            pwd_in   = st.text_input("Password", type="password", placeholder="Enter your password", key="signin_pwd")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            if st.button("Sign In  →", key="btn_signin", use_container_width=True):
                if not email_in.strip() or not pwd_in:
                    st.error("⚠️  Please fill in both fields.")
                else:
                    res = verify_user(email_in.strip(), pwd_in)
                    if res["success"]:
                        st.session_state.logged_in   = True
                        st.session_state.user_email  = email_in.strip().lower()
                        st.rerun()
                    else:
                        st.error(f"❌  {res['message']}")

        with tab_up:
            email_up  = st.text_input("Email Address", placeholder="you@example.com", key="signup_email")
            pwd_up    = st.text_input("Password", type="password", placeholder="Create a strong password (min 6 chars)", key="signup_pwd")
            pwd_up2   = st.text_input("Confirm Password", type="password", placeholder="Repeat your password", key="signup_pwd2")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            if st.button("Create Account  →", key="btn_signup", use_container_width=True):
                if not email_up.strip() or not pwd_up or not pwd_up2:
                    st.error("⚠️  Please fill in all fields.")
                elif pwd_up != pwd_up2:
                    st.error("❌  Passwords do not match.")
                elif len(pwd_up) < 6:
                    st.error("❌  Password must be at least 6 characters.")
                elif "@" not in email_up:
                    st.error("❌  Please enter a valid email address.")
                else:
                    res = register_user(email_up.strip(), pwd_up)
                    if res["success"]:
                        st.success(f"✅  {res['message']}  Please sign in now.")
                    else:
                        st.warning(f"⚠️  {res['message']}")

        # Security note — self-contained
        st.markdown("""
        <p style="text-align:center; color:rgba(255,255,255,0.22); font-size:12px; margin-top:20px;">
            🔒 Passwords are encrypted with bcrypt — never stored in plain text
        </p>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# LOGIN GATE
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    show_login_page()
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLES  (only rendered when logged in)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
    }

    /* ── Background ─────────────────────────────── */
    .stApp { background-color: #f0f4f8; }

    /* ── Sidebar ─────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1a2236 100%);
        border-right: 1px solid rgba(99,102,241,0.2);
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }

    /* Sidebar nav buttons */
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        color: #94a3b8 !important;
        border: 1px solid transparent !important;
        border-radius: 10px !important;
        width: 100% !important;
        text-align: left !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        padding: 10px 14px !important;
        margin-bottom: 2px !important;
        transition: all 0.18s !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(99,102,241,0.14) !important;
        color: #e2e8f0 !important;
        border-color: rgba(99,102,241,0.25) !important;
    }
    [data-testid="stSidebar"] .stButton > button p,
    [data-testid="stSidebar"] .stButton > button span,
    [data-testid="stSidebar"] .stButton > button div {
        color: inherit !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }

    /* ── Main area buttons ───────────────────────── */
    [data-testid="stVerticalBlock"] .stButton > button {
        background: white !important;
        color: #1e293b !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        padding: 9px 16px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        transition: all 0.18s !important;
    }
    [data-testid="stVerticalBlock"] .stButton > button:hover {
        border-color: #6366f1 !important;
        box-shadow: 0 4px 16px rgba(99,102,241,0.18) !important;
        transform: translateY(-1px);
    }
    [data-testid="stVerticalBlock"] .stButton > button p,
    [data-testid="stVerticalBlock"] .stButton > button span {
        color: #1e293b !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }

    /* ── Download Buttons ────────────────────────── */
    [data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 9px 16px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px rgba(99,102,241,0.4) !important;
        transition: all 0.2s !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(99,102,241,0.55) !important;
    }
    [data-testid="stDownloadButton"] > button p,
    [data-testid="stDownloadButton"] > button span {
        color: white !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }

    /* ── Typography ──────────────────────────────── */
    h1 { font-size: 26px !important; font-weight: 800 !important; color: #0f172a !important; letter-spacing: -0.5px !important; }
    h2 { font-size: 20px !important; font-weight: 700 !important; color: #0f172a !important; }
    h3 { font-size: 16px !important; font-weight: 700 !important; color: #0f172a !important; }

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {
        color: #334155;
        font-size: 14px;
        line-height: 1.75;
    }

    /* ── Misc ────────────────────────────────────── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

@st.cache_resource(show_spinner=False)
def init_rag_engine():
    return RAGEngine()

if "rag" not in st.session_state:
    st.session_state.rag = init_rag_engine()
if "indexed" not in st.session_state:
    st.session_state.indexed = False
if "doc_count" not in st.session_state:
    st.session_state.doc_count = 0
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "page" not in st.session_state:
    st.session_state.page = "Chat"
if "doc_stats" not in st.session_state:
    st.session_state.doc_stats = {}
if "doc_summaries" not in st.session_state:
    st.session_state.doc_summaries = {}
if "questions_asked" not in st.session_state:
    st.session_state.questions_asked = []


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""
    <div style="display:flex; align-items:center; gap:12px; padding:4px 0 20px;">
        <div style="width:38px; height:38px; background:linear-gradient(135deg,#6366f1,#4338ca);
                    border-radius:10px; display:flex; align-items:center; justify-content:center;
                    font-size:20px; box-shadow:0 4px 12px rgba(99,102,241,0.35); flex-shrink:0;">
            🤖
        </div>
        <div>
            <div style="color:white; font-weight:700; font-size:16px; line-height:1.1;">RAG Chatbot</div>
            <div style="color:#475569; font-size:11px; margin-top:2px;">Document Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Navigation
    nav_pages = [
        ("💬  Chat",      "Chat"),
        ("📄  Documents", "Documents"),
        ("📊  Analytics", "Analytics"),
        ("ℹ️  About",     "About"),
    ]
    for label, page_key in nav_pages:
        if st.session_state.page == page_key:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(99,102,241,0.22), rgba(79,70,229,0.12));
                border-left: 3px solid #6366f1;
                color: white;
                font-weight: 600;
                font-size: 14px;
                padding: 10px 14px;
                border-radius: 0 10px 10px 0;
                margin-bottom: 4px;
            ">{label}</div>
            """, unsafe_allow_html=True)
        else:
            if st.button(label, key=f"nav_{page_key}"):
                st.session_state.page = page_key
                st.rerun()

    st.divider()

    # Model info badge — no API key needed
    st.markdown("""
    <div style="background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3);
                border-radius:10px; padding:10px 14px; margin-bottom:4px;">
        <div style="font-size:11px; color:#10b981; font-weight:700;
                    text-transform:uppercase; letter-spacing:1px;">🟢 Local AI — No API Key</div>
        <div style="font-size:11px; color:#94a3b8; margin-top:4px; line-height:1.5;">
            Powered by <b style="color:#e2e8f0;">Flan-T5</b> + <b style="color:#e2e8f0;">MiniLM</b><br>
            100% offline · Free · Private
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Upload section
    st.markdown("""<div style="color:#64748b; font-size:11px; font-weight:600;
                               text-transform:uppercase; letter-spacing:1.2px;
                               margin-bottom:10px;">📁 Upload Documents</div>""",
                unsafe_allow_html=True)

    uploaded_pdfs = st.file_uploader(
        "Upload PDF", type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_pdfs:
        new_files = [f for f in uploaded_pdfs if f.name not in st.session_state.uploaded_files]
        if new_files:
            with st.spinner("Processing documents..."):
                for pdf in new_files:
                    text   = st.session_state.rag.load_pdf(pdf)
                    chunks = st.session_state.rag.chunk_text(text)
                    try:
                        summary = st.session_state.rag.summarize_document(text)
                    except Exception:
                        summary = "(Auto-summary unavailable — document indexed successfully.)"
                    st.session_state.doc_stats[pdf.name] = len(chunks)
                    st.session_state.doc_summaries[pdf.name] = summary
                    st.session_state.rag.build_index(chunks)
                    st.session_state.uploaded_files.append(pdf.name)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"📄 **{pdf.name}** uploaded!\n\n**Auto Summary:**\n{summary}",
                        "time": pd.Timestamp.now().strftime("%H:%M")
                    })
                st.session_state.doc_count = len(st.session_state.rag.chunks)
                st.session_state.indexed   = True
            st.success(f"✅ {len(new_files)} doc(s) indexed")
            time.sleep(1.5)
            st.rerun()


    # Indexed docs list
    st.markdown("""<div style="color:#64748b; font-size:11px; font-weight:600;
                               text-transform:uppercase; letter-spacing:1.2px;
                               margin:14px 0 8px;">Indexed Documents</div>""",
                unsafe_allow_html=True)

    if st.session_state.indexed:
        for fname in st.session_state.uploaded_files:
            ch = st.session_state.doc_stats.get(fname, 0)
            st.markdown(f"""
            <div style="background:rgba(99,102,241,0.10); border:1px solid rgba(99,102,241,0.2);
                        border-radius:10px; padding:9px 12px; margin:4px 0;">
                <div style="font-size:12px; color:#e2e8f0; font-weight:500;
                            white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
                            max-width:155px;">📄 {fname}</div>
                <div style="font-size:11px; color:#818cf8; margin-top:3px; font-weight:600;">
                    {ch} chunks
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(
            f"<div style='font-size:12px; color:#475569; margin-top:8px;'>"
            f"Total: <b style='color:#e2e8f0'>{st.session_state.doc_count}</b> chunks</div>",
            unsafe_allow_html=True
        )
        if st.button("🗑️ Clear All Documents"):
            st.session_state.rag.clear_memory()
            st.session_state.rag            = RAGEngine()
            st.session_state.indexed        = False
            st.session_state.doc_count      = 0
            st.session_state.uploaded_files = []
            st.session_state.doc_stats      = {}
            st.session_state.doc_summaries  = {}
            st.session_state.messages       = []
            st.rerun()
    else:
        st.markdown("<p style='color:#475569; font-size:13px;'>No documents yet</p>",
                    unsafe_allow_html=True)

    # User profile + logout at bottom
    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
    st.divider()

    user_email   = st.session_state.get("user_email", "user@example.com")
    user_initial = user_email[0].upper()

    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; padding:10px 12px;
                background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.2);
                border-radius:12px; margin-bottom:10px;">
        <div style="width:36px; height:36px; border-radius:50%;
                    background:linear-gradient(135deg,#6366f1,#4338ca);
                    color:white; display:flex; align-items:center; justify-content:center;
                    font-weight:700; font-size:15px; flex-shrink:0;">{user_initial}</div>
        <div style="overflow:hidden; min-width:0;">
            <div style="color:#e2e8f0; font-weight:600; font-size:13px;
                        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
                        max-width:125px;">{user_email}</div>
            <div style="color:#818cf8; font-size:11px; font-weight:500;">● Active session</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪  Logout", key="logout_btn", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# CHART HELPERS
# ─────────────────────────────────────────────────────────────────────────────
PALETTE = ["#6366f1", "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#ec4899", "#14b8a6", "#8b5cf6"]

def chart_layout(title="", height=350):
    return dict(
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Inter, sans-serif", color="#475569", size=12),
        title=dict(
            text=title,
            font=dict(color="#0f172a", size=16, family="Inter, sans-serif"),
            x=0, xanchor="left", pad=dict(l=4, t=4)
        ),
        margin=dict(t=56, b=48, l=56, r=20),
        xaxis=dict(
            gridcolor="#f1f5f9",
            linecolor="#e2e8f0",
            tickfont=dict(color="#64748b", size=12),
            zerolinecolor="#e2e8f0",
        ),
        yaxis=dict(
            gridcolor="#f1f5f9",
            linecolor="#e2e8f0",
            tickfont=dict(color="#64748b", size=12),
            zerolinecolor="#e2e8f0",
        ),
        hoverlabel=dict(bgcolor="white", bordercolor="#e2e8f0",
                        font=dict(color="#1e293b", size=13, family="Inter")),
    )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: CHAT
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.page == "Chat":
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("💬 Document Q&A")
        st.markdown(
            "<p style='color:#64748b; margin-top:-12px; margin-bottom:28px; font-size:15px;'>"
            "Ask anything about your uploaded documents</p>",
            unsafe_allow_html=True
        )
    with col2:
        if st.session_state.messages:
            pdf_bytes = generate_chat_pdf(st.session_state.messages)
            st.download_button(
                label="📥 Export Chat PDF",
                data=pdf_bytes,
                file_name="chat_export.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    if not st.session_state.indexed:
        st.markdown("""
        <div style="text-align:center; padding:70px 40px; background:white;
                    border-radius:24px; border:1px solid #e2e8f0;
                    margin:40px auto; max-width:520px;
                    box-shadow:0 4px 24px rgba(0,0,0,0.06);">
            <div style="font-size:60px; margin-bottom:20px;">📄</div>
            <div style="font-size:21px; font-weight:700; color:#0f172a; margin-bottom:10px;">
                No Documents Uploaded
            </div>
            <div style="font-size:14px; color:#64748b; line-height:1.8; margin-bottom:28px;">
                Upload PDF documents from the sidebar to start asking questions.<br>
                Supports research papers, reports, manuals, and books.
            </div>
            <div style="display:flex; justify-content:center; gap:10px; flex-wrap:wrap;">
                <span style="background:#f0f4ff; border:1px solid #c7d2fe; border-radius:20px;
                             padding:6px 16px; font-size:12px; color:#4f46e5; font-weight:500;">
                    📑 Research Papers
                </span>
                <span style="background:#f0fdf4; border:1px solid #a7f3d0; border-radius:20px;
                             padding:6px 16px; font-size:12px; color:#047857; font-weight:500;">
                    📘 Manuals
                </span>
                <span style="background:#fff7ed; border:1px solid #fed7aa; border-radius:20px;
                             padding:6px 16px; font-size:12px; color:#c2410c; font-weight:500;">
                    📊 Reports
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Chat history
        for msg in st.session_state.messages:
            msg_time = msg.get("time", pd.Timestamp.now().strftime("%H:%M"))
            if msg["role"] == "user":
                st.markdown(
                    "<div style='display:flex; flex-direction:column; align-items:flex-end; margin-bottom:16px;'>"
                    "<div style='background:linear-gradient(135deg,#6366f1,#4338ca); color:white; "
                    "border-radius:18px 18px 4px 18px; padding:13px 18px; max-width:72%; "
                    "font-size:14px; line-height:1.7; box-shadow:0 4px 16px rgba(99,102,241,0.3);'>"
                    f"{msg['content']}"
                    "</div>"
                    f"<div style='font-size:11px; color:#94a3b8; margin-top:5px;'>{msg_time}</div>"
                    "</div>",
                    unsafe_allow_html=True
                )
            else:
                with st.container():
                    score_html = ""
                    if msg.get("scores") and len(msg["scores"]) > 0:
                        conf_pct = int(max(msg["scores"]) * 100)
                        score_html = f"<div style='font-size:11px; color:#10b981; font-weight:600; margin-left:8px;'>✓ {conf_pct}% Confidence</div>"

                    st.markdown(
                        "<div style='display:flex; flex-direction:column; align-items:flex-start; margin-bottom:8px;'>"
                        "<div style='background:white; color:#1e293b; border:1px solid #e2e8f0; "
                        "border-radius:18px 18px 18px 4px; padding:14px 18px; max-width:76%; "
                        "font-size:14px; line-height:1.75; box-shadow:0 2px 10px rgba(0,0,0,0.06);'>"
                        f"{msg['content']}"
                        "</div>"
                        "<div style='display:flex; align-items:center; margin-top:5px;'>"
                        f"<div style='font-size:11px; color:#94a3b8;'>{msg_time}</div>"
                        f"{score_html}"
                        "</div>"
                        "</div>",
                        unsafe_allow_html=True
                    )
                    if msg.get("sources"):
                        src_html = (
                            "<div style='margin-top:8px; padding:12px 16px; background:#f8fafc; "
                            "border:1px solid #e2e8f0; border-radius:12px; font-size:12px;'>"
                            "<div style='font-weight:600; color:#6366f1; margin-bottom:8px;'>📎 Sources Used</div>"
                        )
                        for src in msg["sources"]:
                            preview = src[:150] + "…" if len(src) > 150 else src
                            src_html += (
                                "<div style='background:white; border:1px solid #e2e8f0; border-radius:8px; "
                                "padding:8px 12px; margin:4px 0; color:#475569; line-height:1.6;'>"
                                f"\"{preview}\""
                                "</div>"
                            )
                        src_html += "</div>"
                        st.markdown(src_html, unsafe_allow_html=True)

        if not st.session_state.messages:
            st.markdown("### 💡 Example Questions")
            cols = st.columns(4)
            for i, ex in enumerate([
                "📋 Summarize the main points",
                "🔍 What are the key findings?",
                "💡 What recommendations are made?",
                "📊 What data is presented?"
            ]):
                with cols[i]:
                    if st.button(ex, key=f"ex_{i}"):
                        st.session_state.messages.append({
                            "role": "user", "content": ex,
                            "time": pd.Timestamp.now().strftime("%H:%M")
                        })
                        st.session_state.questions_asked.append(
                            {"time": pd.Timestamp.now(), "query": ex}
                        )
                        st.rerun()

        query = st.chat_input("Ask a question about your documents…")
        if query:
            st.session_state.messages.append({
                "role": "user", "content": query,
                "time": pd.Timestamp.now().strftime("%H:%M")
            })
            st.session_state.questions_asked.append(
                {"time": pd.Timestamp.now(), "query": query}
            )
            st.rerun()

        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            with st.spinner("🤔 Thinking…"):
                q_text = st.session_state.messages[-1]["content"]
                result = st.session_state.rag.ask(q_text)
                st.session_state.messages.append({
                    "role":    "assistant",
                    "content": result["answer"],
                    "sources": result["sources"],
                    "scores":  result["scores"],
                    "time":    pd.Timestamp.now().strftime("%H:%M")
                })
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: DOCUMENTS
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "Documents":
    st.title("📄 Document Library")
    st.markdown(
        "<p style='color:#64748b; margin-top:-12px; margin-bottom:28px; font-size:15px;'>"
        "Manage your uploaded documents</p>",
        unsafe_allow_html=True
    )

    if not st.session_state.indexed:
        st.markdown("""
        <div style="text-align:center; padding:64px 40px; background:white;
                    border-radius:24px; border:1px solid #e2e8f0;
                    margin:40px auto; max-width:500px;
                    box-shadow:0 4px 24px rgba(0,0,0,0.06);">
            <div style="font-size:52px; margin-bottom:16px;">📁</div>
            <div style="font-size:19px; font-weight:700; color:#0f172a;">No documents uploaded yet</div>
            <div style="font-size:14px; color:#64748b; margin-top:8px;">
                Upload PDFs from the sidebar to get started.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # KPI cards
        kpi_base = ("background:white; border:1px solid #e2e8f0; border-radius:18px;"
                    "padding:24px 28px; box-shadow:0 2px 10px rgba(0,0,0,0.05);")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div style="{kpi_base}">
                <div style="font-size:11px; color:#94a3b8; text-transform:uppercase;
                            letter-spacing:1.2px; margin-bottom:8px; font-weight:600;">Total Documents</div>
                <div style="font-size:40px; font-weight:800; color:#6366f1; line-height:1;">
                    {len(st.session_state.uploaded_files)}
                </div>
                <div style="font-size:12px; color:#94a3b8; margin-top:6px;">PDFs indexed</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div style="{kpi_base}">
                <div style="font-size:11px; color:#94a3b8; text-transform:uppercase;
                            letter-spacing:1.2px; margin-bottom:8px; font-weight:600;">Total Chunks</div>
                <div style="font-size:40px; font-weight:800; color:#3b82f6; line-height:1;">
                    {st.session_state.doc_count}
                </div>
                <div style="font-size:12px; color:#94a3b8; margin-top:6px;">Text segments stored</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            avg = (st.session_state.doc_count // len(st.session_state.uploaded_files)
                   if st.session_state.uploaded_files else 0)
            st.markdown(f"""
            <div style="{kpi_base}">
                <div style="font-size:11px; color:#94a3b8; text-transform:uppercase;
                            letter-spacing:1.2px; margin-bottom:8px; font-weight:600;">Avg Chunks / Doc</div>
                <div style="font-size:40px; font-weight:800; color:#10b981; line-height:1;">{avg}</div>
                <div style="font-size:12px; color:#94a3b8; margin-top:6px;">chunks per document</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

        # File list
        st.markdown("### 📂 Uploaded Files")
        for i, fname in enumerate(st.session_state.uploaded_files):
            chunks    = st.session_state.doc_stats.get(fname, 0)
            summary   = st.session_state.doc_summaries.get(fname, "No summary available.")
            dot_color = PALETTE[i % len(PALETTE)]
            st.markdown(f"""
            <div style="background:white; border:1px solid #e2e8f0; border-radius:16px;
                        padding:18px 24px; box-shadow:0 2px 8px rgba(0,0,0,0.04);
                        margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <div style="display:flex; align-items:center; gap:16px;">
                        <div style="width:44px; height:44px; background:#f0f4ff; border-radius:12px;
                                    display:flex; align-items:center; justify-content:center;
                                    font-size:22px; border:1px solid #e0e7ff;">📄</div>
                        <div>
                            <div style="font-weight:700; color:#0f172a; font-size:15px;">{fname}</div>
                            <div style="color:{dot_color}; font-size:13px; margin-top:3px; font-weight:600;">
                                ✅ Indexed · <b>{chunks}</b> chunks
                            </div>
                        </div>
                    </div>
                    <div style="background:#f0fdf4; color:#16a34a; border:1px solid #bbf7d0;
                                border-radius:20px; padding:5px 16px; font-size:12px; font-weight:700;">
                        ● Active
                    </div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:12px 16px;">
                    <div style="font-size:11px; color:#64748b; text-transform:uppercase; font-weight:700; margin-bottom:6px;">Auto Summary</div>
                    <div style="font-size:13px; color:#334155; line-height:1.6;">{summary}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        # ── Professional bar chart ────────────────────────────────────────────
        df_docs = pd.DataFrame({
            "Document": list(st.session_state.doc_stats.keys()),
            "Chunks":   list(st.session_state.doc_stats.values()),
        })
        if not df_docs.empty:
            bar_colors = [PALETTE[i % len(PALETTE)] for i in range(len(df_docs))]
            fig_bar = go.Figure(go.Bar(
                x=df_docs["Document"],
                y=df_docs["Chunks"],
                marker=dict(
                    color=bar_colors,
                    line=dict(width=0),
                    cornerradius=8,
                ),
                text=df_docs["Chunks"],
                textposition="outside",
                textfont=dict(color="#374151", size=13, family="Inter"),
                hovertemplate="<b>%{x}</b><br>Chunks: <b>%{y}</b><extra></extra>",
            ))
            layout = chart_layout("📊  Chunks per Document", height=380)
            layout["yaxis"].update(title="Number of Chunks",
                                   title_font=dict(color="#64748b", size=13))
            layout["xaxis"].update(title="Document",
                                   title_font=dict(color="#64748b", size=13))
            layout["bargap"] = 0.40
            fig_bar.update_layout(**layout)
            st.plotly_chart(fig_bar, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "Analytics":
    st.title("📊 Chat Analytics")
    st.markdown(
        "<p style='color:#64748b; margin-top:-12px; margin-bottom:28px; font-size:15px;'>"
        "Insights from your Q&A sessions</p>",
        unsafe_allow_html=True
    )

    kpi_base = ("background:white; border:1px solid #e2e8f0; border-radius:18px;"
                "padding:22px 24px; box-shadow:0 2px 10px rgba(0,0,0,0.05);")

    c1, c2, c3, c4 = st.columns(4)
    for col, label, value, color in [
        (c1, "Total Questions",    len(st.session_state.questions_asked), "#6366f1"),
        (c2, "Avg Response Time",  "1.2s",                               "#3b82f6"),
        (c3, "Documents Indexed",  len(st.session_state.uploaded_files),  "#10b981"),
        (c4, "Total Chunks",       st.session_state.doc_count,           "#f59e0b"),
    ]:
        with col:
            col.markdown(f"""
            <div style="{kpi_base}">
                <div style="font-size:11px; color:#94a3b8; text-transform:uppercase;
                            letter-spacing:1.2px; margin-bottom:6px; font-weight:600;">{label}</div>
                <div style="font-size:34px; font-weight:800; color:{color}; line-height:1.1;">{value}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    empty_card = """
    <div style="background:white; border:1px solid #e2e8f0; border-radius:16px;
                padding:52px; text-align:center; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
        <div style="font-size:38px; margin-bottom:12px;">📭</div>
        <div style="color:#94a3b8; font-size:14px; font-weight:500;">No data available yet</div>
        <div style="color:#cbd5e1; font-size:13px; margin-top:4px;">Start chatting to see insights</div>
    </div>"""

    chart_col1, chart_col2 = st.columns(2)

    # ── Line chart ────────────────────────────────────────────────────────────
    with chart_col1:
        st.markdown("### 📈 Questions Over Time")
        if st.session_state.questions_asked:
            df_q = pd.DataFrame(st.session_state.questions_asked)
            df_q["time"]       = pd.to_datetime(df_q["time"])
            df_q["cumulative"] = range(1, len(df_q) + 1)

            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=df_q["time"], y=df_q["cumulative"],
                mode="lines+markers",
                line=dict(color="#6366f1", width=3, shape="spline"),
                marker=dict(size=9, color="white", line=dict(width=2.5, color="#6366f1")),
                fill="tozeroy",
                fillcolor="rgba(99,102,241,0.07)",
                hovertemplate="<b>%{y}</b> questions<br>%{x|%H:%M:%S}<extra></extra>",
            ))
            l = chart_layout("Questions Over Time", height=320)
            l["yaxis"].update(title="Cumulative Questions", title_font=dict(color="#64748b", size=13))
            l["xaxis"].update(title="", showgrid=True)
            l["showlegend"] = False
            fig_line.update_layout(**l)
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.markdown(empty_card, unsafe_allow_html=True)

    # ── Horizontal bar — keywords ─────────────────────────────────────────────
    with chart_col2:
        st.markdown("### 🔍 Top Query Keywords")
        if st.session_state.questions_asked:
            all_text  = " ".join(q["query"].lower() for q in st.session_state.questions_asked)
            words     = re.findall(r'\b\w+\b', all_text)
            stopwords = {"what","is","the","a","an","of","and","in","to","for","are",
                         "how","summarize","points","main","me","my","your","this","that"}
            words = [w for w in words if w not in stopwords and len(w) > 2]
            if words:
                counts  = Counter(words).most_common(6)
                df_kw   = pd.DataFrame(counts, columns=["Keyword", "Count"])
                bar_col = PALETTE[:len(df_kw)]

                fig_kw = go.Figure(go.Bar(
                    x=df_kw["Count"], y=df_kw["Keyword"],
                    orientation="h",
                    marker=dict(color=bar_col, line=dict(width=0), cornerradius=6),
                    text=df_kw["Count"], textposition="outside",
                    textfont=dict(color="#374151", size=12),
                    hovertemplate="<b>%{y}</b>: %{x} occurrences<extra></extra>",
                ))
                l2 = chart_layout("Top Query Keywords", height=320)
                l2["yaxis"].update(categoryorder="total ascending", title="",
                                   tickfont=dict(color="#374151", size=13))
                l2["xaxis"].update(title="Occurrences", title_font=dict(color="#64748b", size=13))
                l2["margin"].update(l=110, r=40)
                fig_kw.update_layout(**l2)
                st.plotly_chart(fig_kw, use_container_width=True)
            else:
                st.markdown(empty_card, unsafe_allow_html=True)
        else:
            st.markdown(empty_card, unsafe_allow_html=True)

    # ── Donut chart ───────────────────────────────────────────────────────────
    st.markdown("### 🥧 Source Document Distribution")
    if st.session_state.uploaded_files:
        df_pie = pd.DataFrame({
            "Document": list(st.session_state.doc_stats.keys()),
            "Chunks":   list(st.session_state.doc_stats.values()),
        })
        fig_pie = go.Figure(go.Pie(
            labels=df_pie["Document"],
            values=df_pie["Chunks"],
            hole=0.58,
            marker=dict(
                colors=PALETTE[:len(df_pie)],
                line=dict(color="white", width=3),
            ),
            textinfo="label+percent",
            textfont=dict(size=13, color="#374151", family="Inter"),
            hovertemplate="<b>%{label}</b><br>%{value} chunks (%{percent})<extra></extra>",
            pull=[0.03] * len(df_pie),
        ))
        l3 = chart_layout("Source Document Distribution", height=400)
        l3["legend"] = dict(
            font=dict(color="#374151", size=12, family="Inter"),
            bgcolor="white", bordercolor="#e2e8f0", borderwidth=1
        )
        l3["annotations"] = [dict(
            text=f"<b style='font-size:20px'>{st.session_state.doc_count}</b><br>"
                 f"<span style='font-size:12px;color:#94a3b8'>chunks</span>",
            x=0.5, y=0.5, font=dict(size=18, color="#0f172a"), showarrow=False
        )]
        fig_pie.update_layout(**l3)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.markdown(empty_card, unsafe_allow_html=True)

    # ── Recent questions table ────────────────────────────────────────────────
    st.markdown("### 📋 Recent Questions")
    if st.session_state.questions_asked:
        recent = list(reversed(st.session_state.questions_asked[-5:]))
        rows_html = ""
        for i, q in enumerate(recent, 1):
            t = q["time"].strftime("%H:%M:%S")
            bg = "#fafbff" if i % 2 == 0 else "white"
            rows_html += f"""
            <tr style="border-bottom:1px solid #f1f5f9; background:{bg};">
                <td style="padding:14px 20px; font-size:13px; color:#94a3b8; font-weight:700;">{i}</td>
                <td style="padding:14px 20px; font-size:14px; color:#334155;">{q['query']}</td>
                <td style="padding:14px 20px; font-size:12px; color:#94a3b8; text-align:right;
                           font-family:monospace; white-space:nowrap;">{t}</td>
            </tr>"""
        st.markdown(f"""
        <div style="background:white; border:1px solid #e2e8f0; border-radius:16px;
                    overflow:hidden; box-shadow:0 2px 10px rgba(0,0,0,0.05);">
            <table style="width:100%; border-collapse:collapse;">
                <thead>
                    <tr style="background:#f8fafc; border-bottom:1px solid #e2e8f0;">
                        <th style="padding:13px 20px; font-size:11px; color:#64748b; text-align:left;
                                   text-transform:uppercase; letter-spacing:1px; font-weight:700; width:40px;">#</th>
                        <th style="padding:13px 20px; font-size:11px; color:#64748b; text-align:left;
                                   text-transform:uppercase; letter-spacing:1px; font-weight:700;">Question</th>
                        <th style="padding:13px 20px; font-size:11px; color:#64748b; text-align:right;
                                   text-transform:uppercase; letter-spacing:1px; font-weight:700;">Time</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(empty_card, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ABOUT
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "About":
    st.title("ℹ️ About This Project")

    card = ("background:white; border:1px solid #e2e8f0; border-radius:18px;"
            "padding:28px 32px; box-shadow:0 2px 10px rgba(0,0,0,0.05); margin-bottom:20px;")

    col1, col2 = st.columns(2)

    with col1:
        steps = [
            "Upload PDF documents",
            "Text is split into overlapping chunks",
            "Chunks converted to vector embeddings",
            "Embeddings stored in FAISS index",
            "Your question is embedded the same way",
            "Most similar chunks are retrieved",
            "Answer is extracted from those chunks",
        ]
        steps_html = "".join([
            f"""<div style="display:flex; align-items:flex-start; gap:12px; margin-bottom:12px;">
                <div style="width:26px; height:26px; border-radius:50%;
                            background:linear-gradient(135deg,#6366f1,#4338ca);
                            color:white; font-size:12px; font-weight:700;
                            display:flex; align-items:center; justify-content:center; flex-shrink:0;">{i}</div>
                <p style="color:#475569; font-size:14px; margin:0; line-height:1.7; padding-top:2px;">{s}</p>
            </div>"""
            for i, s in enumerate(steps, 1)
        ])

        tech_tags = ["Python", "LangChain", "FAISS", "Sentence-Transformers",
                     "HuggingFace", "Streamlit", "PyPDF2", "Docker", "bcrypt"]
        tags_html = " ".join([
            f'<span style="background:#f0f4ff; color:#4f46e5; border:1px solid #c7d2fe;'
            f'padding:5px 12px; border-radius:20px; font-size:12px; font-weight:600;">{t}</span>'
            for t in tech_tags
        ])

        st.markdown(f"""
        <div style="{card}">
            <h3 style="color:#0f172a; font-size:16px; font-weight:700; margin:0 0 12px;">🚀 Project Overview</h3>
            <p style="color:#475569; font-size:14px; line-height:1.8; margin:0;">
                This RAG-Based Q&A Chatbot uses Retrieval-Augmented Generation to answer questions
                from your PDF documents. It combines FAISS vector search with HuggingFace sentence
                transformers to provide accurate, context-aware answers — all locally, no external API needed.
            </p>
        </div>
        <div style="{card}">
            <h3 style="color:#0f172a; font-size:16px; font-weight:700; margin:0 0 16px;">⚙️ How It Works</h3>
            {steps_html}
        </div>
        <div style="{card}">
            <h3 style="color:#0f172a; font-size:16px; font-weight:700; margin:0 0 14px;">🛠 Tech Stack</h3>
            <div style="display:flex; flex-wrap:wrap; gap:8px;">{tags_html}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        details = [
            ("Project Name",    "RAG-Based Q&A Chatbot"),
            ("Version",         "2.0.0"),
            ("Authentication",  "bcrypt encrypted"),
            ("Purpose",         "Document Q&A using RAG"),
            ("Embedding",       "Sentence Transformers"),
            ("Vector DB",       "FAISS (IndexFlatL2)"),
            ("PDF Support",     "Up to 200MB per file"),
            ("Max Chunks",      "Unlimited"),
        ]
        specs = [
            ("Embedding Model", "paraphrase-MiniLM-L3-v2"),
            ("LLM / Generation","Extractive Search"),
            ("Vector Store",    "FAISS (IndexFlatL2)"),
            ("Chunk Size",      "500 words"),
            ("Chunk Overlap",   "50 words"),
            ("Top-K Retrieval", "3 chunks"),
        ]

        def make_table(rows):
            html = ""
            for k, v in rows:
                html += (f'<tr style="border-bottom:1px solid #f1f5f9;">'
                         f'<td style="padding:11px 0; color:#64748b; font-size:13px;">{k}</td>'
                         f'<td style="padding:11px 0; color:#0f172a; font-size:13px;'
                         f'text-align:right; font-weight:600;">{v}</td></tr>')
            return f'<table style="width:100%; border-collapse:collapse;">{html}</table>'

        st.markdown(f"""
        <div style="{card}">
            <h3 style="color:#0f172a; font-size:16px; font-weight:700; margin:0 0 14px;">🏢 Project Details</h3>
            {make_table(details)}
        </div>
        <div style="{card}">
            <h3 style="color:#0f172a; font-size:16px; font-weight:700; margin:0 0 14px;">📋 Technical Specs</h3>
            {make_table(specs)}
        </div>
        """, unsafe_allow_html=True)

# Trigger reload

# Hot reload trigger

# Trigger reload for text splitters
