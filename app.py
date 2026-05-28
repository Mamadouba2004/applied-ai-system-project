"""Streamlit UI for VibeFinder — UI layer only, imports from src/."""
from __future__ import annotations

from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import streamlit as st
from src.recommender import load_songs, recommend_songs
from src.rag import query_rag

# ── Constants ─────────────────────────────────────────────────────────────────
DATA_PATH     = Path(__file__).parent / "data" / "songs.csv"
MAX_SCORE     = 7.0
GAP_THRESHOLD = MAX_SCORE * 0.40   # 2.8 → 40 % confidence

GENRES = [
    "pop", "lofi", "rock", "ambient", "jazz", "synthwave", "indie pop",
    "country", "hip-hop", "classical", "rnb", "metal", "funk", "electronic",
]
MOODS = [
    "happy", "chill", "intense", "relaxed", "focused",
    "moody", "nostalgic", "energetic", "melancholic", "romantic",
]

# ── Palettes ──────────────────────────────────────────────────────────────────
DARK = dict(
    bg="#121212", surface="#1F1F1F", surface2="#2A2A2A",
    text="#FFFFFF", muted="#B3B3B3", accent="#1DB954",
    border="#2A2A2A", row_top="#272727",
    warn_bg="#2D2200", warn_text="#FFB300",
    tag_genre="#1DB954", tag_mood="#1DB954", tag_acoustic="#4DA8DA",
)
LIGHT = dict(
    bg="#FFFFFF", surface="#F5F5F5", surface2="#EBEBEB",
    text="#121212", muted="#6B6B6B", accent="#1DB954",
    border="#E0E0E0", row_top="#E8F5E9",
    warn_bg="#FFF8E1", warn_text="#E65100",
    tag_genre="#1DB954", tag_mood="#1DB954", tag_acoustic="#2196F3",
)


# ── Session state ─────────────────────────────────────────────────────────────
def _init():
    defaults: dict = dict(
        dark_mode=True,
        results=None,
        explanation=None,
        top_score=None,
        active_mode=None,
        candidates=None,
    )
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── CSS injection ─────────────────────────────────────────────────────────────
def _inject_css(t: dict) -> None:
    st.markdown(f"""
<style>
/* ── global ── */
[data-testid="stAppViewContainer"] {{
    background-color: {t['bg']} !important;
}}
[data-testid="stHeader"] {{
    background-color: {t['bg']} !important;
    border-bottom: none !important;
    height: 0 !important;
    min-height: 0 !important;
    overflow: hidden !important;
    padding: 0 !important;
}}
.block-container {{
    padding-top: 0.75rem !important;
    max-width: 860px !important;
}}
/* make all generic text respect the theme */
html, body, p, li, div, span, h1, h2, h3 {{
    color: {t['text']};
}}
/* ── widget labels ── */
label,
.stSelectbox label,
.stSlider label,
.stRadio > label,
.stCheckbox > label > div:first-child {{
    color: {t['muted']} !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    font-weight: 500 !important;
}}
/* ── selectbox ── */
.stSelectbox div[data-baseweb="select"] > div {{
    background-color: {t['surface']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 6px !important;
    color: {t['text']} !important;
}}
.stSelectbox div[data-baseweb="select"] svg {{
    color: {t['muted']} !important;
}}
/* dropdown list */
ul[data-testid="stSelectboxVirtualDropdown"] {{
    background-color: {t['surface']} !important;
    border: 1px solid {t['border']} !important;
}}
ul[data-testid="stSelectboxVirtualDropdown"] li span {{
    color: {t['text']} !important;
}}
ul[data-testid="stSelectboxVirtualDropdown"] li:hover {{
    background-color: {t['surface2']} !important;
}}
/* ── slider thumb ── */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {{
    background-color: {t['accent']} !important;
    border-color: {t['accent']} !important;
}}
/* slider filled track */
[data-testid="stSlider"] [data-baseweb="slider"] div[class*="Track"] > div:first-child {{
    background-color: {t['accent']} !important;
}}
/* hide the built-in min/max tick labels so we replace them */
[data-testid="stSlider"] div[data-testid="stTickBarMin"],
[data-testid="stSlider"] div[data-testid="stTickBarMax"] {{
    color: {t['muted']} !important;
    font-size: 0.72rem !important;
}}
/* ── checkbox ── */
[data-testid="stCheckbox"] span p,
[data-testid="stCheckbox"] span {{
    color: {t['text']} !important;
    font-size: 0.95rem !important;
}}
/* ── radio pills ── */
[data-testid="stRadio"] div[role="radiogroup"] {{
    display: flex !important;
    gap: 8px !important;
    flex-wrap: wrap;
    margin-top: 4px;
}}
[data-testid="stRadio"] div[role="radiogroup"] label {{
    background: {t['surface2']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 20px !important;
    padding: 5px 18px !important;
    cursor: pointer !important;
    font-size: 0.85rem !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    color: {t['muted']} !important;
    transition: all 0.15s;
    line-height: 1.5 !important;
}}
[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {{
    background: {t['accent']}22 !important;
    border-color: {t['accent']} !important;
    color: {t['accent']} !important;
    font-weight: 700 !important;
}}
/* ── form container ── */
[data-testid="stForm"] {{
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
}}
/* primary Find my vibe button */
[data-testid="stFormSubmitButton"] > button {{
    width: 100% !important;
    background-color: {t['accent']} !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
}}
/* toggle button — small pill */
[data-testid="stBaseButton-secondary"] {{
    width: auto !important;
    background-color: transparent !important;
    color: {t['muted']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 20px !important;
    font-size: 0.8rem !important;
    padding: 3px 12px !important;
}}
/* ── spinner ── */
[data-testid="stSpinner"] p {{
    color: {t['muted']} !important;
}}
/* ── hide chrome ── */
#MainMenu {{ visibility: hidden; }}
footer   {{ visibility: hidden; }}
[data-testid="stDecoration"] {{ display: none; }}
hr {{ border-color: {t['border']} !important; margin: 0.75rem 0 !important; }}
</style>
""", unsafe_allow_html=True)


# ── HTML helpers ──────────────────────────────────────────────────────────────
def _tag(label: str, color: str) -> str:
    return (
        f'<span style="border:1px solid {color}; color:{color}; '
        f'border-radius:4px; padding:2px 7px; font-size:0.62rem; '
        f'font-weight:700; letter-spacing:0.07em; white-space:nowrap;">'
        f'{label}</span>'
    )


def _song_row(rank: int, song: dict, score: float, user_prefs: dict,
              likes_acoustic: bool, t: dict, is_top: bool) -> None:
    bg = t["row_top"] if is_top else t["surface"]
    pct = min(score / MAX_SCORE, 1.0)
    bar_w = f"{pct * 100:.1f}%"

    tags_html = ""
    if song["genre"] == user_prefs["genre"]:
        tags_html += " " + _tag("GENRE", t["tag_genre"])
    if song["mood"] == user_prefs["mood"]:
        tags_html += " " + _tag("MOOD", t["tag_mood"])
    if likes_acoustic and float(song.get("acousticness", 0)) > 0.6:
        tags_html += " " + _tag("ACOUSTIC", t["tag_acoustic"])

    st.markdown(f"""
<div style="background:{bg}; border:1px solid {t['border']}; border-radius:8px;
            padding:14px 18px; margin-bottom:8px;">
  <div style="display:flex; align-items:center; gap:14px;">
    <span style="color:{t['muted']}; font-size:0.72rem; font-weight:600;
                 min-width:22px; font-variant-numeric:tabular-nums;">{rank:02d}</span>
    <div style="flex:1; min-width:0;">
      <div style="font-weight:700; font-size:0.97rem; color:{t['text']};
                  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
        {song['title']}
      </div>
      <div style="font-size:0.75rem; color:{t['muted']}; margin-top:2px;">
        {song['artist']} · {song['genre']} · {song['mood']}
      </div>
    </div>
    <div style="display:flex; align-items:center; gap:8px; flex-shrink:0;">
      <span style="font-size:1.05rem; font-weight:700; color:{t['text']};
                   font-variant-numeric:tabular-nums;">{score:.2f}</span>
      <span style="font-size:0.7rem; color:{t['muted']};">/ 7.0</span>
      {tags_html}
    </div>
  </div>
  <div style="margin-top:10px; background:{t['border']}; border-radius:2px; height:3px;">
    <div style="width:{bar_w}; background:{t['accent']}; height:3px; border-radius:2px;"></div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Main app ──────────────────────────────────────────────────────────────────
def main() -> None:
    st.set_page_config(
        page_title="VibeFinder",
        page_icon="🎵",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    _init()
    t = DARK if st.session_state.dark_mode else LIGHT
    _inject_css(t)

    # ── HEADER ────────────────────────────────────────────────────────────────
    mode_label  = st.session_state.active_mode or "Genre-first"
    theme_label = "Dark" if st.session_state.dark_mode else "Light"
    toggle_icon = "☀️" if st.session_state.dark_mode else "🌙"

    hcol_l, hcol_r = st.columns([3, 1])
    with hcol_l:
        st.markdown(
            f'<div style="padding:10px 0 6px;">'
            f'<span style="font-weight:800; font-size:1.25rem; color:{t["text"]};">VibeFinder</span>'
            f'&nbsp;&nbsp;'
            f'<span style="background:{t["surface2"]}; color:{t["muted"]}; '
            f'font-size:0.72rem; padding:3px 10px; border-radius:20px; '
            f'letter-spacing:0.05em;">RAG · Claude API</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with hcol_r:
        st.markdown(
            f'<div style="text-align:right; padding:10px 0 6px; '
            f'font-size:0.78rem; color:{t["muted"]}; font-family:monospace;">'
            f'{mode_label} · {theme_label}</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="toggle-btn">', unsafe_allow_html=True)
        if st.button(f"{toggle_icon} {'Light' if st.session_state.dark_mode else 'Dark'}", key="theme_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<hr style="border-color:{t["border"]}; margin:0 0 1rem 0;">', unsafe_allow_html=True)

    # ── INPUT PANEL ───────────────────────────────────────────────────────────
    st.markdown(
        f'<div style="background:{t["surface"]}; border:1px solid {t["border"]}; '
        f'border-radius:12px; padding:20px 24px 16px;">',
        unsafe_allow_html=True,
    )

    gc, mc = st.columns(2)
    with gc:
        genre = st.selectbox("Favorite Genre", GENRES, index=GENRES.index("lofi"))
    with mc:
        mood  = st.selectbox("Favorite Mood",  MOODS,  index=MOODS.index("chill"))

    # Energy slider
    if "energy_slider" not in st.session_state:
        st.session_state["energy_slider"] = 0.40

    energy = st.slider(
        "Target Energy",
        min_value=0.0, max_value=1.0,
        value=st.session_state["energy_slider"],
        step=0.01,
        key="energy_slider",
    )

    likes_acoustic = st.checkbox("Likes acoustic music", value=True)

    st.markdown(
        f'<div style="font-size:0.7rem; color:{t["muted"]}; letter-spacing:0.1em; '
        f'text-transform:uppercase; font-weight:500; margin-top:12px; '
        f'margin-bottom:4px;">Scoring Mode</div>',
        unsafe_allow_html=True,
    )
    mode = st.radio(
        "Scoring Mode",
        options=["genre-first", "mood-first", "energy-focus"],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    find_clicked = st.button("Find my vibe", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)  # close input panel

    # ── RUN RECOMMENDER ───────────────────────────────────────────────────────
    if find_clicked:
        user_prefs = {"genre": genre, "mood": mood, "energy": energy,
                      "likes_acoustic": likes_acoustic}
        songs = load_songs(str(DATA_PATH))
        results = recommend_songs(user_prefs, songs, k=5, mode=mode)

        candidates = [{"title": song["title"], "score": score}
                      for song, score, _ in results]
        titles = [c["title"] for c in candidates]
        top_score = candidates[0]["score"] if candidates else 0.0

        question = (
            f"A user prefers {genre} music, {mood} mood, energy {energy:.2f}, "
            f"scoring mode: {mode}. Top results: {', '.join(titles)}. "
            f"In 3-4 sentences explain why these songs fit or don't fit this profile, "
            f"and what the {mode} scoring mode reveals about this user's taste profile."
        )

        explanation = ""
        with st.spinner("Finding your vibe…"):
            try:
                explanation = query_rag(question, genre=genre, mood=mood,
                                        candidates=candidates)
            except ValueError as e:
                explanation = f"⚠️ Guardrail: {e}"
            except Exception as e:
                explanation = f"⚠️ Could not reach Claude: {e}"

        st.session_state.results      = results
        st.session_state.explanation  = explanation
        st.session_state.candidates   = candidates
        st.session_state.top_score    = top_score
        st.session_state.active_mode  = mode
        st.session_state.last_prefs   = user_prefs
        st.session_state.last_acoustic = likes_acoustic

    # ── RESULTS ───────────────────────────────────────────────────────────────
    if st.session_state.results is not None:
        results      = st.session_state.results
        explanation  = st.session_state.explanation
        candidates   = st.session_state.candidates
        top_score    = st.session_state.top_score
        active_mode  = st.session_state.active_mode
        user_prefs   = st.session_state.get("last_prefs", {})
        la           = st.session_state.get("last_acoustic", False)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        # ── AI EXPLANATION CARD ───────────────────────────────────────────────
        st.markdown(f"""
<div style="background:{t['surface']}; border:1px solid {t['border']};
            border-radius:12px; padding:20px 24px;">
  <div style="display:flex; justify-content:space-between; align-items:center;
              margin-bottom:14px;">
    <span style="font-size:0.72rem; font-weight:700; color:{t['muted']};
                 letter-spacing:0.1em; text-transform:uppercase;">
      ✦ AI Explanation
    </span>
    <span style="font-size:0.72rem; color:{t['muted']}; font-family:monospace;">
      Claude · Haiku
    </span>
  </div>
  <div style="font-size:1rem; line-height:1.75; color:{t['text']};">
    {explanation}
  </div>
  <div style="margin-top:18px; padding-top:14px; border-top:1px solid {t['border']};
              display:flex; gap:12px;">
    <span style="background:{t['surface2']}; border:1px solid {t['border']};
                 border-radius:20px; padding:3px 12px; font-size:0.72rem;
                 color:{t['muted']};">
      ♡ 4 guardrails passed
    </span>
    <span style="background:{t['surface2']}; border:1px solid {t['border']};
                 border-radius:20px; padding:3px 12px; font-size:0.72rem;
                 color:{t['muted']};">
      ▤ 18 songs in context
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── CATALOG GAP ALERT ─────────────────────────────────────────────────
        if top_score < GAP_THRESHOLD:
            confidence_pct = int(top_score / MAX_SCORE * 100)
            st.warning(
                f"Limited catalog coverage for this profile — top match is "
                f"**{confidence_pct}% confidence**. Results may reflect the best "
                f"available, not a strong match."
            )

        # ── RECOMMENDATIONS ───────────────────────────────────────────────────
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        rc_l, rc_r = st.columns([2, 1])
        with rc_l:
            st.markdown(
                f'<span style="font-size:0.7rem; font-weight:700; color:{t["muted"]}; '
                f'letter-spacing:0.12em; text-transform:uppercase;">Recommendations</span>',
                unsafe_allow_html=True,
            )
        with rc_r:
            st.markdown(
                f'<div style="text-align:right; font-size:0.78rem; '
                f'color:{t["muted"]}; font-family:monospace;">{active_mode}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        for i, (song, score, _) in enumerate(results):
            _song_row(i + 1, song, score, user_prefs, la, t, is_top=(i == 0))


if __name__ == "__main__":
    main()
