# ui.py — the shared "biometric terminal" design system every page injects

import streamlit as st                                        # Streamlit builds the web UI
from datetime import datetime                                 # used for the live timestamp in page headers

# the full stylesheet for the app — written once here, used by every page
_CSS = """
<style>
/* pull in the three fonts: Unbounded (headings), Sora (body), JetBrains Mono (data) */
@import url('https://fonts.googleapis.com/css2?family=Unbounded:wght@400;600;700&family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* design tokens — change a colour here and the whole app follows */
:root{
    --bg:        #070B0F;                                    /* near-black page background */
    --panel:     #0D141C;                                    /* card background */
    --panel-2:   #101B26;                                    /* slightly lighter card background */
    --line:      rgba(52,245,197,.14);                       /* faint mint border colour */
    --mint:      #34F5C5;                                    /* the signature scan-green accent */
    --mint-soft: rgba(52,245,197,.55);                       /* dimmed mint for secondary glows */
    --blue:      #569CFF;                                    /* info colour */
    --amber:     #FFB454;                                    /* warning colour */
    --red:       #FF6B6B;                                    /* danger colour */
    --text:      #E8F4EE;                                    /* main text colour */
    --muted:     #7C8F89;                                    /* secondary text colour */
}

/* page background: two soft radial glows layered over near-black */
.stApp{
    background:
        radial-gradient(1100px 600px at 85% -10%, rgba(52,245,197,.09), transparent 60%),
        radial-gradient(900px 500px at -10% 110%, rgba(86,156,255,.06), transparent 55%),
        var(--bg);
    color: var(--text);
    font-family: 'Sora', sans-serif;
}

/* faint blueprint grid that drifts very slowly across the page */
.stApp::before{
    content:"";                                              /* pseudo-element needs content to exist */
    position:fixed; inset:0;                                 /* stretch it over the entire viewport */
    background-image:
        linear-gradient(rgba(52,245,197,.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(52,245,197,.03) 1px, transparent 1px);
    background-size: 44px 44px;                              /* spacing of the grid lines */
    animation: gridpan 90s linear infinite;                  /* near-imperceptible drift = the page feels alive */
    pointer-events:none;                                     /* let clicks pass straight through it */
    z-index:0;
}
@keyframes gridpan{                                          /* slide the grid one full cell over 90 seconds */
    from{ background-position:0 0, 0 0; }
    to{   background-position:0 44px, 44px 0; }
}

/* film-grain noise overlay (an inline SVG turbulence texture) for analogue depth */
.stApp::after{
    content:""; position:fixed; inset:0; pointer-events:none; z-index:0; opacity:.05;
    background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>");
}

/* hide Streamlit's own chrome (header bar, Deploy button, hamburger menu) — we own the page */
header[data-testid="stHeader"]{ background:transparent; }
[data-testid="stToolbar"]{ display:none; }

/* give content a little room at the top now the header is gone */
.block-container{ padding-top:3rem; }

/* all headings use the geometric display font with a soft mint aura */
h1, h2, h3{
    font-family:'Unbounded', sans-serif !important; letter-spacing:-.01em;
    text-shadow:0 0 36px rgba(52,245,197,.16);
}

/* mint-tinted custom scrollbar */
::-webkit-scrollbar{ width:10px; height:10px; }
::-webkit-scrollbar-track{ background:transparent; }
::-webkit-scrollbar-thumb{ background:#16222D; border-radius:8px; border:2px solid var(--bg); }
::-webkit-scrollbar-thumb:hover{ background:rgba(52,245,197,.4); }

/* sidebar: darker panel with a mint hairline on its edge */
[data-testid="stSidebar"]{
    background:#05090C;
    border-right:1px solid var(--line);
}
[data-testid="stSidebar"] *{ font-family:'Sora', sans-serif; }
[data-testid="stIconMaterial"]{ font-family:'Material Symbols Rounded' !important; }  /* keep Streamlit's icon glyphs as icons, not text */

/* sidebar radio → glowing nav pills (the round radio dot itself is hidden) */
[data-testid="stSidebar"] [role="radiogroup"]{ gap:4px; }
[data-testid="stSidebar"] [role="radiogroup"] > label{
    border:1px solid transparent; border-radius:10px;
    padding:9px 14px; margin:0; width:100%;
    transition:background .15s ease, border-color .15s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] > label:hover{
    background:rgba(52,245,197,.05); border-color:var(--line);
}
[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked){
    background:rgba(52,245,197,.09); border-color:var(--mint-soft);
    box-shadow:inset 3px 0 0 var(--mint), 0 0 18px rgba(52,245,197,.10);
}
[data-testid="stSidebar"] [role="radiogroup"] > label > div:first-child{ display:none; }

/* primary buttons: mint gradient pill, hover glow, and a light-sweep shimmer */
.stButton > button, [data-testid="stFormSubmitButton"] > button, [data-testid="stDownloadButton"] > button{
    background:linear-gradient(135deg, #34F5C5 0%, #1FC79E 100%);
    color:#04110C;
    font-family:'Sora', sans-serif; font-weight:700; letter-spacing:.02em;
    border:none; border-radius:10px; padding:.6rem 1.5rem;
    position:relative; overflow:hidden;
    transition:transform .15s ease, box-shadow .25s ease;
}
.stButton > button::before, [data-testid="stFormSubmitButton"] > button::before{
    content:""; position:absolute; top:0; bottom:0; width:40%; left:-60%;   /* the light streak, parked off-screen */
    background:linear-gradient(105deg, transparent, rgba(255,255,255,.5), transparent);
    transition:left .45s ease;
}
.stButton > button:hover::before, [data-testid="stFormSubmitButton"] > button:hover::before{
    left:120%;                                               /* sweep the streak across on hover */
}
.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover, [data-testid="stDownloadButton"] > button:hover{
    transform:translateY(-1px);                              /* tiny lift on hover */
    box-shadow:0 8px 28px rgba(52,245,197,.35);              /* mint glow under the button */
    color:#04110C;
}

/* sidebar buttons (logout) are quieter: outlined, not filled */
[data-testid="stSidebar"] .stButton > button{
    background:transparent; color:var(--muted);
    border:1px solid rgba(255,255,255,.10);
}
[data-testid="stSidebar"] .stButton > button:hover{
    border-color:var(--mint-soft); color:var(--mint); box-shadow:none;
}

/* text inputs and dropdowns: dark wells with a mint focus ring */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] > div > div{
    background:#0B1219 !important;
    border:1px solid rgba(255,255,255,.08) !important;
    border-radius:10px !important;
    color:var(--text) !important;
    font-family:'JetBrains Mono', monospace !important;
}
[data-testid="stTextInput"] input:focus{
    border-color:var(--mint) !important;
    box-shadow:0 0 0 3px rgba(52,245,197,.15) !important;
}
[data-testid="stTextInput"] label, [data-testid="stSelectbox"] label,
[data-testid="stCameraInput"] label, [data-testid="stDateInput"] label{
    color:var(--muted) !important;
    font-family:'JetBrains Mono', monospace !important;
    text-transform:uppercase; font-size:.72rem !important; letter-spacing:.12em;
}

/* forms become HUD panels: dark plate, hairline border, two corner ticks */
[data-testid="stForm"]{
    background:linear-gradient(180deg, var(--panel-2) 0%, var(--panel) 100%);
    border:1px solid var(--line); border-radius:16px; padding:26px;
    position:relative;
}
[data-testid="stForm"]::before{                              /* top-left corner bracket */
    content:""; position:absolute; top:-1px; left:-1px; width:18px; height:18px;
    border-top:2px solid var(--mint); border-left:2px solid var(--mint);
    border-top-left-radius:16px;
}
[data-testid="stForm"]::after{                               /* bottom-right corner bracket */
    content:""; position:absolute; bottom:-1px; right:-1px; width:18px; height:18px;
    border-bottom:2px solid var(--mint); border-right:2px solid var(--mint);
    border-bottom-right-radius:16px;
}

/* alerts (st.info/success/warning/error) restyled as terminal readouts */
[data-testid="stAlertContainer"]{
    background:var(--panel) !important;
    border:1px solid var(--line);
    border-left:3px solid var(--mint);
    border-radius:10px;
    color:var(--text) !important;
    font-family:'JetBrains Mono', monospace; font-size:.85rem;
}
[data-testid="stAlertContainer"] p{ color:var(--text) !important; }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]){    border-left-color:var(--blue); }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]){ border-left-color:var(--amber); }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]){   border-left-color:var(--red); }

/* expanders match the panel look */
[data-testid="stExpander"]{
    background:var(--panel); border:1px solid var(--line); border-radius:12px;
}

/* dataframes and the camera widget pick up the panel styling */
[data-testid="stDataFrame"]{
    border:1px solid var(--line); border-radius:14px; overflow:hidden;
}
[data-testid="stCameraInput"]{
    border:1px dashed var(--mint-soft); border-radius:16px; padding:10px;
    background:rgba(52,245,197,.03);
    box-shadow:inset 0 0 40px rgba(52,245,197,.04);
}
[data-testid="stCameraInput"] button{                        /* the 'Take Photo' trigger */
    background:rgba(52,245,197,.10); color:var(--mint);
    border:1px solid var(--mint-soft); border-radius:10px;
    font-family:'JetBrains Mono', monospace; letter-spacing:.08em; text-transform:uppercase;
}

/* ---- custom HTML components (built with st.markdown) ---- */

/* small mono label above a page title, e.g. "// ADMIN CONSOLE" — with a faint signal flicker */
.eyebrow{
    font-family:'JetBrains Mono', monospace;
    color:var(--mint); font-size:.75rem; letter-spacing:.22em;
    text-transform:uppercase; margin-bottom:.2rem;
    animation:flicker 6s infinite;
}
@keyframes flicker{                                          /* a single quick dip, like a CRT refresh */
    0%, 96%, 100%{ opacity:1; } 97%{ opacity:.35; } 98%{ opacity:.9; }
}

/* the gradient hairline drawn under every page header */
.hud-rule{
    height:1px; margin:.4rem 0 1.4rem 0;
    background:linear-gradient(90deg, var(--mint-soft), rgba(52,245,197,.06) 40%, transparent);
}

/* right-hand mono metadata in the header row (live timestamp) */
.header-meta{
    font-family:'JetBrains Mono', monospace; color:var(--muted);
    font-size:.72rem; letter-spacing:.14em; text-align:right;
}

/* big stat card used on dashboards — HUD plate with corner ticks and an index number */
.hw-card{
    background:linear-gradient(180deg, var(--panel-2) 0%, var(--panel) 100%);
    border:1px solid var(--line); border-radius:14px;
    padding:20px 22px; position:relative; overflow:hidden;
    transition:transform .2s ease, border-color .2s ease, box-shadow .2s ease;
}
.hw-card:hover{
    transform:translateY(-3px);                              /* cards lift toward you on hover */
    border-color:var(--mint-soft);
    box-shadow:0 12px 34px rgba(0,0,0,.45), 0 0 24px rgba(52,245,197,.08);
}
.hw-card::after{                                             /* thin mint light-strip along the card top */
    content:""; position:absolute; top:0; left:22px; right:22px; height:1px;
    background:linear-gradient(90deg, transparent, var(--mint-soft), transparent);
}
.hw-card .c{ position:absolute; width:9px; height:9px; border:1px solid var(--mint-soft); }
.hw-card .c.tl{ top:6px;  left:6px;  border-right:none; border-bottom:none; }   /* ┌ */
.hw-card .c.tr{ top:6px;  right:6px; border-left:none;  border-bottom:none; }   /* ┐ */
.hw-card .c.bl{ bottom:6px; left:6px;  border-right:none; border-top:none; }    /* └ */
.hw-card .c.br{ bottom:6px; right:6px; border-left:none;  border-top:none; }    /* ┘ */
.hw-card .idx{                                               /* faint 01/02/03 index in the corner */
    position:absolute; top:14px; right:16px;
    font-family:'JetBrains Mono', monospace; font-size:.65rem; color:rgba(124,143,137,.55);
    letter-spacing:.18em;
}
.hw-card .label{
    font-family:'JetBrains Mono', monospace; color:var(--muted);
    font-size:.68rem; letter-spacing:.16em; text-transform:uppercase;
    word-break:keep-all;                                     /* never split a word mid-letter */
}
.hw-card .value{
    font-family:'Unbounded', sans-serif; color:var(--text);
    font-size:2rem; font-weight:600; line-height:1.25; margin-top:8px;
}
.hw-card .value.mint{ color:var(--mint); text-shadow:0 0 24px rgba(52,245,197,.4); }

/* identity badge shown after a successful face match */
.scan-result{
    display:flex; align-items:center; gap:16px;
    background:rgba(52,245,197,.07); border:1px solid var(--mint-soft);
    border-radius:14px; padding:18px 22px; margin:10px 0;
    box-shadow:0 0 30px rgba(52,245,197,.10);
}
.scan-result .dot{
    width:12px; height:12px; border-radius:50%; background:var(--mint);
    box-shadow:0 0 14px var(--mint); animation:pulse 1.6s infinite;
}
.scan-result .who{ font-family:'Unbounded', sans-serif; font-size:1.15rem; color:var(--text); }
.scan-result .score{ font-family:'JetBrains Mono', monospace; color:var(--muted); font-size:.8rem; }

/* status ticker line: pulsing dot + mono system facts */
.ticker{
    display:flex; align-items:center; justify-content:center; gap:10px;
    font-family:'JetBrains Mono', monospace; font-size:.7rem;
    color:var(--muted); letter-spacing:.14em; text-transform:uppercase;
}
.ticker .dot{
    width:7px; height:7px; border-radius:50%; background:var(--mint);
    box-shadow:0 0 10px var(--mint); animation:pulse 2s infinite;
}

/* the animated scan-ring logo on the login page */
.scan-ring{
    width:120px; height:120px; margin:0 auto 18px auto;
    border-radius:50%; position:relative;
    border:1px solid var(--mint-soft);
    box-shadow:0 0 40px rgba(52,245,197,.18), inset 0 0 30px rgba(52,245,197,.06);
    overflow:hidden;
}
.scan-ring::before{                                          /* simple face glyph drawn with a radial gradient */
    content:""; position:absolute; inset:18px; border-radius:50%;
    background:radial-gradient(circle at 50% 38%, rgba(52,245,197,.35) 0 14px, transparent 15px),
               radial-gradient(circle at 50% 78%, rgba(52,245,197,.22) 0 22px, transparent 23px);
}
.scan-ring .beam{                                            /* the moving horizontal scan line */
    position:absolute; left:8%; right:8%; height:2px;
    background:linear-gradient(90deg, transparent, var(--mint), transparent);
    box-shadow:0 0 12px var(--mint);
    animation:scan 2.4s ease-in-out infinite;
}
@keyframes scan{                                             /* sweep the beam top-to-bottom and back */
    0%,100%{ top:14%; } 50%{ top:84%; }
}
@keyframes pulse{                                            /* gentle breathing for status dots */
    0%,100%{ opacity:1; } 50%{ opacity:.35; }
}

/* staggered fade-up applied to page content blocks */
.fade-in{ animation:fadeUp .5s ease both; }
@keyframes fadeUp{
    from{ opacity:0; transform:translateY(10px); }
    to{ opacity:1; transform:none; }
}
</style>
"""


def inject_css():
    """Push the stylesheet above into the current page."""
    st.markdown(_CSS, unsafe_allow_html=True)                 # unsafe_allow_html lets the <style> tag through


def page_header(eyebrow, title):
    """Draw the standard page heading: mono label, display title, live timestamp, gradient rule."""
    left, right = st.columns([3, 1], vertical_alignment="bottom")  # title left, timestamp right
    with left:                                                # the main heading block
        st.markdown(
            f"<div class='fade-in'><div class='eyebrow'>// {eyebrow}</div>"  # the small mint label
            f"<h1 style='margin:0'>{title}</h1></div>",                      # the big Unbounded heading
            unsafe_allow_html=True,                           # allow our custom HTML
        )
    with right:                                               # the mono metadata block
        st.markdown(
            f"<div class='header-meta'>{datetime.now():%H:%M:%S}<br>{datetime.now():%d·%m·%Y}</div>",
            unsafe_allow_html=True,                           # allow our custom HTML
        )
    st.markdown("<div class='hud-rule'></div>", unsafe_allow_html=True)  # the gradient hairline underneath


def metric_cards(items):
    """Draw a row of HUD stat cards; items = list of (label, value, highlight?) tuples."""
    cols = st.columns(len(items))                             # one equal-width column per card
    for i, (col, (label, value, *flag)) in enumerate(zip(cols, items)):  # pair each column with its card data
        mint = "mint" if flag and flag[0] else ""             # optional mint highlight on the number
        col.markdown(                                         # render the card HTML inside its column
            f"<div class='hw-card fade-in'>"
            f"<span class='c tl'></span><span class='c tr'></span>"   # the four corner ticks
            f"<span class='c bl'></span><span class='c br'></span>"
            f"<span class='idx'>0{i + 1}</span>"                       # faint index number top-right
            f"<div class='label'>{label}</div>"
            f"<div class='value {mint}'>{value}</div></div>",
            unsafe_allow_html=True,
        )


def scan_result(name, student_id, score):
    """Draw the glowing identity badge after a face is recognized."""
    st.markdown(
        f"<div class='scan-result'><div class='dot'></div>"   # pulsing mint status dot
        f"<div><div class='who'>{name}</div>"                 # the matched student's name
        f"<div class='score'>ID {student_id} &nbsp;·&nbsp; match confidence {score:.0%}</div></div></div>",
        unsafe_allow_html=True,
    )


def ticker(text):
    """Draw a status ticker line: pulsing mint dot + mono uppercase text."""
    st.markdown(
        f"<div class='ticker'><span class='dot'></span><span>{text}</span></div>",
        unsafe_allow_html=True,                               # allow the custom HTML through
    )


def sidebar_status():
    """Draw the SYSTEM ONLINE status block at the bottom of the sidebar."""
    st.sidebar.markdown("---")                                # divider above the status block
    st.sidebar.markdown(
        "<div class='ticker' style='justify-content:flex-start'>"
        "<span class='dot'></span><span>System online</span></div>"        # pulsing dot + label
        "<p style='font-family:JetBrains Mono, monospace; font-size:.62rem; "
        "color:var(--muted); letter-spacing:.12em; margin-top:6px'>"
        "VERIFACE v2.0 · ENGINE BUFFALO_L · 512-D</p>",                     # quiet version line
        unsafe_allow_html=True,                               # allow the custom HTML through
    )


def require_role(role):
    """Block the page unless the logged-in user has the given role."""
    if st.session_state.get("role") != role:                  # not logged in, or wrong role
        st.error("Access denied — please log in first.")      # explain why the page is blocked
        st.page_link("App.py", label="Go to login")           # one-click way back to the login page
        st.stop()                                             # halt the script so nothing below renders


def style_chart(fig):
    """Restyle a Plotly figure to match the app theme."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",                        # transparent outer background
        plot_bgcolor="rgba(0,0,0,0)",                         # transparent plotting area
        font_family="Sora",                                   # match the body font
        font_color="#7C8F89",                                 # muted text on axes
        colorway=["#34F5C5", "#FFB454", "#569CFF"],           # mint first, then accents
        margin=dict(l=10, r=10, t=50, b=10),                  # tighter margins than the default
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,.05)")       # faint grid lines
    fig.update_yaxes(gridcolor="rgba(255,255,255,.05)")       # faint grid lines
    return fig                                                # hand the styled figure back
