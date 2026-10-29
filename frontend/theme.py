"""
frontend/theme.py
Custom Dark & Light Mode Themes & Reusable HTML Component Renderers for SchedulAI.
Supports instant seamless switching between Dark Navy and Modern Clean Light themes.
"""
import streamlit as st

def get_theme_css(mode: str = "dark") -> str:
    """Generates theme CSS tokens for Dark or Light mode."""
    if mode == "light":
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        /* Global Root Variables - Light Mode */
        :root {
            --bg-app: #f1f5f9;
            --bg-card: #ffffff;
            --bg-card-hover: #f8fafc;
            --bg-sidebar: #ffffff;
            --border-subtle: rgba(0, 0, 0, 0.08);
            --border-active: rgba(99, 102, 241, 0.5);
            --primary: #4f46e5;
            --primary-gradient: linear-gradient(135deg, #4f46e5, #6366f1);
            --success: #059669;
            --warning: #d97706;
            --danger: #e11d48;
            --text-main: #0f172a;
            --text-secondary: #475569;
            --text-muted: #64748b;
            --stat-sub-bg: rgba(0, 0, 0, 0.03);
            --radius-md: 10px;
            --radius-lg: 14px;
        }

        #MainMenu, header, footer, div[data-testid="stToolbar"] {
            visibility: hidden;
            height: 0%;
            position: fixed;
        }

        .stApp {
            background-color: var(--bg-app) !important;
            font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif !important;
            color: var(--text-main) !important;
        }

        /* Streamlit text elements in Light Mode */
        .stApp p, .stApp label, .stApp span, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
            color: var(--text-main);
        }

        section[data-testid="stSidebar"] {
            background-color: var(--bg-sidebar) !important;
            border-right: 1px solid var(--border-subtle) !important;
        }

        section[data-testid="stSidebar"] div.stButton > button {
            width: 100%;
            background: #f8fafc !important;
            color: #334155 !important;
            border: 1px solid rgba(0, 0, 0, 0.08) !important;
            border-radius: var(--radius-md) !important;
            padding: 0.6rem 1rem !important;
            font-weight: 600 !important;
            text-align: left !important;
            justify-content: flex-start !important;
            transition: all 0.2s ease !important;
            margin-bottom: 0.25rem;
        }

        section[data-testid="stSidebar"] div.stButton > button:hover {
            background: rgba(99, 102, 241, 0.1) !important;
            color: #4f46e5 !important;
            border-color: rgba(99, 102, 241, 0.4) !important;
            transform: translateX(3px);
        }

        div.stButton > button[kind="primary"] {
            background: var(--primary-gradient) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: var(--radius-md) !important;
            padding: 0.55rem 1.25rem !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.25) !important;
            transition: all 0.2s ease !important;
        }

        div.stButton > button[kind="primary"]:hover {
            opacity: 0.95 !important;
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(79, 70, 229, 0.35) !important;
        }

        div.stButton > button[kind="secondary"] {
            background: #ffffff !important;
            color: #1e293b !important;
            border: 1px solid rgba(0, 0, 0, 0.12) !important;
            border-radius: var(--radius-md) !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }

        div.stButton > button[kind="secondary"]:hover {
            background: rgba(99, 102, 241, 0.08) !important;
            border-color: rgba(99, 102, 241, 0.4) !important;
            color: #4f46e5 !important;
            transform: translateY(-1px);
        }

        .schedulai-card {
            background-color: #ffffff;
            border: 1px solid rgba(0, 0, 0, 0.08);
            border-radius: var(--radius-lg);
            padding: 1.35rem 1.5rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
        }

        .schedulai-hero {
            background: linear-gradient(135deg, #ffffff, #eef2ff);
            border: 1px solid rgba(99, 102, 241, 0.25);
            border-radius: var(--radius-lg);
            padding: 1.75rem 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(99, 102, 241, 0.08);
        }

        .stat-card {
            background-color: #ffffff;
            border: 1px solid rgba(0, 0, 0, 0.08);
            border-radius: var(--radius-lg);
            padding: 1.15rem 1.25rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            transition: all 0.2s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        }

        .stat-card:hover {
            border-color: rgba(99, 102, 241, 0.3);
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
        }

        .stat-icon {
            width: 46px;
            height: 46px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.35rem;
        }

        .stat-val {
            font-size: 1.6rem;
            font-weight: 800;
            color: #0f172a;
            line-height: 1.2;
        }

        .stat-label {
            font-size: 0.8rem;
            color: #64748b;
            font-weight: 600;
        }

        .schedulai-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.2rem 0.6rem;
            border-radius: 9999px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            margin-right: 0.4rem;
        }
        .badge-primary { background: rgba(99, 102, 241, 0.12); color: #4338ca; border: 1px solid rgba(99, 102, 241, 0.3); }
        .badge-success { background: rgba(16, 185, 129, 0.12); color: #047857; border: 1px solid rgba(16, 185, 129, 0.3); }
        .badge-warning { background: rgba(245, 158, 11, 0.12); color: #b45309; border: 1px solid rgba(245, 158, 11, 0.3); }
        .badge-danger  { background: rgba(244, 63, 94, 0.12);  color: #be123c; border: 1px solid rgba(244, 63, 94, 0.3); }
        </style>
        """
    else:
        # Default Dark Navy Theme
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        /* Global Root Variables - Dark Mode */
        :root {
            --bg-app: #0b1020;
            --bg-card: #121a30;
            --bg-card-hover: #182342;
            --bg-sidebar: #0e1426;
            --border-subtle: rgba(255, 255, 255, 0.08);
            --border-active: rgba(99, 102, 241, 0.45);
            --primary: #6366f1;
            --primary-gradient: linear-gradient(135deg, #6366f1, #818cf8);
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #f43f5e;
            --text-main: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --stat-sub-bg: rgba(255, 255, 255, 0.02);
            --radius-md: 10px;
            --radius-lg: 14px;
        }

        #MainMenu, header, footer, div[data-testid="stToolbar"] {
            visibility: hidden;
            height: 0%;
            position: fixed;
        }

        .stApp {
            background-color: var(--bg-app) !important;
            font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif !important;
            color: var(--text-main) !important;
        }

        section[data-testid="stSidebar"] {
            background-color: var(--bg-sidebar) !important;
            border-right: 1px solid var(--border-subtle) !important;
        }

        section[data-testid="stSidebar"] div.stButton > button {
            width: 100%;
            background: rgba(255, 255, 255, 0.03) !important;
            color: var(--text-secondary) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: var(--radius-md) !important;
            padding: 0.6rem 1rem !important;
            font-weight: 500 !important;
            text-align: left !important;
            justify-content: flex-start !important;
            transition: all 0.2s ease !important;
            margin-bottom: 0.25rem;
        }

        section[data-testid="stSidebar"] div.stButton > button:hover {
            background: rgba(99, 102, 241, 0.15) !important;
            color: #ffffff !important;
            border-color: rgba(99, 102, 241, 0.4) !important;
            transform: translateX(4px);
        }

        div.stButton > button[kind="primary"] {
            background: var(--primary-gradient) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: var(--radius-md) !important;
            padding: 0.55rem 1.25rem !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
            transition: all 0.2s ease !important;
        }

        div.stButton > button[kind="primary"]:hover {
            opacity: 0.95 !important;
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
        }

        div.stButton > button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.05) !important;
            color: #e2e8f0 !important;
            border: 1px solid rgba(255, 255, 255, 0.14) !important;
            border-radius: var(--radius-md) !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }

        div.stButton > button[kind="secondary"]:hover {
            background: rgba(99, 102, 241, 0.22) !important;
            border-color: rgba(99, 102, 241, 0.5) !important;
            color: #ffffff !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25) !important;
        }

        .schedulai-card {
            background-color: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 1.35rem 1.5rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        }

        .schedulai-hero {
            background: linear-gradient(135deg, rgba(18, 26, 48, 0.95), rgba(30, 41, 74, 0.95));
            border: 1px solid rgba(99, 102, 241, 0.35);
            border-radius: var(--radius-lg);
            padding: 1.75rem 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 8px 30px rgba(99, 102, 241, 0.15);
        }

        .stat-card {
            background-color: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 1.15rem 1.25rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            transition: all 0.2s ease;
        }

        .stat-card:hover {
            border-color: rgba(255, 255, 255, 0.15);
            transform: translateY(-2px);
        }

        .stat-icon {
            width: 46px;
            height: 46px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.35rem;
        }

        .stat-val {
            font-size: 1.6rem;
            font-weight: 800;
            color: #ffffff;
            line-height: 1.2;
        }

        .stat-label {
            font-size: 0.8rem;
            color: var(--text-secondary);
            font-weight: 500;
        }

        .schedulai-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.2rem 0.6rem;
            border-radius: 9999px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            margin-right: 0.4rem;
        }
        .badge-primary { background: rgba(99, 102, 241, 0.2); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.4); }
        .badge-success { background: rgba(16, 185, 129, 0.18); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.35); }
        .badge-warning { background: rgba(245, 158, 11, 0.18); color: #fde68a; border: 1px solid rgba(245, 158, 11, 0.35); }
        .badge-danger  { background: rgba(244, 63, 94, 0.18);  color: #fda4af; border: 1px solid rgba(244, 63, 94, 0.35); }
        </style>
        """

def apply_theme(theme_mode: str = "dark"):
    """Injects the custom CSS theme (Dark or Light) into the Streamlit session."""
    st.markdown(get_theme_css(theme_mode), unsafe_allow_html=True)

def page_header(title: str, subtitle: str):
    """Renders a sleek page title and description."""
    h_html = f'<div style="margin-bottom: 1.5rem;"><h1 style="font-size: 1.65rem; font-weight: 800; margin: 0 0 0.3rem 0;">{title}</h1><p style="font-size: 0.88rem; color: var(--text-secondary); margin: 0;">{subtitle}</p></div>'
    st.markdown(h_html, unsafe_allow_html=True)

def hero(title: str, description: str, badges: list = None):
    """Renders the executive Hero Card."""
    badges_html = ""
    if badges:
        for b_text, b_variant in badges:
            badges_html += f'<span class="schedulai-badge badge-{b_variant}">{b_text}</span>'
    h_html = f'<div class="schedulai-hero"><div style="margin-bottom: 0.75rem;">{badges_html}</div><h2 style="font-size: 1.5rem; font-weight: 800; margin: 0 0 0.5rem 0;">{title}</h2><p style="font-size: 0.9rem; line-height: 1.55; margin: 0; max-width: 850px; opacity: 0.92;">{description}</p></div>'
    st.markdown(h_html, unsafe_allow_html=True)

def stat_card(label: str, value: str, icon: str = "📊", bg_color: str = "rgba(99, 102, 241, 0.15)", subtext: str = ""):
    """Renders an analytical KPI stat tile with robust layout preventing text overlaps and markdown code block parsing."""
    display_icon = icon
    display_subtext = subtext

    if len(icon) > 4:
        display_subtext = icon
        if "teaching" in label.lower() or "load" in label.lower():
            display_icon = "⏱️"
        elif "faculty" in label.lower() or "teacher" in label.lower():
            display_icon = "👨‍🏫"
        elif "facility" in label.lower() or "room" in label.lower():
            display_icon = "🏛️"
        elif "quality" in label.lower() or "compliance" in label.lower():
            display_icon = "🎯"
        elif "fast" in label.lower() or "speed" in label.lower():
            display_icon = "⚡"
        elif "soft" in label.lower():
            display_icon = "✨"
        else:
            display_icon = "📊"

    if "badge-" in bg_color:
        if "primary" in bg_color:
            bg_color = "rgba(99, 102, 241, 0.18)"
        elif "success" in bg_color:
            bg_color = "rgba(16, 185, 129, 0.18)"
        elif "warning" in bg_color:
            bg_color = "rgba(245, 158, 11, 0.18)"
        elif "danger" in bg_color:
            bg_color = "rgba(244, 63, 94, 0.18)"
        else:
            bg_color = "rgba(56, 189, 248, 0.18)"

    subtext_html = f'<div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 0.18rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{display_subtext}</div>' if display_subtext else ""

    return f'<div class="stat-card"><div class="stat-icon" style="background: {bg_color}; flex-shrink: 0;">{display_icon}</div><div style="min-width: 0; flex: 1; overflow: hidden;"><div class="stat-val" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{value}</div><div class="stat-label" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{label}</div>{subtext_html}</div></div>'
