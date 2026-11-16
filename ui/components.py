"""Komponen UI: maskot SVG, loading overlay, tabel HTML ber-CSS, helper Plotly & API Streamlit."""
from __future__ import annotations

import html
import os
import time
from contextlib import contextmanager
from typing import Dict, Iterator, List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from core.info import PLANT_COLORS

AUTHOR = "Fajar Setya Adhi"
NIM = "20251233022"
PRODI = "Sistem Informasi"
FAKULTAS = "Fakultas Teknik"
UNIV = "Universitas Islam Madura"
FOOTER = f"© 2026 {AUTHOR} - {NIM} | {PRODI}, {FAKULTAS}, {UNIV}"


# ------------------------------------------------------------ kompatibilitas
def stretch_kw() -> dict:
    """Argumen lebar penuh yang cocok untuk versi Streamlit terpasang (tanpa warning)."""
    import inspect
    try:
        if "width" in inspect.signature(st.button).parameters:
            return {"width": "stretch"}
    except (TypeError, ValueError):
        pass
    return {"use_container_width": True}


def plot(fig: go.Figure, key: str) -> None:
    """Tampilkan Plotly dengan lebar penuh (kompatibel lintas versi)."""
    try:
        st.plotly_chart(fig, key=key, **stretch_kw(), config={"displaylogo": False})
    except TypeError:
        st.plotly_chart(fig, key=key, use_container_width=True, config={"displaylogo": False})


def min_load_seconds() -> float:
    return float(os.environ.get("TANDUR_LOAD_SECONDS", "0.55"))


# ------------------------------------------------------------------ loading
def _overlay(label: str) -> str:
    return (f'<div class="load-ov" role="status" aria-live="polite"><div class="load-box">'
            f'<div class="grow"><div class="stem"></div><div class="leaf l1"></div>'
            f'<div class="leaf l2"></div><div class="soil"></div></div>'
            f'<div class="load-text">Memuat {html.escape(label)}...</div></div></div>')


@contextmanager
def loading(label: str, min_seconds: float | None = None) -> Iterator[None]:
    """Overlay loading penuh-layar; selalu dikosongkan (try/finally)."""
    ph = st.empty()
    t0 = time.time()
    ph.markdown(_overlay(label), unsafe_allow_html=True)
    try:
        yield
    finally:
        try:
            wait = (min_load_seconds() if min_seconds is None else min_seconds) - (time.time() - t0)
            if wait > 0:
                time.sleep(wait)
        finally:
            ph.empty()


# ------------------------------------------------------------------- maskot
def mascot_svg(confidence: float, pal: Dict[str, str]) -> str:
    """Maskot 'Si Odheng': tanaman kecil bertopi odheng (ikat kepala batik)."""
    if confidence >= 0.75:
        eyes = '<circle cx="42" cy="86" r="4.2" fill="#2b2b2b"/><circle cx="68" cy="86" r="4.2" fill="#2b2b2b"/>' \
               '<circle cx="43.4" cy="84.6" r="1.4" fill="#fff"/><circle cx="69.4" cy="84.6" r="1.4" fill="#fff"/>'
        mouth = '<path d="M44 97 Q55 109 66 97" stroke="#2b2b2b" stroke-width="3" fill="#fff" stroke-linecap="round"/>'
        mood, brows = "senang", ""
    elif confidence >= 0.5:
        eyes = '<circle cx="42" cy="86" r="4" fill="#2b2b2b"/><circle cx="68" cy="86" r="4" fill="#2b2b2b"/>'
        mouth = '<path d="M46 99 L64 99" stroke="#2b2b2b" stroke-width="3" stroke-linecap="round"/>'
        mood, brows = "netral", ""
    else:
        eyes = '<circle cx="42" cy="87" r="4" fill="#2b2b2b"/><circle cx="68" cy="85" r="4" fill="#2b2b2b"/>'
        mouth = '<path d="M46 102 Q55 94 64 102" stroke="#2b2b2b" stroke-width="3" fill="none" stroke-linecap="round"/>'
        brows = '<path d="M35 79 Q41 74 48 77" stroke="#2b2b2b" stroke-width="2.4" fill="none"/><path d="M62 74 Q69 70 75 75" stroke="#2b2b2b" stroke-width="2.4" fill="none"/>'
        mood = "bingung"
    red, gold = "#B5403A", "#D9A441"
    return f"""<div class="mascot"><svg viewBox="0 0 110 150" role="img" aria-label="Maskot Si Odheng, tanaman kecil bertopi odheng batik Madura, ekspresi {mood}" xmlns="http://www.w3.org/2000/svg">
<title>Si Odheng ({mood})</title>
<ellipse cx="55" cy="143" rx="34" ry="5" fill="rgba(0,0,0,.18)"/>
<path d="M30 118 L80 118 L74 142 L36 142 Z" fill="#A9643A"/><rect x="26" y="112" width="58" height="10" rx="4" fill="#C27A48"/>
<path d="M55 112 C55 100 55 96 55 90" stroke="#4E8F3A" stroke-width="5" fill="none"/>
<circle cx="55" cy="84" r="30" fill="#8FCB6B"/><circle cx="55" cy="84" r="30" fill="url(#g)" opacity=".35"/>
<defs><radialGradient id="g" cx=".35" cy=".3"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000" stop-opacity=".25"/></radialGradient></defs>
<path d="M28 70 C8 60 6 44 18 40 C30 44 34 58 28 70 Z" fill="#6DB04F"/><path d="M82 70 C102 60 104 44 92 40 C80 44 76 58 82 70 Z" fill="#6DB04F"/>
<path d="M26 66 Q55 38 84 66 L84 72 Q55 50 26 72 Z" fill="{red}"/>
<path d="M26 66 Q55 38 84 66 L84 72 Q55 50 26 72 Z" fill="none" stroke="#7a2622" stroke-width="1.2"/>
<g fill="{gold}"><circle cx="38" cy="62" r="2.2"/><circle cx="48" cy="57.5" r="2.2"/><circle cx="58" cy="56.5" r="2.2"/><circle cx="68" cy="58.5" r="2.2"/><circle cx="76" cy="63" r="2.2"/></g>
<path d="M47 45 Q55 16 63 45 Q55 40 47 45 Z" fill="{red}" stroke="#7a2622" stroke-width="1.2"/><path d="M51 38 L59 38" stroke="{gold}" stroke-width="2"/>
{brows}{eyes}<ellipse cx="34" cy="96" rx="5" ry="3" fill="#F28B82" opacity=".6"/><ellipse cx="76" cy="96" rx="5" ry="3" fill="#F28B82" opacity=".6"/>{mouth}
</svg></div>"""


def banner_html(confidence: float, pal: Dict[str, str]) -> str:
    chips = (f'<span class="chip">👤 <b>{AUTHOR}</b></span><span class="chip">🆔 {NIM}</span>'
             f'<span class="chip">🎓 {PRODI}</span><span class="chip">🏛️ {FAKULTAS}</span>'
             f'<span class="chip">📍 {UNIV} 2026</span>')
    return f"""<div class="banner-grid"><div>
<h1 class="banner-title">TANDUR</h1>
<p class="banner-tag">Teknologi Analisis dan Rekomendasi untuk Dunia Usaha Pertanian Madura</p>
<p class="banner-en">SMART CROP RECOMMENDATION SYSTEM FOR MADURA ISLAND</p>
<p class="banner-sub">Sistem Pendukung Keputusan Rekomendasi Tanaman Berbasis K-Nearest Neighbors (KNN)</p>
<div class="chips">{chips}</div></div>{mascot_svg(confidence, pal)}</div>"""


def clock_html(pal: Dict[str, str]) -> str:
    """Jam real-time Asia/Jakarta (JS, tanpa rerun Streamlit); warna mengikuti tema."""
    return f"""<html><head><style>
html,body{{margin:0;background:transparent;font-family:'Inter',sans-serif;}}
#c{{display:inline-block;padding:7px 16px;border-radius:999px;font-weight:600;font-size:clamp(11px,3.2vw,14px);
color:{pal['text']};background:{pal['bg']};box-shadow:inset 3px 3px 7px {pal['sh_dark']},inset -3px -3px 7px {pal['sh_light']};white-space:nowrap;}}
#c b{{color:{pal['primary_text']};}}
</style></head><body><div id="c" role="timer" aria-label="Jam dan tanggal saat ini">🕒 <span id="t">memuat…</span></div>
<script>
const fmtD=new Intl.DateTimeFormat('id-ID',{{timeZone:'Asia/Jakarta',weekday:'long',day:'numeric',month:'long',year:'numeric'}});
const fmtT=new Intl.DateTimeFormat('id-ID',{{timeZone:'Asia/Jakarta',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false}});
function tick(){{const n=new Date();let tm=fmtT.format(n).replace(/\\./g,':');
document.getElementById('t').innerHTML=fmtD.format(n).replace(/(\\d{{4}})$/,'$1')+' • <b>'+tm+' WIB</b>';}}
tick();setInterval(tick,1000);
</script></body></html>"""


def render_clock(pal: Dict[str, str]) -> None:
    html_src = clock_html(pal)
    if hasattr(st, "iframe"):  # Streamlit baru: components.v1.html sudah deprecated
        st.iframe(html_src, height=48)
    else:
        components.html(html_src, height=48)


# ------------------------------------------------------------------- tabel
def table_html(df: pd.DataFrame) -> str:
    cols = "".join(f"<th>{html.escape(str(c))}</th>" for c in df.columns)
    rows = []
    for rec in df.itertuples(index=False):
        tds = []
        for v in rec:
            if isinstance(v, float):
                v = f"{v:.4g}" if abs(v) < 1e5 else f"{v:.0f}"
            tds.append(f"<td>{html.escape(str(v))}</td>")
        rows.append("<tr>" + "".join(tds) + "</tr>")
    return (f'<div class="tbl-wrap" tabindex="0" role="region" aria-label="Tabel data">'
            f'<table class="tbl"><thead><tr>{cols}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


def render_table(df: pd.DataFrame, page_size: int = 50, key: str = "tbl") -> None:
    """Tabel HTML ber-CSS dengan paginasi (mengikuti tema, scroll horizontal di mobile)."""
    n = len(df)
    pages = max(1, -(-n // page_size))
    page = 1
    if pages > 1:
        c1, c2 = st.columns([1, 3])
        page = int(c1.number_input("Halaman", 1, pages, 1, 1, key=f"{key}_page",
                                   help=f"{n} baris, {page_size} baris per halaman."))
        c2.caption(f"Menampilkan baris {(page - 1) * page_size + 1}-{min(n, page * page_size)} dari {n} "
                   f"(halaman {page}/{pages}).")
    st.markdown(table_html(df.iloc[(page - 1) * page_size: page * page_size]), unsafe_allow_html=True)


def bars_html(items: List[tuple], colors: Dict[str, str] | None = None) -> str:
    """Bar neumorphism: items = [(nama, nilai 0..1)]."""
    out = []
    for name, val in items:
        col = (colors or PLANT_COLORS).get(name, "var(--primary)")
        out.append(f'<div class="bar-row"><div class="bar-name">{html.escape(name)}</div>'
                   f'<div class="bar-track" role="progressbar" aria-valuenow="{val * 100:.0f}" aria-valuemin="0" aria-valuemax="100" aria-label="{html.escape(name)}">'
                   f'<div class="bar-fill" style="width:{max(2, val * 100):.1f}%;background:{col}"></div></div>'
                   f'<div class="bar-val">{val * 100:.1f}%</div></div>')
    return "".join(out)


# ------------------------------------------------------------------ plotly
def style_fig(fig: go.Figure, pal: Dict[str, str], height: int = 380, legend_bottom: bool = True) -> go.Figure:
    axis = dict(gridcolor=pal["grid"], zerolinecolor=pal["grid"], linecolor=pal["grid"],
                tickfont=dict(color=pal["text"]), title_font=dict(color=pal["text"]))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=height,
        font=dict(color=pal["text"], family="Inter, sans-serif"),
        margin=dict(l=10, r=10, t=44, b=10), title_font=dict(color=pal["text"], size=15),
        legend=dict(orientation="h", y=-0.22, x=0, font=dict(color=pal["text"]), bgcolor="rgba(0,0,0,0)")
        if legend_bottom else dict(font=dict(color=pal["text"]), bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(**axis)
    fig.update_yaxes(**axis)
    if getattr(fig.layout, "scene", None) is not None and any(t.type == "scatter3d" for t in fig.data):
        for ax in ("xaxis", "yaxis", "zaxis"):
            fig.update_layout(scene={ax: dict(backgroundcolor="rgba(0,0,0,0)", gridcolor=pal["grid"],
                                              color=pal["text"], showbackground=False)})
    return fig
