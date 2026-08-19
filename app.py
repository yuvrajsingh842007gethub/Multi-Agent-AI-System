import streamlit as st
import time
import json
import re
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #e8e4dc;
}

.stApp {
    background: #0a0a0f;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(255,140,50,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(255,80,30,0.08) 0%, transparent 55%);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; }

.hero {
    text-align: center;
    padding: 3.5rem 0 2.5rem;
    position: relative;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #ff8c32;
    margin-bottom: 1rem;
    opacity: 0.9;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.8rem, 6vw, 5rem);
    font-weight: 800;
    line-height: 1.0;
    letter-spacing: -0.03em;
    color: #f0ebe0;
    margin: 0 0 1rem;
}
.hero h1 span { color: #ff8c32; }
.hero-sub {
    font-size: 1.05rem;
    font-weight: 300;
    color: #a09890;
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.65;
}

.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,140,50,0.3), transparent);
    margin: 2rem 0;
}

.st-key-input_card {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,140,50,0.15) !important;
    border-radius: 16px !important;
    padding: 1.5rem 2rem !important;
    margin-bottom: 2rem;
    backdrop-filter: blur(8px);
}

.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,140,50,0.25) !important;
    border-radius: 10px !important;
    color: #f0ebe0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #ff8c32 !important;
    box-shadow: 0 0 0 3px rgba(255,140,50,0.12) !important;
}
.stTextInput > label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: #ff8c32 !important;
    font-weight: 500 !important;
}

.stButton > button {
    background: linear-gradient(135deg, #ff8c32 0%, #ff5a1a 100%) !important;
    color: #0a0a0f !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.7rem 2.2rem !important;
    cursor: pointer !important;
    transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s !important;
    box-shadow: 0 4px 20px rgba(255,140,50,0.3) !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(255,140,50,0.4) !important;
    opacity: 0.95 !important;
}
.stButton > button:active { transform: translateY(0) !important; }

.step-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s;
}
.step-card.active { border-color: rgba(255,140,50,0.4); background: rgba(255,140,50,0.04); }
.step-card.done { border-color: rgba(80,200,120,0.3); background: rgba(80,200,120,0.03); }
.step-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 14px 0 0 14px;
    background: rgba(255,255,255,0.05);
    transition: background 0.3s;
}
.step-card.active::before { background: #ff8c32; }
.step-card.done::before   { background: #50c878; }

.step-header { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.3rem; }
.step-num {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.15em;
    color: #ff8c32;
    opacity: 0.7;
}
.step-title { font-family: 'Syne', sans-serif; font-size: 0.95rem; font-weight: 700; color: #f0ebe0; }
.step-status { margin-left: auto; font-family: 'DM Mono', monospace; font-size: 0.68rem; letter-spacing: 0.1em; }
.status-waiting  { color: #555; }
.status-running  { color: #ff8c32; }
.status-done     { color: #50c878; }

.result-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-top: 1rem;
    margin-bottom: 1rem;
}
.result-panel-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #ff8c32;
    margin-bottom: 1rem;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid rgba(255,140,50,0.15);
}
.result-content {
    font-size: 0.92rem;
    line-height: 1.8;
    color: #cdc8bf;
    white-space: pre-wrap;
    font-family: 'DM Sans', sans-serif;
}

.st-key-panel_search_fallback,
.st-key-panel_reader {
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important;
    padding: 1.8rem 2rem !important;
    margin-top: 1rem;
    margin-bottom: 1rem;
}
.st-key-panel_search_fallback .stMarkdown,
.st-key-panel_reader .stMarkdown {
    color: #cdc8bf;
}

.st-key-panel_report {
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid rgba(255,140,50,0.2) !important;
    border-radius: 16px !important;
    padding: 2rem 2.5rem !important;
    margin-top: 1rem;
}
.st-key-panel_feedback {
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid rgba(80,200,120,0.2) !important;
    border-radius: 16px !important;
    padding: 2rem 2.5rem !important;
    margin-top: 1rem;
}
.panel-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    padding-bottom: 0.7rem;
}
.panel-label.orange { color: #ff8c32; border-bottom: 1px solid rgba(255,140,50,0.15); }
.panel-label.green { color: #50c878; border-bottom: 1px solid rgba(80,200,120,0.15); }

.stSpinner > div { color: #ff8c32 !important; }

details summary {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    color: #a09890 !important;
    letter-spacing: 0.1em !important;
    cursor: pointer;
}

.section-heading {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #f0ebe0;
    margin: 2rem 0 1rem;
}

.notice {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #605850;
    text-align: center;
    margin-top: 3rem;
    letter-spacing: 0.08em;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
STEPS = ["search", "reader", "writer", "critic"]
STEP_META = {
    "search": ("01", "Search Agent", "Gathers recent web information", "🔍  Search Agent is working…"),
    "reader": ("02", "Reader Agent", "Scrapes & extracts deep content", "📄  Reader Agent is scraping top resources…"),
    "writer": ("03", "Writer Chain", "Drafts the full research report", "✍️  Writer is drafting the report…"),
    "critic": ("04", "Critic Chain", "Reviews & scores the report", "🧐  Critic is reviewing the report…"),
}


def normalize_content(raw):
    """Unwrap LangChain-style objects and parse JSON-looking strings into
    real Python objects so downstream code can inspect their structure."""
    if hasattr(raw, "content"):
        raw = raw.content

    if isinstance(raw, str):
        stripped = raw.strip()
        if stripped[:1] in ("[", "{"):
            try:
                raw = json.loads(stripped)
            except (json.JSONDecodeError, TypeError):
                pass
    return raw


def extract_search_items(raw):
    """
    Best-effort walk over arbitrary agent/tool output to pull out a list of
    {title, url, snippet} search-result dicts, plus any leftover plain text
    that didn't fit that shape.

    Returns (items, fallback_text).
    """
    raw = normalize_content(raw)
    items, text_chunks = [], []

    def pick(d, keys):
        for k in keys:
            v = d.get(k)
            if v:
                return v
        return None

    def handle_dict(d):
        title = pick(d, ["title", "name", "heading"])
        url = pick(d, ["url", "link", "href", "source"])
        snippet = pick(d, ["snippet", "description", "summary", "content", "text", "body"])

        # LangChain-style content block: {"type": "text", "text": "...", ["reference": {...}]}
        # Covers both real text chunks AND empty citation/reference markers -
        # either way it should never fall through to a raw JSON dump.
        if d.get("type") == "text" and not title and not url:
            text = d.get("text", "")
            if text:
                text_chunks.append(str(text))
            return  # empty citation-marker blocks are silently dropped

        if title or url:
            items.append({"title": str(title or url), "url": url, "snippet": str(snippet) if snippet else ""})
            return

        # Container wrapping a list of results, e.g. {"results": [...]}
        for container_key in ("results", "organic_results", "items", "data", "sources", "documents"):
            if isinstance(d.get(container_key), list):
                for sub in d[container_key]:
                    walk(sub)
                return

        # Pure citation/reference marker with no useful payload - drop silently
        if "reference" in d or "reference_ids" in d:
            return

        # Nothing recognizable — dump as text
        text_chunks.append(json.dumps(d, ensure_ascii=False, indent=2))

    def walk(node):
        if isinstance(node, dict):
            handle_dict(node)
        elif isinstance(node, list):
            for sub in node:
                walk(sub)
        elif node is not None:
            text_chunks.append(str(node))

    walk(raw)
    # Text chunks are often just the same running sentence/paragraph split
    # around citation markers - concatenate them as-is (no forced blank line
    # between them), then only collapse genuinely excessive blank lines.
    fallback_text = "".join(text_chunks)
    fallback_text = re.sub(r"\n{3,}", "\n\n", fallback_text).strip()
    return items, fallback_text


def extract_text(raw_content):
    """Flatten arbitrary agent output into a single readable plain-text
    string (used for downloads and for feeding text into the next agent)."""
    items, fallback_text = extract_search_items(raw_content)
    if items:
        lines = []
        for i, item in enumerate(items, start=1):
            lines.append(f"{i}. {item['title']}")
            if item["url"]:
                lines.append(f"   {item['url']}")
            if item["snippet"]:
                lines.append(f"   {item['snippet']}")
            lines.append("")
        if fallback_text:
            lines.append(fallback_text)
        text = "\n".join(lines).strip()
    else:
        text = fallback_text.strip() if fallback_text else str(raw_content)
    return re.sub(r"\n{3,}", "\n\n", text)


def render_search_results(raw_content):
    """Render search-agent output as clean result cards when it has
    recognizable structure (title/url/snippet); falls back to plain text."""
    items, fallback_text = extract_search_items(raw_content)

    if items:
        for i, item in enumerate(items, start=1):
            title_html = (
                f'<a href="{item["url"]}" target="_blank" '
                f'style="color:#ff8c32;text-decoration:none;font-weight:700;">{item["title"]}</a>'
                if item["url"] else
                f'<span style="color:#f0ebe0;font-weight:700;">{item["title"]}</span>'
            )
            snippet_html = (
                f'<div class="result-content" style="font-size:0.85rem;margin-top:0.5rem;">{item["snippet"]}</div>'
                if item["snippet"] else ""
            )
            url_html = (
                f'<div style="font-size:0.72rem;color:#706860;margin-top:0.5rem;">{item["url"]}</div>'
                if item["url"] else ""
            )
            st.markdown(f"""
            <div class="result-panel" style="margin-bottom:0.8rem;">
                <div style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#605850;margin-bottom:0.5rem;letter-spacing:0.1em;">RESULT {i:02d}</div>
                <div style="font-size:0.95rem;">{title_html}</div>
                {snippet_html}
                {url_html}
            </div>
            """, unsafe_allow_html=True)
        if fallback_text:
            with st.expander("Additional raw output"):
                st.markdown(fallback_text)
    else:
        display_text = fallback_text if fallback_text else str(raw_content)
        with st.container(key="panel_search_fallback"):
            st.markdown('<div class="result-panel-title">Search Agent Output</div>', unsafe_allow_html=True)
            st.markdown(display_text)


def step_card(step_key: str, status: str):
    num, title, desc, _ = STEP_META[step_key]
    status_map = {
        "waiting": ("WAITING", "status-waiting"),
        "running": ("● RUNNING", "status-running"),
        "done":    ("✓ DONE", "status-done"),
    }
    label, cls = status_map.get(status, ("", ""))
    card_cls = {"running": "active", "done": "done"}.get(status, "")
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
        <div style='font-size:0.82rem;color:#706860;margin-top:0.3rem;'>{desc}</div>
    </div>
    """, unsafe_allow_html=True)


def build_combined_markdown(results: dict, topic: str) -> str:
    parts = [f"# Research Report: {topic}\n"]
    if "writer" in results:
        parts.append("## Final Report\n\n" + str(results["writer"]) + "\n")
    if "critic" in results:
        parts.append("## Critic Feedback\n\n" + str(results["critic"]) + "\n")
    if "search" in results:
        parts.append("## Raw Search Results\n\n" + str(results["search"]) + "\n")
    if "reader" in results:
        parts.append("## Scraped Content\n\n" + str(results["reader"]) + "\n")
    return "\n".join(parts)


# ── Session state init ────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = {}
if "running" not in st.session_state:
    st.session_state.running = False
if "done" not in st.session_state:
    st.session_state.done = False
if "active_topic" not in st.session_state:
    st.session_state.active_topic = ""


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Multi-Agent AI System</div>
    <h1>Research<span>Mind</span></h1>
    <p class="hero-sub">
        Four specialized AI agents collaborate — searching, scraping, writing,
        and critiquing — to deliver a polished research report on any topic.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Layout: input left, pipeline right ───────────────────────────────────────
results = st.session_state.results
next_step = next((s for s in STEPS if s not in results), None)

col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    with st.container(key="input_card"):
        topic = st.text_input(
            "Research Topic",
            placeholder="e.g. Quantum computing breakthroughs in 2025",
            key="topic_input",
            label_visibility="visible",
            disabled=st.session_state.running,
        )
        run_btn = st.button(
            "⚡  Run Research Pipeline",
            use_container_width=True,
            disabled=st.session_state.running,
        )

    if run_btn:
        if not topic.strip():
            st.warning("Please enter a research topic first.")
        else:
            st.session_state.results = {}
            st.session_state.running = True
            st.session_state.done = False
            st.session_state.active_topic = topic.strip()
            st.rerun()

    # ── Loading indicator lives right here, directly under the button ──
    if st.session_state.running and next_step is not None:
        _, _, _, spinner_text = STEP_META[next_step]
        topic_val = st.session_state.active_topic

        with st.spinner(spinner_text):
            if next_step == "search":
                search_agent = build_search_agent()
                sr = search_agent.invoke({
                    "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
                })
                raw_search_content = sr["messages"][-1].content
                results["search_raw"] = raw_search_content  # keep structure for card rendering
                results["search"] = extract_text(raw_search_content)  # flattened text for downstream use

            elif next_step == "reader":
                reader_agent = build_reader_agent()
                rr = reader_agent.invoke({
                    "messages": [("user",
                        f"Based on the following search results about '{topic_val}', "
                        f"pick the most relevant URL and scrape it for deeper content.\n\n"
                        f"Search Results:\n{results['search'][:800]}"
                    )]
                })
                results["reader"] = extract_text(rr["messages"][-1].content)

            elif next_step == "writer":
                research_combined = (
                    f"SEARCH RESULTS:\n{results['search']}\n\n"
                    f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
                )
                results["writer"] = writer_chain.invoke({
                    "topic": topic_val,
                    "research": research_combined
                })

            elif next_step == "critic":
                results["critic"] = critic_chain.invoke({"report": results["writer"]})

        st.session_state.results = results

        if next_step == "critic":
            st.session_state.running = False
            st.session_state.done = True

        st.rerun()

    st.markdown("""
    <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:1.5rem;">
        <span style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#605850;letter-spacing:0.1em;">TRY →</span>
    """, unsafe_allow_html=True)
    for ex in ["LLM agents 2025", "CRISPR gene editing", "Fusion energy progress"]:
        st.markdown(f"""
        <span style="
            background:rgba(255,255,255,0.04);
            border:1px solid rgba(255,255,255,0.08);
            border-radius:6px;
            padding:0.25rem 0.7rem;
            font-size:0.75rem;
            color:#a09890;
            font-family:'DM Sans',sans-serif;
            cursor:default;
        ">{ex}</span>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)

    # Render each step card with correct status (purely visual - no execution here)
    for step_key in STEPS:
        if step_key in results:
            status = "done"
        elif st.session_state.running and step_key == next_step:
            status = "running"
        else:
            status = "waiting"
        step_card(step_key, status)


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

    if st.session_state.done:
        combined_md = build_combined_markdown(r, st.session_state.active_topic)
        st.download_button(
            label="⬇  Download All Results (.md)",
            data=combined_md,
            file_name=f"research_all_{int(time.time())}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    if "search" in r:
        with st.expander("🔍 Search Results", expanded=False):
            render_search_results(r.get("search_raw", r["search"]))
            st.download_button(
                "⬇ Download search results (.txt)",
                data=r["search"],
                file_name="search_results.txt",
                mime="text/plain",
                key="dl_search",
            )

    if "reader" in r:
        with st.expander("📄 Scraped Content (raw)", expanded=False):
            with st.container(key="panel_reader"):
                st.markdown('<div class="result-panel-title">Reader Agent Output</div>', unsafe_allow_html=True)
                st.markdown(r["reader"])
            st.download_button(
                "⬇ Download scraped content (.txt)",
                data=r["reader"],
                file_name="scraped_content.txt",
                mime="text/plain",
                key="dl_reader",
            )

    if "writer" in r:
        with st.container(key="panel_report"):
            st.markdown('<div class="panel-label orange">📝 Final Research Report</div>', unsafe_allow_html=True)
            st.markdown(r["writer"])
        st.download_button(
            "⬇  Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
            key="dl_report",
        )

    if "critic" in r:
        with st.container(key="panel_feedback"):
            st.markdown('<div class="panel-label green">🧐 Critic Feedback</div>', unsafe_allow_html=True)
            st.markdown(r["critic"])
        st.download_button(
            "⬇ Download Critic Feedback (.md)",
            data=r["critic"],
            file_name="critic_feedback.md",
            mime="text/markdown",
            key="dl_critic",
        )


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    ResearchMind · Powered by LangChain multi-agent pipeline · Built with Streamlit
</div>
""", unsafe_allow_html=True)