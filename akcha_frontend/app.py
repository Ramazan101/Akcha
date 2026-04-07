import streamlit as st

st.set_page_config(
    page_title="Akcha AI — Финансовый Ассистент",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Inject global CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500&display=swap');

/* ── Reset & Variables ── */
:root {
    --bg:        #0a0e1a;
    --surface:   #111827;
    --card:      #151d2e;
    --border:    #1e2d45;
    --accent:    #00d4aa;
    --accent2:   #6366f1;
    --accent3:   #f59e0b;
    --danger:    #ef4444;
    --success:   #10b981;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --font-head: 'Syne', sans-serif;
    --font-mono: 'Space Mono', monospace;
    --font-body: 'Inter', sans-serif;
}

/* ── Base ── */
html, body, [data-testid="stApp"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}

[data-testid="stApp"]::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background:
        radial-gradient(ellipse 60% 40% at 20% 10%, rgba(0,212,170,.08) 0%, transparent 60%),
        radial-gradient(ellipse 50% 60% at 80% 80%, rgba(99,102,241,.07) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { font-family: var(--font-body) !important; }

/* ── Headings ── */
h1, h2, h3, h4 {
    font-family: var(--font-head) !important;
    color: var(--text) !important;
}

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] > div,
[data-testid="stTextArea"] textarea,
[data-testid="stDateInput"] input {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
    font-family: var(--font-body) !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(0,212,170,.15) !important;
}

/* ── Primary Button ── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, var(--accent), #00a885) !important;
    color: #0a0e1a !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: var(--font-head) !important;
    font-weight: 700 !important;
    letter-spacing: .05em !important;
    padding: .6rem 1.4rem !important;
    transition: all .2s ease !important;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 20px rgba(0,212,170,.3) !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 1.2rem !important;
}
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size:.8rem !important; }
[data-testid="stMetricValue"] { font-family: var(--font-head) !important; font-size:1.8rem !important; }

/* ── Tabs ── */
[data-testid="stTabs"] [role="tab"] {
    font-family: var(--font-head) !important;
    color: var(--muted) !important;
    font-weight: 600 !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}

/* ── Dataframes ── */
[data-testid="stDataFrame"] { border-radius: 12px !important; overflow: hidden !important; }

/* ── Alerts ── */
[data-testid="stAlert"] { border-radius: 12px !important; border: none !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* ── Chat ── */
.chat-msg { display:flex; gap:12px; margin-bottom:16px; animation: fadeUp .3s ease; }
.chat-msg.user { flex-direction: row-reverse; }
.chat-bubble {
    max-width: 72%;
    padding: .75rem 1.1rem;
    border-radius: 18px;
    font-size: .9rem;
    line-height: 1.6;
}
.chat-msg.ai .chat-bubble {
    background: var(--card);
    border: 1px solid var(--border);
    border-bottom-left-radius: 4px;
    color: var(--text);
}
.chat-msg.user .chat-bubble {
    background: linear-gradient(135deg, var(--accent2), #4f46e5);
    border-bottom-right-radius: 4px;
    color: white;
}
.chat-avatar {
    width: 36px; height: 36px;
    border-radius: 50%;
    display:flex; align-items:center; justify-content:center;
    font-size: 1rem; flex-shrink:0;
}
.ai-avatar { background: rgba(0,212,170,.15); border: 1px solid var(--accent); }
.user-avatar { background: rgba(99,102,241,.2); border: 1px solid var(--accent2); }

@keyframes fadeUp {
    from { opacity:0; transform: translateY(8px); }
    to   { opacity:1; transform: translateY(0); }
}

/* ── Custom cards ── */
.akcha-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}
.akcha-card-title {
    font-family: var(--font-head);
    font-size: .75rem;
    text-transform: uppercase;
    letter-spacing: .1em;
    color: var(--muted);
    margin-bottom: .5rem;
}
.akcha-card-value {
    font-family: var(--font-head);
    font-size: 2rem;
    font-weight: 800;
    color: var(--accent);
}

.insight-card {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    padding: .9rem 1.1rem;
    border-radius: 12px;
    margin-bottom:.6rem;
    font-size:.88rem;
    line-height:1.5;
}
.insight-success { background: rgba(16,185,129,.1); border-left: 3px solid var(--success); }
.insight-warning { background: rgba(245,158,11,.1); border-left: 3px solid var(--accent3); }
.insight-danger  { background: rgba(239,68,68,.1);  border-left: 3px solid var(--danger); }

.goal-bar-wrap {
    background: var(--border);
    border-radius: 99px;
    height: 8px;
    overflow: hidden;
    margin: .5rem 0;
}
.goal-bar-fill {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    transition: width .6s ease;
}

.logo-text {
    font-family: var(--font-head);
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.logo-sub {
    font-family: var(--font-mono);
    font-size: .65rem;
    color: var(--muted);
    letter-spacing: .12em;
    text-transform: uppercase;
}

.pill {
    display: inline-block;
    padding: .2rem .7rem;
    border-radius: 99px;
    font-size: .72rem;
    font-family: var(--font-mono);
    font-weight: 700;
    letter-spacing: .05em;
}
.pill-green  { background: rgba(0,212,170,.15); color: var(--accent); border:1px solid rgba(0,212,170,.3); }
.pill-purple { background: rgba(99,102,241,.15); color: #818cf8; border:1px solid rgba(99,102,241,.3); }
.pill-amber  { background: rgba(245,158,11,.15); color: var(--accent3); border:1px solid rgba(245,158,11,.3); }
.pill-red    { background: rgba(239,68,68,.15); color: var(--danger); border:1px solid rgba(239,68,68,.3); }

div[data-testid="stForm"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 1.2rem !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Session state defaults ────────────────────────────────────────────────────
for key, val in {
    "token": None,
    "username": "",
    "chat_history": [],
    "api_base": "http://localhost:8000",
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ─── Import pages ─────────────────────────────────────────────────────────────
from pages_internal import auth, dashboard, expenses, goals, chat, settings_page

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="logo-text">💰 Akcha AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="logo-sub">Финансовый ассистент</div>', unsafe_allow_html=True)
    st.markdown("---")

    if st.session_state.token:
        st.markdown(f"**👤 {st.session_state.username}**")
        st.markdown('<span class="pill pill-green">● Онлайн</span>', unsafe_allow_html=True)
        st.markdown("")

        page = st.radio(
            "Навигация",
            ["🏠 Дашборд", "💳 Расходы", "🎯 Цели", "🤖 AI Чат", "⚙️ Настройки"],
            label_visibility="collapsed"
        )
        st.markdown("---")
        if st.button("🚪 Выйти", use_container_width=True):
            st.session_state.token = None
            st.session_state.username = ""
            st.session_state.chat_history = []
            st.rerun()
    else:
        page = "auth"

# ─── Routing ──────────────────────────────────────────────────────────────────
if not st.session_state.token:
    auth.render()
elif page == "🏠 Дашборд":
    dashboard.render()
elif page == "💳 Расходы":
    expenses.render()
elif page == "🎯 Цели":
    goals.render()
elif page == "🤖 AI Чат":
    chat.render()
elif page == "⚙️ Настройки":
    settings_page.render()