import re
import json
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from transaction_parser import parse_transaction, CATEGORIES
from storage import (init_db, add_transaction, get_transactions, get_monthly_summary,
                     set_budget, get_budget, update_transaction, delete_transaction,
                     set_savings_goal, get_savings_goal, create_user, verify_user,
                     get_user_setting, set_user_setting,
                     update_username, update_password)
from prediction import predict_next_month_expense
from gpt_helper import get_expense_description, suggest_category
from gmail_api import fetch_transaction_emails
from ocr import extract_text_from_image

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = "expanded"
st.set_page_config(
    page_title="BudgetBuddy",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state=st.session_state.sidebar_state )

# ─────────────────────────────────────────────
# i18n — load strings from en.json
# ─────────────────────────────────────────────
@st.cache_data
def load_strings():
    with open("en.json", "r", encoding="utf-8") as f:
        return json.load(f)

S = load_strings()

def t(path: str, **kwargs) -> str:
    """Dot-path accessor: t('auth.errors.username_taken', username='foo')"""
    keys = path.split(".")
    val  = S
    for k in keys:
        val = val[k]
    return val.format(**kwargs) if kwargs else val

# ─────────────────────────────────────────────
# THEMES
# ─────────────────────────────────────────────
THEMES = {
    "💜 Purple": {
        "accent":"#4f46e5","accent2":"#7c3aed","accent3":"#a855f7",
        "bg":"#f5f3ff","card_bg":"#ffffff","text":"#1e1b4b",
        "subtext":"#6b7280","border":"#ede9fe",
        "sidebar_from":"#1e1b4b","sidebar_to":"#312e81",
        "sidebar_text":"#e0e7ff","sidebar_sub":"#818cf8",
        "hero_from":"#4f46e5","hero_to":"#a855f7","chart_scale":"Purples",
    },
    "🌊 Ocean Blue": {
        "accent":"#0369a1","accent2":"#0284c7","accent3":"#38bdf8",
        "bg":"#f0f9ff","card_bg":"#ffffff","text":"#0c4a6e",
        "subtext":"#6b7280","border":"#bae6fd",
        "sidebar_from":"#0c4a6e","sidebar_to":"#075985",
        "sidebar_text":"#e0f2fe","sidebar_sub":"#7dd3fc",
        "hero_from":"#0369a1","hero_to":"#38bdf8","chart_scale":"Blues",
    },
    "🌿 Forest Green": {
        "accent":"#15803d","accent2":"#16a34a","accent3":"#4ade80",
        "bg":"#f0fdf4","card_bg":"#ffffff","text":"#14532d",
        "subtext":"#6b7280","border":"#bbf7d0",
        "sidebar_from":"#14532d","sidebar_to":"#166534",
        "sidebar_text":"#dcfce7","sidebar_sub":"#86efac",
        "hero_from":"#15803d","hero_to":"#4ade80","chart_scale":"Greens",
    },
    "🌅 Sunset Orange": {
        "accent":"#c2410c","accent2":"#ea580c","accent3":"#fb923c",
        "bg":"#fff7ed","card_bg":"#ffffff","text":"#7c2d12",
        "subtext":"#6b7280","border":"#fed7aa",
        "sidebar_from":"#7c2d12","sidebar_to":"#9a3412",
        "sidebar_text":"#ffedd5","sidebar_sub":"#fdba74",
        "hero_from":"#c2410c","hero_to":"#fb923c","chart_scale":"Oranges",
    },
    "🌸 Rose Pink": {
        "accent":"#be185d","accent2":"#db2777","accent3":"#f472b6",
        "bg":"#fdf2f8","card_bg":"#ffffff","text":"#831843",
        "subtext":"#6b7280","border":"#fbcfe8",
        "sidebar_from":"#831843","sidebar_to":"#9d174d",
        "sidebar_text":"#fce7f3","sidebar_sub":"#f9a8d4",
        "hero_from":"#be185d","hero_to":"#f472b6","chart_scale":"RdPu",
    },
    "🌙 Dark Mode": {
        "accent":"#818cf8","accent2":"#a78bfa","accent3":"#c4b5fd",
        "bg":"#0f172a","card_bg":"#1e293b","text":"#f1f5f9",
        "subtext":"#94a3b8","border":"#334155",
        "sidebar_from":"#020617","sidebar_to":"#0f172a",
        "sidebar_text":"#e2e8f0","sidebar_sub":"#818cf8",
        "hero_from":"#312e81","hero_to":"#1e1b4b","chart_scale":"Purples",
    },
}

# Nav items: (display label, internal key)
NAV_ITEMS = [
    ("📊 Dashboard",          "Dashboard"),
    ("💳 Add Transaction",    "Add Transaction"),
    ("📸 Upload Receipt",     "Upload Receipt"),
    # ("📧 Fetch Emails",       "Fetch Emails"),
    ("📋 View Transactions",  "View Transactions"),
    ("📋 Budget Planning",    "Budget Planning"),
    ("🎯 Savings Goals",      "Savings Goals"),
    ("🔍 Financial Insights", "Financial Insights"),
]

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
init_db()
for key, val in {
    "logged_in":         False,
    "user_id":           None,
    "username":          None,
    "register_mode":     False,
    "confirm_delete_id": None,
    "login_time":        None,
    "theme":             "💜 Purple",
    "current_page":      "Dashboard",
    "display_name":      None,
    # stale-state cleanup
    "parsed_transaction": None,
    "parsed_receipt":     None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

T = THEMES[st.session_state.theme]

# ─────────────────────────────────────────────
# DYNAMIC CSS
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] {{
    font-family:'Inter',sans-serif;
    background-color:{T['bg']} !important;
    color:{T['text']} !important;
}}
.main-header {{ font-size:2.4rem; font-weight:700; color:{T['accent']}; margin-bottom:0; }}
.metric-card {{
    background:{T['card_bg']}; padding:20px; border-radius:16px;
    box-shadow:0 1px 4px rgba(0,0,0,.08); border:1px solid {T['border']};
    height:100%; transition:box-shadow .2s;
}}
.metric-card:hover {{ box-shadow:0 4px 16px rgba(0,0,0,.12); }}
.positive {{ color:#10b981; font-weight:600; }}
.negative {{ color:#ef4444; font-weight:600; }}
.progress-bar  {{ height:10px; border-radius:99px; background:#e5e7eb; margin-top:6px; overflow:hidden; }}
.progress-fill {{
    height:100%; border-radius:99px;
    background:linear-gradient(90deg,{T['accent']},{T['accent2']});
    transition:width .4s;
}}
.progress-danger {{ background:linear-gradient(90deg,#ef4444,#f97316) !important; }}

/* ── Sidebar: hide ALL native widgets, show nothing ── */
section[data-testid="stSidebar"] {{
    background:linear-gradient(180deg,{T['sidebar_from']} 0%,{T['sidebar_to']} 100%) !important;
}}
section[data-testid="stSidebar"] * {{ color:{T['sidebar_text']} !important; }}
/* Hide the selectbox widget Streamlit renders — we use HTML buttons only */
section[data-testid="stSidebar"] .stSelectbox {{ display:none !important; }}

/* ── Custom nav items ── */
.nav-item {{
    display:flex; align-items:center; gap:10px;
    padding:10px 16px; border-radius:10px;
    cursor:pointer; margin-bottom:6px;
    font-size:.93rem; font-weight:500;
    color:{T['sidebar_text']};
    transition:background .15s;
    text-decoration:none;
}}
.nav-item:hover  {{ background:rgba(255,255,255,.1); }}
.nav-item.active {{
    background:rgba(255,255,255,.18);
    font-weight:700;
    border-left:3px solid {T['accent3']};
    padding-left:13px;
    margin-bottom:6px;
    margin-top:4px;
}}

/* ── Theme swatch pill ── */
.theme-pill {{
    display:inline-flex; align-items:center; gap:6px;
    padding:5px 12px; border-radius:99px;
    background:rgba(255,255,255,.12);
    font-size:.78rem; font-weight:600;
    cursor:pointer; margin:3px 2px;
    transition:background .15s;
    border:2px solid transparent;
}}
.theme-pill.active {{ border-color:{T['accent3']}; background:rgba(255,255,255,.22); }}

/* ── Hero ── */
.hero-section {{
    background:linear-gradient(135deg,{T['hero_from']} 0%,{T['hero_to']} 100%);
    padding:56px 24px 48px; border-radius:24px; margin-bottom:36px;
    text-align:center; color:white; position:relative; overflow:hidden;
}}
.hero-section::after {{
    content:''; position:absolute; inset:0;
    background:radial-gradient(ellipse at 70% 20%,rgba(255,255,255,.08) 0%,transparent 60%);
    pointer-events:none;
}}
.hero-title    {{ font-size:3.2rem; font-weight:800; letter-spacing:-.02em; margin-bottom:8px; }}
.hero-subtitle {{ font-size:1.15rem; opacity:.88; margin-bottom:24px; }}
.hero-features {{ display:flex; justify-content:center; gap:28px; flex-wrap:wrap; position:relative; z-index:1; }}
.feature-item  {{ display:flex; align-items:center; gap:6px; font-size:.95rem; background:rgba(255,255,255,.15); padding:6px 14px; border-radius:99px; }}
.stats-container {{ display:flex; justify-content:center; gap:48px; margin:28px 0 8px; flex-wrap:wrap; }}
.stat-item   {{ text-align:center; color:white; }}
.stat-number {{ font-size:2.4rem; font-weight:700; display:block; }}
.stat-label  {{ font-size:.85rem; opacity:.75; }}

/* ── Login ── */
.login-container::before {{
    content:''; position:absolute; top:0; left:0; right:0; height:4px;
    background:linear-gradient(90deg,{T['accent']},{T['accent2']},{T['accent3']});
    border-radius:20px 20px 0 0;
}}
.form-title    {{ font-size:1.8rem; font-weight:700; color:{T['text']}; text-align:center; margin-bottom:4px; }}
.form-subtitle {{ color:{T['subtext']}; font-size:.9rem; text-align:center; margin-bottom:24px; }}

/* ── Buttons ── */
.stButton > button {{
    border-radius:12px !important; font-weight:600 !important; transition:all .2s !important;
    border:none !important;
    background:linear-gradient(135deg,{T['accent']},{T['accent2']}) !important;
    color:white !important;
}}
.stButton > button:hover {{ transform:translateY(-1px) !important; box-shadow:0 6px 16px rgba(0,0,0,.2) !important; }}

/* ── Benefits ── */
.benefits-section {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:24px; margin-top:40px; }}
.benefit-card {{
    text-align:center; padding:28px 20px; border-radius:16px;
    background:{T['card_bg']}; box-shadow:0 4px 20px rgba(0,0,0,.07);
    border:1px solid {T['border']}; transition:transform .25s;
}}
.benefit-card:hover {{ transform:translateY(-4px); }}
.benefit-icon  {{ font-size:2.4rem; margin-bottom:12px; }}
.benefit-title {{ font-size:1.05rem; font-weight:600; color:{T['accent']}; margin-bottom:8px; }}
.benefit-desc  {{ color:{T['subtext']}; font-size:.88rem; line-height:1.55; }}

/* ── Avatar ── */
.avatar-chip {{
    display:inline-flex; align-items:center; gap:8px;
    background:{T['border']}; border-radius:99px; padding:6px 14px;
    font-weight:600; color:{T['accent']};
}}
.avatar-circle {{
    width:32px; height:32px; border-radius:50%;
    background:linear-gradient(135deg,{T['accent']},{T['accent2']});
    color:white; display:inline-flex; align-items:center;
    justify-content:center; font-weight:700; font-size:.9rem;
}}

/* ── Badges ── */
.badge {{ display:inline-block; padding:3px 10px; border-radius:99px; font-size:.75rem; font-weight:600; }}
.badge-income  {{ background:#d1fae5; color:#065f46; }}
.badge-expense {{ background:#fee2e2; color:#991b1b; }}

.section-title {{ font-size:1.15rem; font-weight:700; color:{T['text']}; margin-bottom:12px; }}
.empty-state {{ text-align:center; padding:48px 24px; color:{T['subtext']}; }}
.empty-state h3 {{ font-size:1.4rem; color:{T['subtext']}; margin-bottom:8px; }}

@keyframes float {{
    0%,100% {{ transform:translateY(0) rotate(0); }}
    50%      {{ transform:translateY(-18px) rotate(180deg); }}
}}
.floating-elements {{ position:absolute;width:100%;height:100%;overflow:hidden;pointer-events:none; }}
.floating-element  {{ position:absolute; opacity:.12; font-size:2rem; animation:float 6s ease-in-out infinite; }}
.floating-element:nth-child(1){{top:12%;left:8%;animation-delay:0s}}
.floating-element:nth-child(2){{top:18%;right:8%;animation-delay:1.5s}}
.floating-element:nth-child(3){{bottom:18%;left:12%;animation-delay:3s}}
.floating-element:nth-child(4){{bottom:10%;right:18%;animation-delay:4.5s}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def Rs(amount, decimals=2):
    return f"₹{amount:,.{decimals}f}"

def get_transactions_df():
    rows = get_transactions(st.session_state.user_id)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df

def full_logout():
    """BUG FIX: clear ALL session state on logout, not just a few keys."""
    for k in ["logged_in","user_id","username","display_name","login_time",
              "confirm_delete_id","parsed_transaction","parsed_receipt",
              "register_mode"]:
        st.session_state[k] = (False if k == "logged_in" else None)
    st.session_state.current_page = "Dashboard"

# ─────────────────────────────────────────────
# AUTO-LOGOUT (30 min)
# ─────────────────────────────────────────────
if st.session_state.logged_in and st.session_state.login_time:
    if datetime.now() - st.session_state.login_time > timedelta(minutes=30):
        full_logout()
        st.warning(t("app.session_expired"))
        st.rerun()

# ═══════════════════════════════════════════════════════
# LOGIN / REGISTER
# ═══════════════════════════════════════════════════════
if not st.session_state.logged_in:

    st.markdown(f"""
    <div class="hero-section">
        <div class="floating-elements">
            <div class="floating-element">💰</div>
            <div class="floating-element">💳</div>
            <div class="floating-element">🎯</div>
            <div class="floating-element">📊</div>
        </div>
        <div class="hero-title">💰 {t('app.name')}</div>
        <div class="hero-subtitle">{t('app.tagline').replace('BudgetBuddy', '<strong style="color:#fbbf24">BudgetBuddy</strong>')}</div>
        <div class="stats-container">
            <div class="stat-item"><span class="stat-number">100+</span><span class="stat-label">{t('hero.stats.happy_users')}</span></div>
            <div class="stat-item"><span class="stat-number">95%</span><span class="stat-label">{t('hero.stats.parse_accuracy')}</span></div>
            <div class="stat-item"><span class="stat-number">∞</span><span class="stat-label">{t('hero.stats.transactions')}</span></div>
        </div>
        <div class="hero-features">
            <div class="feature-item">{t('hero.features.ai')}</div>
            <div class="feature-item">{t('hero.features.receipt')}</div>
            <div class="feature-item">{t('hero.features.security')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)

        if st.session_state.register_mode:
            st.markdown(f'<div class="form-title">{t("auth.register_title")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="form-subtitle">{t("auth.register_subtitle")}</div>', unsafe_allow_html=True)

            with st.form("register_form"):
                new_full_name    = st.text_input("Full Name", placeholder="e.g. Rahul Sharma")
                new_username     = st.text_input(t("auth.username_label"), placeholder=t("auth.username_placeholder"))
                st.caption(t("auth.username_hint"))
                new_password     = st.text_input(t("auth.password_label"), type="password", placeholder=t("auth.password_placeholder"))
                confirm_password = st.text_input(t("auth.confirm_password_label"), type="password", placeholder=t("auth.confirm_password_placeholder"))
                register_btn     = st.form_submit_button(t("auth.create_account_btn"), use_container_width=True)

                if register_btn:
                    stripped   = new_username.strip()
                    clean_name = new_full_name.strip()
                    if not clean_name:
                        st.error("Please enter your full name.")
                    elif not stripped or not new_password:
                        st.error(t("auth.errors.fill_all_fields"))
                    elif len(stripped) < 3:
                        st.error(t("auth.errors.username_too_short"))
                    elif len(stripped) > 20:
                        st.error(t("auth.errors.username_too_long"))
                    elif not re.match(r"^[a-zA-Z0-9_]+$", stripped):
                        st.error(t("auth.errors.username_invalid_chars"))
                    elif stripped[0].isdigit():
                        st.error(t("auth.errors.username_starts_digit"))
                    elif len(new_password) < 8:
                        st.error(t("auth.errors.password_too_short"))
                    elif not any(c.isdigit() for c in new_password):
                        st.error(t("auth.errors.password_no_digit"))
                    elif new_password != confirm_password:
                        st.error(t("auth.errors.passwords_no_match"))
                    else:
                        uid = create_user(stripped, new_password, clean_name)
                        if uid:
                            st.success(t("auth.success.account_created"))
                            st.session_state.register_mode = False
                        else:
                            st.error(t("auth.errors.username_taken", username=stripped))

            if st.button(t("auth.back_to_login"), use_container_width=True):
                st.session_state.register_mode = False
                st.rerun()

        else:
            st.markdown(f'<div class="form-title">{t("auth.login_title")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="form-subtitle">{t("auth.login_subtitle")}</div>', unsafe_allow_html=True)

            with st.form("login_form"):
                username  = st.text_input(t("auth.username_label"), placeholder=t("auth.username_placeholder"))
                password  = st.text_input(t("auth.password_label"), type="password", placeholder=t("auth.password_placeholder"))
                login_btn = st.form_submit_button(t("auth.sign_in_btn"), use_container_width=True)

                if login_btn:
                    if not username or not password:
                        st.error(t("auth.errors.enter_both"))
                    else:
                        result = verify_user(username, password)
                        if result:
                            uid, full_name = result
                            st.session_state.logged_in    = True
                            st.session_state.user_id      = uid
                            st.session_state.username     = username
                            st.session_state.display_name = full_name or username
                            st.session_state.login_time   = datetime.now()
                            st.rerun()
                        else:
                            st.error(t("auth.errors.invalid_credentials"))

            st.markdown(f"<div style='text-align:center;color:{T['subtext']};margin:14px 0 6px;font-size:.85rem'>{t('auth.no_account')}</div>", unsafe_allow_html=True)
            if st.button(t("auth.create_new"), use_container_width=True):
                st.session_state.register_mode = True
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="benefits-section">
        <div class="benefit-card"><div class="benefit-icon">{t('benefits.goals.icon')}</div><div class="benefit-title">{t('benefits.goals.title')}</div><p class="benefit-desc">{t('benefits.goals.desc')}</p></div>
        <div class="benefit-card"><div class="benefit-icon">{t('benefits.analytics.icon')}</div><div class="benefit-title">{t('benefits.analytics.title')}</div><p class="benefit-desc">{t('benefits.analytics.desc')}</p></div>
        <div class="benefit-card"><div class="benefit-icon">{t('benefits.ai.icon')}</div><div class="benefit-title">{t('benefits.ai.title')}</div><p class="benefit-desc">{t('benefits.ai.desc')}</p></div>
        <div class="benefit-card"><div class="benefit-icon">{t('benefits.security.icon')}</div><div class="benefit-title">{t('benefits.security.title')}</div><p class="benefit-desc">{t('benefits.security.desc')}</p></div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════
# MAIN APP — HEADER
# ═══════════════════════════════════════════════════════
initial = (st.session_state.display_name or st.session_state.username)[0].upper()
display  = st.session_state.display_name or st.session_state.username
c1, c2, c3 = st.columns([4, 1, 1])
with c1:
    st.markdown("<h1 class='main-header'>💰 BudgetBuddy</h1>", unsafe_allow_html=True)
with c3:
    if st.button(t("app.logout"), use_container_width=True):
        full_logout()
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# SIDEBAR — pure HTML nav list, NO input widgets
# ═══════════════════════════════════════════════════════
with st.sidebar:

    # ── App title + user name ──
    st.markdown("""
    <div style='font-size:1.4rem;font-weight:700;margin-bottom:6px'>
        💰 BudgetBuddy
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='font-size:1.5rem;padding:10px 4px;'>
        <span>Hi, <strong>{display}</strong> 👋</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Nav list ──
    for label, key in NAV_ITEMS:
        is_active = st.session_state.current_page == key
        if is_active:
            st.markdown(f"""
            <div class="nav-item active" style="background:rgba(255,255,255,.18);font-weight:700;border-left:3px solid {T['accent3']};padding-left:13px;margin-bottom:8px;margin-top:4px;">
                {label}
            </div>""", unsafe_allow_html=True)
        else:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.session_state.sidebar_state = "collapsed"
                st.session_state.parsed_transaction = None
                st.session_state.parsed_receipt     = None
                st.session_state.confirm_delete_id  = None
                st.rerun()
    if st.session_state.sidebar_state == "collapsed":
        st.session_state.sidebar_state = "expanded"
    st.markdown("<hr style='border-color:rgba(255,255,255,.15);margin:16px 0'>", unsafe_allow_html=True)

    # ── Theme picker ──
    st.markdown(f"<div style='font-size:.72rem;font-weight:600;opacity:.6;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px'>🎨 Theme</div>", unsafe_allow_html=True)
    tcols = st.columns(len(THEMES))
    for i, tname in enumerate(THEMES.keys()):
        tv   = THEMES[tname]
        is_t = st.session_state.theme == tname
        with tcols[i]:
            border = f"2px solid {tv['accent3']}" if is_t else "2px solid transparent"
            st.markdown(f"""
            <div title="{tname}" style="width:24px;height:24px;border-radius:50%;
                background:linear-gradient(135deg,{tv['accent']},{tv['accent3']});
                border:{border};margin:0 auto 2px;cursor:pointer;">
            </div>""", unsafe_allow_html=True)
            if st.button("", key=f"t_{i}", help=tname):
                st.session_state.theme = tname
                st.rerun()

    # ── Spacer to push avatar to bottom ──
    st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
    for _ in range(2):
        st.markdown("&nbsp;", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(255,255,255,.15);margin:8px 0 12px'>", unsafe_allow_html=True)

    # ── Avatar chip at bottom — click to open profile/settings ──
    is_profile = st.session_state.current_page == "Profile"
    if st.button(
        f"{'⚙️' if is_profile else '👤'}  {display}",
        key="avatar_btn",
        use_container_width=True,
        help="Account & Settings"
    ):
        if is_profile:
            st.session_state.current_page = "Dashboard"
        else:
            st.session_state.current_page = "Profile"
            st.session_state.parsed_transaction = None
            st.session_state.parsed_receipt     = None
            st.session_state.confirm_delete_id  = None
            st.session_state.sidebar_state = "collapsed"
        st.rerun()

    st.markdown(f"<div style='font-size:.68rem;opacity:.45;text-align:center;margin-top:6px'>{t('app.session_active')} · {t('app.auto_logout')}</div>", unsafe_allow_html=True)

# Active page
choice = st.session_state.current_page

# ═══════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════
if choice == "Dashboard":
    st.markdown(f"<div class='section-title'>📊 {t('dashboard.title')}</div>", unsafe_allow_html=True)
    df = get_transactions_df()

    if not df.empty:
        cur_month      = datetime.now().strftime("%Y-%m")
        mdf            = df[df["date"].dt.strftime("%Y-%m") == cur_month]
        total_income   = mdf[mdf["type"] == "income"]["amount"].sum()
        total_expenses = mdf[mdf["type"] == "expense"]["amount"].sum()
        net_flow       = total_income - total_expenses
        budget         = get_budget(st.session_state.user_id)

        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric(t("dashboard.income"),   Rs(total_income))
        with c2: st.metric(t("dashboard.expenses"), Rs(total_expenses))
        with c3:
            st.metric(t("dashboard.net_flow"), Rs(net_flow),
                      delta=f"{'▲' if net_flow>=0 else '▼'} {Rs(abs(net_flow),0)}",
                      delta_color="normal" if net_flow>=0 else "inverse")
        with c4:
            if budget:
                util = (total_expenses / budget) * 100
                st.metric(t("dashboard.budget_used"), f"{util:.1f}%",
                          delta=t("dashboard.remaining", amount=Rs(budget-total_expenses,0)),
                          delta_color="normal" if total_expenses<=budget else "inverse")
            else:
                st.metric(t("dashboard.budget_used"), t("dashboard.budget_not_set"))

        if budget:
            progress  = min(total_expenses / budget, 1.0)
            bar_class = "progress-danger" if progress > 0.85 else ""
            st.markdown(f"""
            <div style="margin:12px 0 20px">
                <div style="display:flex;justify-content:space-between;font-size:.82rem;color:{T['subtext']};margin-bottom:4px">
                    <span>{t('dashboard.budget_progress')}</span>
                    <span>{Rs(total_expenses,0)} / {Rs(budget,0)}</span>
                </div>
                <div class="progress-bar"><div class="progress-fill {bar_class}" style="width:{progress*100:.1f}%"></div></div>
            </div>""", unsafe_allow_html=True)

        st.divider()
        c1,c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='section-title'>{t('dashboard.spending_by_category')}</div>", unsafe_allow_html=True)
            cat_spend = df[df["type"]=="expense"].groupby("category")["amount"].sum()
            if not cat_spend.empty:
                fig = px.pie(values=cat_spend.values, names=cat_spend.index, hole=0.4,
                             color_discrete_sequence=px.colors.sequential.Purples_r)
                fig.update_layout(margin=dict(t=0,b=0,l=0,r=0),
                                  legend=dict(orientation="h",yanchor="bottom",y=-0.3))
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown(f"<div class='section-title'>{t('dashboard.monthly_net_flow')}</div>", unsafe_allow_html=True)
            ms = get_monthly_summary(st.session_state.user_id)
            if ms:
                fig = px.area(pd.DataFrame(ms), x="month", y="net",
                              color_discrete_sequence=[T["accent"]],
                              labels={"net":"Net (₹)","month":""})
                fig.update_layout(margin=dict(t=0,b=0,l=0,r=0))
                st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"<div class='section-title'>{t('dashboard.recent_transactions', count=len(df))}</div>", unsafe_allow_html=True)
        for _, row in df.sort_values("date", ascending=False).head(5).iterrows():
            badge  = "badge-income" if row["type"]=="income" else "badge-expense"
            symbol = "+" if row["type"]=="income" else "-"
            color  = "#10b981" if row["type"]=="income" else "#ef4444"
            c1,c2,c3,c4 = st.columns([3,2,1.5,1.5])
            with c1: st.write(row["note"][:55]+("…" if len(row["note"])>55 else ""))
            with c2: st.markdown(f"<span class='badge {badge}'>{row['category'].title()}</span>", unsafe_allow_html=True)
            with c3: st.markdown(f"<span style='color:{color};font-weight:600'>{symbol}{Rs(row['amount'])}</span>", unsafe_allow_html=True)
            with c4: st.caption(row["date"].strftime("%d %b %Y"))
            st.divider()

        # BUG FIX: avoid divide-by-zero when income=0
        with st.expander(t("dashboard.tips.title")):
            if total_income == 0:
                st.info(t("dashboard.tips.no_income"))
            elif total_expenses > total_income * 0.9:
                st.error(t("dashboard.tips.critical"))
            elif total_expenses > total_income * 0.7:
                st.warning(t("dashboard.tips.warning"))
            elif net_flow > total_income * 0.2:
                st.success(t("dashboard.tips.great"))
            else:
                st.info(t("dashboard.tips.advice"))
    else:
        st.markdown(f'<div class="empty-state"><h3>{t("dashboard.no_transactions")}</h3><p>{t("dashboard.no_transactions_desc")}</p></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# ADD TRANSACTION
# ═══════════════════════════════════════════════════════
elif choice == "Add Transaction":
    st.markdown(f"<div class='section-title'>{t('add_transaction.title')}</div>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        user_input = st.text_input(t("add_transaction.input_label"), placeholder=t("add_transaction.input_placeholder"))
        if st.button(t("add_transaction.parse_btn"), use_container_width=True):
            if not user_input.strip():
                st.error(t("add_transaction.errors.empty_input"))
            else:
                parsed = parse_transaction(user_input)
                if parsed:
                    if parsed["category"] == "other":
                        suggested = suggest_category(user_input)
                        if suggested and suggested in CATEGORIES:
                            parsed["category"] = suggested
                            st.info(t("add_transaction.ai_suggested", category=suggested))
                    st.session_state.parsed_transaction = parsed
                    st.success("✅ Parsed successfully!")
                else:
                    st.error(t("add_transaction.errors.parse_failed"))

    with c2:
        if st.session_state.parsed_transaction:
            parsed = st.session_state.parsed_transaction
            st.markdown(f"<div class='section-title'>{t('add_transaction.confirm_title')}</div>", unsafe_allow_html=True)
            badge = "badge-income" if parsed["type"]=="income" else "badge-expense"
            st.markdown(f"**Amount:** {Rs(parsed['amount'])} &nbsp;<span class='badge {badge}'>{parsed['type'].title()}</span>", unsafe_allow_html=True)
            categories = list(CATEGORIES.keys())
            sel_cat  = st.selectbox(t("add_transaction.category_label"), categories,
                                    index=categories.index(parsed["category"]) if parsed["category"] in categories else 0)
            txn_date = st.date_input(t("add_transaction.date_label"), datetime.now())
            note     = st.text_area(t("add_transaction.note_label"), parsed["note"])
            if st.button(t("add_transaction.save_btn"), use_container_width=True):
                parsed.update({"category":sel_cat,"date":txn_date.strftime("%Y-%m-%d %H:%M:%S"),"note":note})
                add_transaction(st.session_state.user_id, parsed)
                st.session_state.parsed_transaction = None   # BUG FIX: clear after save
                st.success(t("add_transaction.success", type=parsed["type"], amount=Rs(parsed["amount"]), category=sel_cat))
                st.balloons()

# ═══════════════════════════════════════════════════════
# UPLOAD RECEIPT
# ═══════════════════════════════════════════════════════
elif choice == "Upload Receipt":
    st.markdown(f"<div class='section-title'>{t('upload_receipt.title')}</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(t("upload_receipt.upload_label"), type=["png","jpg","jpeg"])

    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Receipt", use_container_width=True)  # BUG FIX: deprecated param
        with st.spinner("Extracting text…"):
            with open("temp_receipt.jpg","wb") as f: f.write(uploaded_file.getbuffer())
            extracted_text = extract_text_from_image("temp_receipt.jpg")
        st.text_area(t("upload_receipt.extracted_text"), extracted_text, height=140)

        if st.button(t("upload_receipt.parse_btn"), use_container_width=True):
            parsed = parse_transaction(extracted_text)
            if parsed:
                if parsed["category"] == "other":
                    suggested = suggest_category(extracted_text)
                    if suggested and suggested in CATEGORIES:
                        parsed["category"] = suggested
                        st.info(t("add_transaction.ai_suggested", category=suggested))
                st.session_state.parsed_receipt = parsed
                st.success(t("upload_receipt.parse_success"))
            else:
                st.warning(t("upload_receipt.parse_failed"))

    if st.session_state.parsed_receipt:
        parsed = st.session_state.parsed_receipt
        st.markdown("<div class='section-title'>Transaction Details</div>", unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            st.write(f"**Amount:** {Rs(parsed['amount'])}")
            st.write(f"**Type:** {parsed['type'].title()}")
        with c2:
            categories = list(CATEGORIES.keys())
            sel_cat  = st.selectbox(t("add_transaction.category_label"), categories,
                                    index=categories.index(parsed["category"]) if parsed["category"] in categories else 0)
            txn_date = st.date_input(t("add_transaction.date_label"), datetime.now())
        note = st.text_area(t("add_transaction.note_label"), parsed["note"])
        if st.button(t("upload_receipt.save_btn"), use_container_width=True):
            parsed.update({"category":sel_cat,"date":txn_date.strftime("%Y-%m-%d %H:%M:%S"),"note":note})
            add_transaction(st.session_state.user_id, parsed)
            st.session_state.parsed_receipt = None   # BUG FIX: clear after save
            st.success(t("upload_receipt.success"))
            with st.spinner("AI explanation…"):
                explanation = get_expense_description(parsed["note"], parsed["amount"])
                st.info(f"💬 {explanation}")

# ═══════════════════════════════════════════════════════
# FETCH EMAILS
# ═══════════════════════════════════════════════════════
elif choice == "Fetch Emails":
    st.markdown(f"<div class='section-title'>{t('fetch_emails.title')}</div>", unsafe_allow_html=True)
    st.info(t("fetch_emails.info"))
    if st.button(t("fetch_emails.fetch_btn"), use_container_width=True):
        with st.spinner("Fetching emails…"):
            new_txns = fetch_transaction_emails()
            if new_txns:
                for txn in new_txns:
                    add_transaction(st.session_state.user_id, txn)  # BUG FIX: user_id included
                st.success(t("fetch_emails.success", count=len(new_txns)))
            else:
                st.info(t("fetch_emails.no_found"))

# ═══════════════════════════════════════════════════════
# VIEW TRANSACTIONS
# ═══════════════════════════════════════════════════════
elif choice == "View Transactions":
    st.markdown(f"<div class='section-title'>{t('view_transactions.title')}</div>", unsafe_allow_html=True)
    df = get_transactions_df()

    if not df.empty:
        with st.expander("🔽 Filters", expanded=True):
            c1,c2,c3,c4,c5 = st.columns(5)
            with c1: start_date = st.date_input(t("view_transactions.filter_from"), df["date"].min().date())
            with c2: end_date   = st.date_input(t("view_transactions.filter_to"),   df["date"].max().date())
            with c3:
                cats    = [t("view_transactions.filter_all")] + sorted(df["category"].unique().tolist())
                sel_cat = st.selectbox(t("view_transactions.filter_category"), cats)
            with c4:
                type_opts = [t("view_transactions.filter_all"),
                             t("view_transactions.filter_income"),
                             t("view_transactions.filter_expense")]
                sel_type = st.selectbox(t("view_transactions.filter_type"), type_opts)
            with c5:
                search = st.text_input("🔍 Search", placeholder=t("view_transactions.search_placeholder"))

        # BUG FIX: use .copy() to avoid mutating original df
        fdf = df[(df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)].copy()
        if sel_cat  != t("view_transactions.filter_all"): fdf = fdf[fdf["category"] == sel_cat]
        if sel_type != t("view_transactions.filter_all"): fdf = fdf[fdf["type"] == sel_type.lower()]
        if search.strip(): fdf = fdf[fdf["note"].str.contains(search, case=False, na=False)]

        st.caption(t("view_transactions.showing", shown=len(fdf), total=len(df)))
        st.dataframe(fdf[["date","category","type","amount","note"]].rename(columns={
            "date":t("view_transactions.col_date"),
            "category":t("view_transactions.col_category"),
            "type":t("view_transactions.col_type"),
            "amount":t("view_transactions.col_amount"),
            "note":t("view_transactions.col_desc"),
        }), use_container_width=True)

        st.download_button(t("view_transactions.export_btn"), data=fdf.to_csv(index=False),
                           file_name="transactions.csv", mime="text/csv")

        st.divider()
        st.markdown(f"<div class='section-title'>{t('view_transactions.edit_title')}</div>", unsafe_allow_html=True)

        if not fdf.empty:
            sel_id = st.selectbox("Select transaction", fdf.index.tolist(),
                format_func=lambda x: f"{fdf.loc[x,'date'].strftime('%d %b %Y')}  |  {fdf.loc[x,'note'][:35]}…  |  {Rs(fdf.loc[x,'amount'])}")
            txn = fdf.loc[sel_id]
            c1,c2 = st.columns(2)
            with c1:
                new_amount = st.number_input(t("view_transactions.col_amount"), value=float(txn["amount"]), min_value=0.0, step=1.0)
                new_cat    = st.selectbox(t("add_transaction.category_label"), list(CATEGORIES.keys()),
                                          index=list(CATEGORIES.keys()).index(txn["category"]) if txn["category"] in CATEGORIES else 0)
            with c2:
                new_type = st.selectbox(t("view_transactions.filter_type"), ["income","expense"],
                                        index=0 if txn["type"]=="income" else 1)
                new_date = st.date_input(t("add_transaction.date_label"), txn["date"].date())
            new_note = st.text_area(t("add_transaction.note_label"), txn["note"])

            bc1,bc2 = st.columns(2)
            with bc1:
                if st.button(t("view_transactions.update_btn"), use_container_width=True):
                    update_transaction(st.session_state.user_id, sel_id, {
                        "amount":new_amount,"category":new_cat,"type":new_type,
                        "date":new_date.strftime("%Y-%m-%d %H:%M:%S"),"note":new_note
                    })
                    st.success(t("view_transactions.update_success"))
                    st.rerun()
            with bc2:
                if st.session_state.confirm_delete_id == sel_id:
                    st.warning(t("view_transactions.confirm_delete"))
                    yc,nc = st.columns(2)
                    with yc:
                        if st.button(t("view_transactions.yes_delete"), use_container_width=True):
                            delete_transaction(st.session_state.user_id, sel_id)
                            st.session_state.confirm_delete_id = None
                            st.success(t("view_transactions.delete_success"))
                            st.rerun()
                    with nc:
                        if st.button(t("view_transactions.cancel"), use_container_width=True):
                            st.session_state.confirm_delete_id = None
                            st.rerun()
                else:
                    if st.button(t("view_transactions.delete_btn"), use_container_width=True):
                        st.session_state.confirm_delete_id = sel_id
                        st.rerun()
    else:
        st.markdown(f'<div class="empty-state"><h3>{t("view_transactions.no_transactions")}</h3><p>{t("view_transactions.no_transactions_desc")}</p></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# BUDGET PLANNING
# ═══════════════════════════════════════════════════════
elif choice == "Budget Planning":
    st.markdown(f"<div class='section-title'>{t('budget.title')}</div>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.subheader(t("budget.set_title"))
        cur_val = get_budget(st.session_state.user_id) or 0.0
        budget  = st.number_input(t("budget.input_label"), min_value=0.0, step=500.0, value=float(cur_val))
        if st.button(t("budget.save_btn"), use_container_width=True):
            set_budget(st.session_state.user_id, budget)
            st.success(t("budget.save_success"))
    with c2:
        st.subheader(t("budget.progress_title"))
        cur_budget = get_budget(st.session_state.user_id)
        if cur_budget:
            df = get_transactions_df()
            if not df.empty:
                cur_month = datetime.now().strftime("%Y-%m")
                spent     = df[(df["date"].dt.strftime("%Y-%m")==cur_month) & (df["type"]=="expense")]["amount"].sum()
                progress  = min(spent/cur_budget, 1.0)
                bar_cls   = "progress-danger" if progress > 0.85 else ""
                st.markdown(f"""
                <div style="margin:8px 0">
                    <div style="display:flex;justify-content:space-between;font-size:.82rem;color:{T['subtext']}">
                        <span>{t('budget.spent', amount=Rs(spent,0))}</span>
                        <span>{t('budget.budget_label', amount=Rs(cur_budget,0))}</span>
                    </div>
                    <div class="progress-bar"><div class="progress-fill {bar_cls}" style="width:{progress*100:.1f}%"></div></div>
                </div>""", unsafe_allow_html=True)
                if spent > cur_budget:       st.error(t("budget.exceeded"))
                elif progress > 0.8:         st.warning(t("budget.approaching"))
                else:                        st.success(t("budget.within"))
        else:
            st.info(t("budget.no_budget"))

    st.divider()
    st.subheader(t("budget.category_spending"))
    df2 = get_transactions_df()
    if not df2.empty:
        cs  = df2[df2["type"]=="expense"].groupby("category")["amount"].sum().reset_index()
        cs.columns = ["Category","Amount"]
        fig = px.bar(cs, x="Category", y="Amount",
                     color="Amount", color_continuous_scale=T["chart_scale"],
                     labels={"Amount":"Spent (₹)"})
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════
# SAVINGS GOALS
# ═══════════════════════════════════════════════════════
elif choice == "Savings Goals":
    st.markdown(f"<div class='section-title'>{t('savings.title')}</div>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.subheader(t("savings.new_goal"))
        goal_name     = st.text_input(t("savings.goal_name"), placeholder=t("savings.goal_placeholder"))
        target_amount = st.number_input(t("savings.target_amount"), min_value=1.0, step=500.0)
        deadline      = st.date_input(t("savings.target_date"), min_value=datetime.now().date())
        if st.button(t("savings.set_btn"), use_container_width=True):
            if goal_name and target_amount:
                set_savings_goal(st.session_state.user_id, goal_name, target_amount, deadline.strftime("%Y-%m-%d"))
                st.success(t("savings.set_success"))
                st.balloons()
            else:
                st.error(t("savings.errors.missing_fields"))
    with c2:
        st.subheader(t("savings.your_goals"))
        goals = get_savings_goal(st.session_state.user_id)
        if goals:
            df_g = get_transactions_df()
            total_saved = max(
                (df_g[df_g["type"]=="income"]["amount"].sum() -
                 df_g[df_g["type"]=="expense"]["amount"].sum()), 0
            ) if not df_g.empty else 0

            for goal in goals:
                # BUG FIX: guard division by zero if target somehow 0
                progress  = min(total_saved / goal["target"], 1.0) if goal["target"] > 0 else 0
                bar_cls   = "progress-danger" if progress >= 1.0 else ""
                days_left = (datetime.strptime(goal["deadline"],"%Y-%m-%d") - datetime.now()).days
                st.markdown(f"**{goal['name']}** — {Rs(goal['target'],0)} by {goal['deadline']}")
                st.caption(t("savings.saved_info", saved=Rs(total_saved,0), days=max(days_left,0)))
                st.markdown(f"""
                <div class="progress-bar"><div class="progress-fill {bar_cls}" style="width:{progress*100:.1f}%"></div></div>
                <div style="text-align:right;font-size:.75rem;color:{T['subtext']};margin-top:2px">{progress*100:.1f}%</div>
                """, unsafe_allow_html=True)
                st.divider()
        else:
            st.markdown(f'<div class="empty-state"><h3>{t("savings.no_goals")}</h3><p>{t("savings.no_goals_desc")}</p></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# FINANCIAL INSIGHTS
# ═══════════════════════════════════════════════════════
elif choice == "Financial Insights":
    st.markdown(f"<div class='section-title'>{t('insights.title')}</div>", unsafe_allow_html=True)
    df = get_transactions_df()

    if not df.empty:
        c1,c2 = st.columns(2)
        with c1:
            cat_spend = df[df["type"]=="expense"].groupby("category")["amount"].sum()
            if not cat_spend.empty:
                fig = px.pie(values=cat_spend.values, names=cat_spend.index,
                             title=t("insights.by_category"), hole=0.4,
                             color_discrete_sequence=px.colors.sequential.Purples_r)
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            # BUG FIX: use .copy() before adding a column to avoid SettingWithCopyWarning
            df_w = df[df["type"]=="expense"].copy()
            df_w["week"] = df_w["date"].dt.isocalendar().week
            weekly = df_w.groupby("week")["amount"].sum().reset_index()
            fig = px.bar(weekly, x="week", y="amount", title=t("insights.weekly"),
                         color="amount", color_continuous_scale=T["chart_scale"],
                         labels={"week":"Week No.","amount":"Amount (₹)"})
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader(t("insights.prediction_title"))
        predicted = predict_next_month_expense(df)
        if predicted:
            expense_series = df[df["type"]=="expense"].groupby(df["date"].dt.to_period("M"))["amount"].sum()
            hist_avg  = expense_series.mean() if len(expense_series) > 0 else 0
            # BUG FIX: guard division by zero
            delta_pct = ((predicted - hist_avg) / hist_avg * 100) if hist_avg else 0
            c1,c2,c3 = st.columns(3)
            c1.metric(t("insights.predicted"), Rs(predicted, 0))
            c2.metric(t("insights.hist_avg"),  Rs(hist_avg,  0))
            c3.metric(t("insights.delta"),     f"{delta_pct:+.1f}%",
                      delta_color="inverse" if delta_pct>0 else "normal")
            if delta_pct > 20:    st.warning(t("insights.prediction_high"))
            elif delta_pct < -20: st.success(t("insights.prediction_low"))

        st.divider()
        st.subheader(t("insights.monthly_comparison"))
        monthly_exp = df[df["type"]=="expense"].groupby(
            df["date"].dt.to_period("M"))["amount"].sum().tail(6).reset_index()
        monthly_exp.columns = ["Month","Amount"]
        monthly_exp["Month"] = monthly_exp["Month"].astype(str)
        fig = px.bar(monthly_exp, x="Month", y="Amount",
                     color="Amount", color_continuous_scale=T["chart_scale"],
                     labels={"Amount":"Expenses (₹)"})
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown(f'<div class="empty-state"><h3>{t("insights.no_data")}</h3><p>{t("insights.no_data_desc")}</p></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# PROFILE / SETTINGS PANEL — opens via avatar chip click
# ═══════════════════════════════════════════════════════
elif choice == "Profile":
    st.markdown(f"<div class='section-title'>⚙️ Account Settings</div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["👤 Change Username", "🔑 Change Password", "🎨 Theme & Data"])

    # ── TAB 1: Change Username (once every 15 days) ──
    with tab1:
        last_change_str = get_user_setting(st.session_state.user_id, "username_last_changed")
        days_since      = None
        can_change      = True
        if last_change_str:
            last_change = datetime.strptime(last_change_str, "%Y-%m-%d")
            days_since  = (datetime.now() - last_change).days
            can_change  = days_since >= 15

        if not can_change:
            days_left = 15 - days_since
            st.warning(f"⏳ Username can only be changed **once every 15 days**. **{days_left} days** remaining until the next change.")
        else:
            st.info("✏️ Want to change your username? Remember — this can only be done **once every 15 days**.")

        with st.form("change_username_form"):
            st.markdown(f"**Current username:** `{st.session_state.username}`")
            new_uname    = st.text_input("New Username", placeholder="3–20 chars, letters/numbers/underscore")
            st.caption("ℹ️ 3–20 characters · Only letters, numbers, underscores · Cannot start with a number")
            submit_uname = st.form_submit_button("✅ Update Username", use_container_width=True, disabled=not can_change)

            if submit_uname and can_change:
                stripped = new_uname.strip()
                if not stripped:
                    st.error("Please enter a new username.")
                elif len(stripped) < 3:
                    st.error("👤 Username must be at least 3 characters.")
                elif len(stripped) > 20:
                    st.error("👤 Username cannot exceed 20 characters.")
                elif not re.match(r"^[a-zA-Z0-9_]+$", stripped):
                    st.error("👤 Only letters, numbers, and underscores allowed.")
                elif stripped[0].isdigit():
                    st.error("👤 Cannot start with a number.")
                elif stripped == st.session_state.username:
                    st.error("Yeh toh pehle se hi tera username hai! 😄")
                else:
                    success = update_username(st.session_state.user_id, stripped)
                    if success:
                        set_user_setting(st.session_state.user_id, "username_last_changed",
                                         datetime.now().strftime("%Y-%m-%d"))
                        st.session_state.username = stripped
                        st.success(f"✅ Username badal ke **{stripped}** kar diya!")
                        st.rerun()
                    else:
                        st.error(f"❌ Username **'{stripped}'** already taken hai.")

    # ── TAB 2: Change Password (anytime) ──
    with tab2:
        st.info("🔑 Feel free to change your password anytime to keep your account secure.")
        with st.form("change_password_form"):
            old_pass    = st.text_input("Current Password",     type="password", placeholder="Enter current password")
            new_pass    = st.text_input("New Password",          type="password", placeholder="Min 8 chars, include a number")
            conf_pass   = st.text_input("Confirm New Password",  type="password", placeholder="Repeat new password")
            submit_pass = st.form_submit_button("🔑 Update Password", use_container_width=True)

            if submit_pass:
                if not old_pass or not new_pass or not conf_pass:
                    st.error("Please fill all fields.")
                elif len(new_pass) < 8:
                    st.error("🔑 Password must be at least 8 characters.")
                elif not any(c.isdigit() for c in new_pass):
                    st.error("🔢 Password must contain at least one number.")
                elif new_pass != conf_pass:
                    st.error("❌ New passwords do not match.")
                else:
                    result = verify_user(st.session_state.username, old_pass)
                    if not result:
                        st.error("❌ Current password is incorrect.")
                    else:
                        update_password(st.session_state.user_id, new_pass)
                        st.success("✅ Password successfully updated!")

    # ── TAB 3: Theme & Data ──
    with tab3:
        st.subheader("🎨 App Theme")
        theme_cols = st.columns(len(THEMES))
        for i,(tname,tvals) in enumerate(THEMES.items()):
            with theme_cols[i]:
                is_active    = st.session_state.theme == tname
                border_style = f"3px solid white;box-shadow:0 0 0 3px {tvals['accent']}" if is_active else "3px solid #e5e7eb"
                st.markdown(f"""
                <div style="text-align:center;margin-bottom:4px">
                    <div style="width:40px;height:40px;border-radius:50%;margin:0 auto 6px;
                        background:linear-gradient(135deg,{tvals['accent']},{tvals['accent3']});
                        border:{border_style}"></div>
                    <div style="font-size:.68rem;font-weight:{'700' if is_active else '400'}">{tname.split()[0]}</div>
                </div>""", unsafe_allow_html=True)
                if st.button("✓" if is_active else "Pick", key=f"pt_{i}", use_container_width=True):
                    st.session_state.theme = tname
                    st.rerun()

        st.divider()
        st.subheader("📂 Data Management")
        if st.button("⬇️ Export All Data as CSV", use_container_width=True):
            df_exp = get_transactions_df()
            if not df_exp.empty:
                st.download_button("Download CSV", data=df_exp.to_csv(index=False),
                                   file_name="budgetbuddy_export.csv", mime="text/csv")
            else:
                st.warning("No data to export.")

        st.divider()
        st.subheader("🔔 Notifications")
        saved_email  = get_user_setting(st.session_state.user_id, "email_notifications") == "True"
        saved_budget = get_user_setting(st.session_state.user_id, "budget_alerts")       == "True"
        email_notif  = st.checkbox("Enable Email Notifications",       value=saved_email)
        budget_alert = st.checkbox("Enable Budget Alert Notifications", value=saved_budget)
        if st.button("💾 Save Preferences", use_container_width=True):
            set_user_setting(st.session_state.user_id, "email_notifications", str(email_notif))
            set_user_setting(st.session_state.user_id, "budget_alerts",       str(budget_alert))
            st.success("✅ Saved!")