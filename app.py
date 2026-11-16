"""TANDUR - Smart Crop Recommendation System for Madura Island.

Teknologi Analisis dan Rekomendasi untuk Dunia Usaha Pertanian Madura.
Pembuat: Fajar Setya Adhi - 20251233022 | Sistem Informasi, Fakultas Teknik, Universitas Islam Madura 2026
"""
from __future__ import annotations

import random
from datetime import datetime
from types import SimpleNamespace

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="TANDUR - Smart Crop Recommendation System for Madura Island | Fajar Setya Adhi",
    page_icon="🌱", layout="wide", initial_sidebar_state="auto",
)

from core import data as D  # noqa: E402
from core import model as M  # noqa: E402
from core import themes as T  # noqa: E402
from core.info import SKENARIO  # noqa: E402
from ui import components as C  # noqa: E402
from ui.pages import PAGE_FUNCS, PAGES  # noqa: E402
from ui.styles import build_css  # noqa: E402

FEATURE_KEYS = {"kabupaten": "in_kab", "musim": "in_mus", "jenis_tanah": "in_tnh", "suhu": "in_suhu",
                "kelembapan": "in_kel", "curah_hujan": "in_ch", "ph_tanah": "in_ph", "ketinggian": "in_tg"}
DEFAULT = SKENARIO[0][1]


# ------------------------------------------------------------------ cache
@st.cache_data(show_spinner=False)
def cached_data(path: str, mtime: float) -> pd.DataFrame:
    return D.load_dataframe()


@st.cache_resource(show_spinner=False)
def cached_model(path: str, mtime: float):
    return M.load_or_train()


def set_values(values: dict) -> None:
    """Callback: set nilai widget sidebar (aman dari StreamlitAPIException)."""
    for f, key in FEATURE_KEYS.items():
        st.session_state[key] = values[f]


def random_values(df: pd.DataFrame) -> None:
    v = {f: random.choice(D.CATEGORIES[f]) for f in D.CAT_COLS}
    v["suhu"] = round(random.uniform(df.suhu.min(), df.suhu.max()), 1)
    v["ph_tanah"] = round(random.uniform(df.ph_tanah.min(), df.ph_tanah.max()), 1)
    for f in ("kelembapan", "curah_hujan", "ketinggian"):
        v[f] = random.randint(int(df[f].min()), int(df[f].max()))
    set_values(v)


# ------------------------------------------------------------- data tidak ada
def missing_data_screen() -> None:
    st.markdown(build_css(T.palette(T.DEFAULT_THEME, "siang")), unsafe_allow_html=True)
    st.markdown("# 🌱 TANDUR")
    st.warning(f"File data **{D.DATA_NAME}** belum ditemukan. Letakkan file di folder proyek, atau unggah di sini.")
    up = st.file_uploader("Unggah data_rekomendasi_tanaman_madura.xlsx", ["xlsx", "csv"], key="boot_upload")
    if up is not None:
        try:
            new = D.read_uploaded(up.getvalue(), up.name)
            errs = D.validate_schema(new)
        except Exception as exc:
            errs = [f"File tidak dapat dibaca: {exc}"]
        if errs:
            st.error("Unggahan ditolak:\n\n" + "\n".join(f"- {e}" for e in errs))
        elif st.button("Simpan & mulai", type="primary", key="boot_save"):
            D.save_dataframe(new)
            st.cache_data.clear()
            st.rerun()
    st.markdown(f'<div class="tandur-footer">{C.FOOTER}</div>', unsafe_allow_html=True)
    st.stop()


def init_state() -> None:
    qp = st.query_params
    if "theme" not in st.session_state:
        t = qp.get("theme")
        st.session_state["theme"] = t if t in T.THEME_NAMES else T.DEFAULT_THEME
    if "night" not in st.session_state:
        st.session_state["night"] = qp.get("mode") == "malam"
    if "page" not in st.session_state:
        st.session_state["page"] = PAGES[0]
    for f, key in FEATURE_KEYS.items():
        if key not in st.session_state:
            st.session_state[key] = DEFAULT[f]
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("last_page", None)
    st.session_state.setdefault("last_tkey", None)


# ------------------------------------------------------------------ sidebar
def sidebar(df: pd.DataFrame) -> None:
    sb = st.sidebar
    sb.markdown('<div class="tandur-logo">🌱 TANDUR<small>Rekomendasi Tanaman Madura</small></div>', unsafe_allow_html=True)
    sb.markdown("### 🌿 Panel Kondisi Lahan")
    sb.caption("Pilih skenario cepat atau atur sendiri parameter lahan.")
    for i, (label, vals) in enumerate(SKENARIO):
        sb.button(label, key=f"sc_{i}", on_click=set_values, args=(vals,), **C.stretch_kw())
    r1, r2 = sb.columns(2)
    r1.button("🎲 Acak", key="sc_rand", on_click=random_values, args=(df,), help="Nilai acak dalam rentang data.", **C.stretch_kw())
    r2.button("↺ Reset", key="sc_reset", on_click=set_values, args=(DEFAULT,), help="Kembali ke nilai awal.", **C.stretch_kw())
    sb.selectbox("Kabupaten", D.CATEGORIES["kabupaten"], key="in_kab", help="Lokasi kabupaten lahan di Pulau Madura.")
    sb.selectbox("Musim", D.CATEGORIES["musim"], key="in_mus", help="Musim tanam: Hujan atau Kemarau.")
    sb.selectbox("Jenis tanah", D.CATEGORIES["jenis_tanah"], key="in_tnh",
                 help="Kapur, aluvial (subur, dekat sungai), regosol (berpasir), grumusol (liat, mengembang-mengerut).")
    sb.slider("Suhu (°C)", 20.0, 36.0, step=0.1, key="in_suhu", help="Suhu udara rata-rata dalam derajat Celsius.")
    sb.slider("Kelembapan (%)", 45, 95, key="in_kel", help="Kelembapan udara relatif dalam persen.")
    sb.slider("Curah hujan (mm/bulan)", 10, 350, key="in_ch", help="Curah hujan rata-rata per bulan dalam milimeter.")
    sb.slider("pH tanah", 4.5, 8.0, step=0.1, key="in_ph", help="Derajat keasaman tanah (7 = netral).")
    sb.slider("Ketinggian (mdpl)", 1, 350, key="in_tg", help="Ketinggian lokasi dari permukaan laut dalam meter.")
    sb.markdown("### 🎨 Tampilan")
    sb.toggle("☀️ Siang / 🌙 Malam", key="night", help="Aktif = mode malam.")
    c1, c2 = sb.columns([3, 1])
    c1.selectbox("Tema warna (25 pilihan)", T.THEME_NAMES, key="theme", help="Pilih palet warna aplikasi.")
    t = T.THEMES[st.session_state["theme"]]
    c2.markdown(f'<div style="display:flex;gap:3px;margin-top:2rem" aria-hidden="true">'
                + "".join(f'<span style="width:12px;height:26px;border-radius:6px;background:{t[k]};display:block"></span>'
                          for k in ("primary", "secondary", "accent")) + "</div>", unsafe_allow_html=True)
    sb.markdown(f'<div class="side-author"><b>{C.AUTHOR}</b><br>NIM {C.NIM}<br>{C.PRODI}, {C.FAKULTAS}<br>'
                f'{C.UNIV} 2026</div>', unsafe_allow_html=True)


def current_input() -> dict:
    s = st.session_state
    return {"kabupaten": s["in_kab"], "musim": s["in_mus"], "jenis_tanah": s["in_tnh"], "suhu": float(s["in_suhu"]),
            "kelembapan": float(s["in_kel"]), "curah_hujan": float(s["in_ch"]), "ph_tanah": float(s["in_ph"]),
            "ketinggian": float(s["in_tg"])}


def main() -> None:
    dp = D.data_path()
    if not dp.exists():
        missing_data_screen()
    try:
        df = cached_data(str(dp), dp.stat().st_mtime)
    except Exception as exc:
        st.error(f"Data tidak dapat dibaca: {exc}")
        st.stop()
    init_state()
    if "flash" in st.session_state:
        msg, icon = st.session_state.pop("flash")
        st.toast(msg, icon=icon)
    sidebar(df)

    mp = D.model_path()
    bundle, retrained = cached_model(str(mp), mp.stat().st_mtime if mp.exists() else 0.0)
    if retrained and not st.session_state.get("retrain_notified"):
        st.session_state["retrain_notified"] = True
        st.toast("Model dilatih ulang otomatis.", icon="🔁")

    x = current_input()
    proba = M.predict(bundle, x)
    top = max(proba, key=proba.get)
    conf = proba[top]

    mode = "malam" if st.session_state["night"] else "siang"
    theme = st.session_state["theme"]
    pal = T.palette(theme, mode)
    if st.query_params.get("theme") != theme or st.query_params.get("mode") != mode:
        st.query_params["theme"], st.query_params["mode"] = theme, mode
    st.markdown(build_css(pal), unsafe_allow_html=True)

    with st.container(key="banner"):
        st.markdown(C.banner_html(conf, pal), unsafe_allow_html=True)
        C.render_clock(pal)

    st.radio("Navigasi halaman", PAGES, horizontal=True, key="page", label_visibility="collapsed")
    page, tkey = st.session_state["page"], (theme, mode)
    s = st.session_state
    changed = (s["last_page"] is not None and s["last_page"] != page) or \
              (s["last_tkey"] is not None and s["last_tkey"] != tkey)

    # Riwayat otomatis (di Dashboard) - maks 50
    sig = tuple(x.values())
    if page == PAGES[0] and s.get("last_sig") != sig:
        s["last_sig"] = sig
        s["history"] = ([{"waktu": datetime.now().strftime("%H:%M:%S"), **{k: v for k, v in x.items()},
                          "rekomendasi": top, "keyakinan_%": round(conf * 100, 1)}] + s["history"])[:50]

    ctx = SimpleNamespace(df=df, bundle=bundle, x=x, proba=proba, top=top, conf=conf, pal=pal, mode=mode, theme=theme)
    try:
        if changed:
            with C.loading(page.split(" ", 1)[1] if s["last_page"] != page else "tema"):
                PAGE_FUNCS[page](ctx)
        else:
            PAGE_FUNCS[page](ctx)
    except Exception as exc:  # tidak menampilkan traceback mentah
        st.error(f"Terjadi kesalahan saat menampilkan halaman: {exc}")
    s["last_page"], s["last_tkey"] = page, tkey
    st.markdown(f'<div class="tandur-footer">{C.FOOTER}</div>', unsafe_allow_html=True)


main()
