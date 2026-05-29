"""Streamlit UI for VibeFinder — embeds the VibeFinder design (HTML/React)
inside a Streamlit component and bridges window.claude.complete() to the
real Anthropic API.

The dark UI, custom sliders, progress bars, AI card, and Tweaks panel all
live in vibefinder_ui.html and run inside the component iframe, which keeps
Streamlit's CSS from interfering (the source of the earlier UI bugs).
"""
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="VibeFinder",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    [data-testid="stAppViewContainer"] { background: #0F0F0F; }
    [data-testid="stVerticalBlock"] { gap: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

api_key = ""
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

ui_path = Path(__file__).parent / "vibefinder_ui.html"
html = ui_path.read_text(encoding="utf-8")

api_bridge = f"""<script>
window.claude = {{
  complete: async function(prompt) {{
    const key = "{api_key}";
    if (!key) throw new Error("No API key — set ANTHROPIC_API_KEY in Streamlit secrets.");
    const resp = await fetch("https://api.anthropic.com/v1/messages", {{
      method: "POST",
      headers: {{
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
        "anthropic-dangerous-direct-browser-access": "true"
      }},
      body: JSON.stringify({{
        model: "claude-haiku-4-5-20251001",
        max_tokens: 300,
        messages: [{{ role: "user", content: prompt }}]
      }})
    }});
    if (!resp.ok) {{
      const err = await resp.json().catch(() => ({{}}));
      throw new Error((err.error && err.error.message) || "API error " + resp.status);
    }}
    const data = await resp.json();
    return data.content[0].text;
  }}
}};
</script>
"""

html = html.replace("</head>", api_bridge + "\n</head>", 1)

components.html(html, height=1200, scrolling=True)
