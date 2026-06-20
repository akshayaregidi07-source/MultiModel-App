import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from main import ask, MODELS, PRICES

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

# ── Per-model display metadata: friendly name, provider label, accent colour ──

META = {
    "openai/gpt-4o-mini":               {"name": "OpenAI GPT", "provider": "OpenAI",   "color": "#22C55E"},
    "deepseek/deepseek-chat":           {"name": "DeepSeek",   "provider": "DeepSeek", "color": "#3B82F6"},
    "meta-llama/llama-3.1-8b-instruct": {"name": "Meta Llama", "provider": "Meta",     "color": "#F97316"},
    "qwen/qwen-2.5-7b-instruct":        {"name": "Qwen",       "provider": "Alibaba",  "color": "#A855F7"},
}

# Order shown in the UI (matches the reference layout)
DISPLAY_ORDER = [
    "openai/gpt-4o-mini",
    "deepseek/deepseek-chat",
    "meta-llama/llama-3.1-8b-instruct",
    "qwen/qwen-2.5-7b-instruct",
]
# Keep only models that actually exist in MODELS, plus any extras from MODELS
ORDER = [m for m in DISPLAY_ORDER if m in MODELS] + [m for m in MODELS if m not in DISPLAY_ORDER]

def meta(m):
    return META.get(m, {"name": m.split("/")[-1], "provider": m.split("/")[0], "color": "#64748B"})

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(page_title="Multi-Model Comparison Tool", layout="wide")

# ── Global styles ─────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* ── Background with subtle grid ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #F4F7FB !important;
    background-image:
        linear-gradient(rgba(45,80,140,0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(45,80,140,0.035) 1px, transparent 1px);
    background-size: 44px 44px;
    font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
    color: #1E293B;
}
[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding-top: 2.5rem !important; max-width: 1280px; }

/* ── Brand tag ── */
.brand-row { display: flex; align-items: center; gap: 12px; margin-bottom: 22px; }
.brand-icon {
    width: 40px; height: 40px; border-radius: 12px;
    background: linear-gradient(135deg, #2563EB 0%, #0891B2 100%);
    display: flex; align-items: center; justify-content: center;
    color: white; font-size: 1.2rem; box-shadow: 0 4px 12px rgba(37,99,235,0.3);
}
.brand-name {
    font-size: 0.82rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: #64748B;
}

/* ── Title ── */
.page-title {
    font-size: 3.4rem; font-weight: 800; line-height: 1.05;
    letter-spacing: -1.5px; margin: 0 0 16px 0; color: #0F172A;
}
.page-title .grad {
    background: linear-gradient(100deg, #2563EB 0%, #0891B2 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.page-subtitle {
    font-size: 1.05rem; color: #64748B; max-width: 640px;
    line-height: 1.6; margin: 0 0 30px 0; font-weight: 400;
}

/* ── Input card (st.container border) ── */
div[data-testid="stVerticalBlockBorderWrapper"]:has(textarea) {
    background: #FFFFFF;
    border-radius: 24px !important;
    border: 1px solid #E7ECF3 !important;
    box-shadow: 0 16px 48px rgba(30,55,110,0.07);
    padding: 14px 20px !important;
}

/* ── Field labels ── */
.field-label {
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #94A3B8; margin-bottom: 8px;
}
.field-label .count { float: right; color: #64748B; font-weight: 600; letter-spacing: 0.04em; }

/* ── Text area ── */
textarea {
    background-color: #F8FAFC !important;
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 14px !important;
    color: #1E293B !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 1rem !important;
}
textarea:focus {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 4px rgba(37,99,235,0.1) !important;
}

/* ── Model toggle cards ── */
.model-card {
    border: 1.5px solid #E7ECF3; border-radius: 16px;
    padding: 16px 18px; margin-bottom: 6px;
    background: #FBFCFE; transition: all 0.15s; position: relative; overflow: hidden;
}
.model-card .dot {
    width: 10px; height: 10px; border-radius: 50%;
    display: inline-block; margin-right: 9px; vertical-align: middle;
}
.model-card .mname { font-weight: 700; font-size: 0.98rem; color: #1E293B; vertical-align: middle; }
.model-card .mprov { font-size: 0.78rem; color: #94A3B8; margin-top: 4px; margin-left: 19px; }

/* checkbox under each card */
[data-testid="stCheckbox"] { margin-top: -2px; }
[data-testid="stCheckbox"] label p { font-size: 0.78rem !important; color: #64748B !important; }

/* ── Compare button ── */
[data-testid="stButton"] > button {
    background: linear-gradient(100deg, #2563EB 0%, #0891B2 100%) !important;
    color: white !important; border: none !important;
    border-radius: 14px !important; padding: 14px 30px !important;
    font-size: 0.98rem !important; font-weight: 700 !important;
    width: 100% !important;
    box-shadow: 0 8px 22px rgba(37,99,235,0.28) !important;
    transition: transform 0.12s, box-shadow 0.12s !important;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 28px rgba(37,99,235,0.38) !important;
}

.footnote { font-size: 0.8rem; color: #94A3B8; }

/* ── Results section ── */
.results-title {
    font-size: 0.78rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: #94A3B8; margin: 34px 0 16px 0;
}

/* ── Hide chrome ── */
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="brand-row">
  <div class="brand-icon">✦</div>
  <div class="brand-name">Multi-Model Arena</div>
</div>
<div class="page-title">Multi-Model <span class="grad">Comparison Tool</span></div>
<div class="page-subtitle">Compare AI models by response quality, latency, and cost — side by side, through a single gateway.</div>
""", unsafe_allow_html=True)

# ── Input card ────────────────────────────────────────────────────────────────

with st.container(border=True):
    st.markdown('<div class="field-label">Your Prompt</div>', unsafe_allow_html=True)
    question = st.text_area(
        "Your prompt", label_visibility="collapsed",
        placeholder="Ask anything…  e.g.  Who is the President of India?",
        height=130,
    )

    count_ph = st.empty()

    # Model toggle cards in a row
    cols = st.columns(len(ORDER))
    selected_models = []
    for c, m in zip(cols, ORDER):
        info = meta(m)
        with c:
            st.markdown(f"""
            <div class="model-card">
                <span class="dot" style="background:{info['color']}"></span>
                <span class="mname">{info['name']}</span>
                <div class="mprov">{info['provider']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.checkbox("Compare", value=True, key=f"sel_{m}"):
                selected_models.append(m)

    count_ph.markdown(
        f'<div class="field-label">Models<span class="count">{len(selected_models)} selected</span></div>',
        unsafe_allow_html=True,
    )

    # Footer row: note + button
    f_left, f_right = st.columns([3, 1])
    with f_left:
        st.markdown(
            '<div class="footnote" style="margin-top:18px;">Runs all selected models in parallel · refresh to cancel</div>',
            unsafe_allow_html=True,
        )
    with f_right:
        compare = st.button("Compare Models  →")

# ── Run comparison ────────────────────────────────────────────────────────────

if compare:
    if not question.strip():
        st.warning("Please type a prompt before comparing.")
    elif not selected_models:
        st.warning("Please select at least one model.")
    else:
        results = []
        with st.spinner("Querying models…"):
            for m in selected_models:
                try:
                    results.append(ask(client, question, m))
                except Exception as exc:
                    results.append({"model": m, "error": str(exc)})
        st.session_state["results"] = results

# ── Results ───────────────────────────────────────────────────────────────────

def render_card(r):
    info = meta(r["model"])
    color = info["color"]
    failed = "error" in r

    badge = (
        f'<span style="background:#FEE2E2;color:#DC2626;border-radius:20px;padding:4px 12px;'
        f'font-size:0.7rem;font-weight:700;float:right;">⊘ ERROR</span>'
        if failed else
        f'<span style="background:#DCFCE7;color:#16A34A;border-radius:20px;padding:4px 12px;'
        f'font-size:0.7rem;font-weight:700;float:right;">✓ SUCCESS</span>'
    )

    if failed:
        body = (
            f'<div style="background:#FEF2F2;border:1px solid #FECACA;border-radius:14px;'
            f'padding:16px 18px;min-height:150px;">'
            f'<div style="color:#DC2626;font-weight:700;font-size:0.92rem;margin-bottom:8px;">⊘ Request failed</div>'
            f'<div style="color:#EF4444;font-size:0.82rem;line-height:1.6;word-break:break-word;">'
            f'{r["error"][:260].replace("<","&lt;").replace(">","&gt;")}</div></div>'
        )
        latency = f"{r.get('latency', 0):.2f}s" if "latency" in r else "—"
        cost, in_tok, out_tok = "$0.00000", 0, 0
    else:
        ans = r["answer"].replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        body = (
            f'<div style="background:#F8FAFC;border:1px solid #EEF2F7;border-radius:14px;'
            f'padding:16px 18px;min-height:150px;color:#334155;font-size:0.9rem;line-height:1.7;">{ans}</div>'
        )
        latency = f"{r['latency']:.2f}s"
        cost = f"${r['cost']:.5f}"
        in_tok, out_tok = r["in_tok"], r["out_tok"]

    def metric(label, value):
        return (
            f'<div style="flex:1;padding:14px 4px 4px 4px;">'
            f'<div style="font-size:0.66rem;font-weight:700;letter-spacing:0.06em;'
            f'text-transform:uppercase;color:#94A3B8;margin-bottom:4px;">{label}</div>'
            f'<div style="font-size:1.05rem;font-weight:700;color:#1E293B;">{value}</div></div>'
        )

    st.markdown(f"""
    <div style="background:#FFFFFF;border:1px solid #E7ECF3;border-radius:20px;
                padding:22px 24px;box-shadow:0 8px 28px rgba(30,55,110,0.06);
                margin-bottom:20px;
                background-image:radial-gradient(circle at top right,{color}14,transparent 55%);">
        <div style="margin-bottom:16px;">
            {badge}
            <span style="width:11px;height:11px;border-radius:50%;background:{color};
                         display:inline-block;margin-right:10px;vertical-align:middle;"></span>
            <span style="font-weight:800;font-size:1.15rem;color:#0F172A;vertical-align:middle;">{info['name']}</span>
            <div style="font-size:0.74rem;font-weight:700;letter-spacing:0.08em;
                        text-transform:uppercase;color:#94A3B8;margin:4px 0 0 21px;">{info['provider']}</div>
        </div>
        {body}
        <div style="display:flex;border-top:1px solid #EEF2F7;margin-top:18px;">
            {metric("Latency", latency)}
            {metric("Est. Cost", cost)}
        </div>
        <div style="display:flex;border-top:1px solid #EEF2F7;">
            {metric("Input Tokens", in_tok)}
            {metric("Output Tokens", out_tok)}
        </div>
    </div>
    """, unsafe_allow_html=True)


if "results" in st.session_state:
    st.markdown('<div class="results-title">Comparison Results</div>', unsafe_allow_html=True)

    results = st.session_state["results"]
    # 2-column grid
    for i in range(0, len(results), 2):
        row = st.columns(2, gap="large")
        for col, r in zip(row, results[i:i + 2]):
            with col:
                render_card(r)

    st.markdown(
        '<div style="text-align:center;color:#94A3B8;font-size:0.82rem;margin-top:10px;">'
        'Response costs are estimates and may vary based on current OpenRouter pricing.</div>',
        unsafe_allow_html=True,
    )
