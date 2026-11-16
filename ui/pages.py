"""Halaman-halaman TANDUR (7 halaman)."""
from __future__ import annotations

import html
import sys
from types import SimpleNamespace
from typing import Dict

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sklearn
import streamlit as st

from core import data as D
from core import model as M
from core.info import (FAKTA_MADURA, KOORDINAT, PLANT_COLORS, PLANT_EMOJI, PLANTS, SARAN_FITUR)
from ui import components as C

PAGES = ["🎛️ Dashboard & Rekomendasi", "📊 Visualisasi 3D & 2D", "🧮 Bedah Perhitungan Manual",
         "📈 Evaluasi & Optimasi K", "📁 Manajemen Dataset", "🌾 Profil Tanaman Madura",
         "ℹ️ Tentang & Panduan"]

NUM_LABEL = {c: D.LABELS[c] for c in D.NUM_COLS}
FIT_LABEL = {"under": "Di bawah", "ok": "Sesuai", "over": "Di atas"}


def card(name: str):
    return st.container(key=f"card_{name}")


def _color(plant: str) -> str:
    return PLANT_COLORS.get(plant, "#888888")


def _x_df(x: Dict) -> pd.DataFrame:
    return pd.DataFrame([x])[D.CAT_COLS + D.NUM_COLS]


def _flash(msg: str, icon: str = "✅") -> None:
    st.session_state["flash"] = (msg, icon)


def _refresh_after_data_change(retrain: bool) -> None:
    st.cache_data.clear()
    if retrain:
        st.cache_resource.clear()
    st.rerun()


# ============================================================= 1. DASHBOARD
def page_dashboard(ctx: SimpleNamespace) -> None:
    df, x, proba, top = ctx.df, ctx.x, ctx.proba, ctx.top
    ranked = sorted(proba.items(), key=lambda kv: -kv[1])
    conf = ctx.conf
    emo = PLANT_EMOJI.get(top, "🌱")
    st.markdown(
        f'<div class="result-card" style="--rc:{_color(top)}"><div class="result-emoji">{emo}</div><div>'
        f'<div class="result-label">Tanaman yang direkomendasikan</div>'
        f'<div class="result-name">{html.escape(top)}</div>'
        f'<div class="result-conf">Tingkat keyakinan: {conf * 100:.1f}%</div></div></div>',
        unsafe_allow_html=True)
    st.write("")
    if conf < 0.5:
        st.warning("Keyakinan model di bawah 50%: kondisi lahan ini berada di wilayah yang 'abu-abu' "
                   "antar beberapa tanaman. Gunakan hasil dengan sangat hati-hati.")
    out = [c for c in D.NUM_COLS if not (df[c].min() <= x[c] <= df[c].max())]
    if out:
        st.warning("Input di luar rentang data latih untuk: " + ", ".join(NUM_LABEL[c] for c in out) +
                   ". Prediksi merupakan ekstrapolasi dan kurang andal.")

    c1, c2 = st.columns(2)
    with c1, card("top3"):
        st.markdown("### 🏆 Peringkat 3 Teratas")
        st.markdown(C.bars_html([(k, v) for k, v in ranked[:3]]), unsafe_allow_html=True)
    with c2, card("why"):
        st.markdown("### 🔍 Mengapa hasilnya begini?")
        nb = M.neighbors_of(ctx.bundle, x)
        cnt = nb[D.TARGET].value_counts()
        kk = len(nb)
        parts = ", ".join(f"**{n} dari {kk}** tetangga = {k}" for k, n in cnt.items())
        st.markdown(f"Dari {kk} data latih paling mirip (K = {kk}): {parts}.")
        view = nb[["jarak", "kabupaten", "musim", "jenis_tanah", "suhu", "curah_hujan", D.TARGET]].head(8).copy()
        view["jarak"] = view["jarak"].round(3)
        C.render_table(view, key="why_tbl")

    with card("fit"):
        st.markdown(f"### 🌱 Kecocokan lahan untuk **{top}**")
        st.caption("Dibandingkan dengan rentang P10-P90 data tanaman terpilih.")
        sub = df[df[D.TARGET] == top]
        rows = ['<div class="fit-row fit-head"><div>Parameter</div><div>Input</div><div>Status</div><div>Saran</div></div>']
        for c in D.NUM_COLS:
            lo, hi = np.percentile(sub[c], [10, 90])
            v = x[c]
            if v < lo:
                status, cls, tip = "Di bawah", "warn", SARAN_FITUR[c][0]
            elif v > hi:
                status, cls, tip = "Di atas", "warn", SARAN_FITUR[c][1]
            else:
                status, cls, tip = "Sesuai", "ok", "Berada pada rentang ideal data."
            rows.append(f'<div class="fit-row"><div><b>{NUM_LABEL[c]}</b><br><small>P10-P90: {lo:.1f}-{hi:.1f}</small></div>'
                        f'<div>{v:g}</div><div><span class="badge {cls}">{status}</span></div><div>{tip}</div></div>')
        st.markdown("".join(rows), unsafe_allow_html=True)

    with card("tips"):
        info = PLANTS[top]
        st.markdown(f"### 🧑‍🌾 Saran budidaya singkat: {emo} {top}")
        st.markdown(info["deskripsi"])
        st.markdown("\n".join(f"- {t}" for t in info["tips"]))
        st.caption(f"Musim tanam: {info['musim']}")
    st.markdown('<div class="disclaimer">⚠️ Hasil ini adalah <b>saran pendukung keputusan</b>, bukan keputusan '
                'akhir. Konfirmasikan dengan penyuluh pertanian setempat dan kondisi nyata lahan Anda. Data '
                'pelatihan bersifat simulasi.</div>', unsafe_allow_html=True)

    st.markdown("### 🕘 Riwayat Rekomendasi")
    hist = st.session_state.get("history", [])
    if hist:
        hdf = pd.DataFrame(hist)
        C.render_table(hdf, page_size=50, key="hist_tbl")
        b1, b2 = st.columns(2)
        b1.download_button("⬇️ Unduh riwayat (CSV)", hdf.to_csv(index=False).encode("utf-8"),
                           "riwayat_rekomendasi_tandur.csv", "text/csv", key="dl_hist", **C.stretch_kw())
        if b2.button("🗑️ Hapus riwayat", key="clear_hist", **C.stretch_kw()):
            st.session_state["history"] = []
            st.session_state["last_sig"] = None
            st.rerun()
    else:
        st.info("Belum ada riwayat. Ubah kondisi lahan di sidebar untuk membuat rekomendasi.")


# ============================================================= 2. VISUALISASI
def page_viz(ctx: SimpleNamespace) -> None:
    df, x, pal = ctx.df, ctx.x, ctx.pal
    with card("vizfilter"):
        st.markdown("### 🔎 Filter data")
        f1, f2, f3 = st.columns(3)
        kab = f1.multiselect("Kabupaten", D.CATEGORIES["kabupaten"], D.CATEGORIES["kabupaten"], key="f_kab")
        mus = f2.multiselect("Musim", D.CATEGORIES["musim"], D.CATEGORIES["musim"], key="f_mus")
        tnh = f3.multiselect("Jenis tanah", D.CATEGORIES["jenis_tanah"], D.CATEGORIES["jenis_tanah"], key="f_tnh")
    d = df[df.kabupaten.isin(kab) & df.musim.isin(mus) & df.jenis_tanah.isin(tnh)]
    if d.empty:
        st.warning("Tidak ada data yang cocok dengan filter. Pilih minimal satu nilai pada tiap filter.")
        return
    st.caption(f"{len(d)} dari {len(df)} baris ditampilkan.")
    cmap = PLANT_COLORS
    star = dict(color=pal["primary"], size=11, symbol="diamond", line=dict(color=pal["text"], width=2))

    with card("viz3d"):
        st.markdown("### 🧊 Scatter 3D")
        a1, a2, a3 = st.columns(3)
        ax = a1.selectbox("Sumbu X", D.NUM_COLS, 0, key="ax3x", format_func=NUM_LABEL.get)
        ay = a2.selectbox("Sumbu Y", D.NUM_COLS, 1, key="ax3y", format_func=NUM_LABEL.get)
        az = a3.selectbox("Sumbu Z", D.NUM_COLS, 2, key="ax3z", format_func=NUM_LABEL.get)
        lines = st.checkbox("Tampilkan garis ke K tetangga terdekat", True, key="show_lines")
        fig = go.Figure()
        for pl in D.CATEGORIES["tanaman"]:
            s = d[d.tanaman == pl]
            fig.add_trace(go.Scatter3d(x=s[ax], y=s[ay], z=s[az], mode="markers", name=pl,
                                       marker=dict(size=3, color=cmap[pl], opacity=.75)))
        fig.add_trace(go.Scatter3d(x=[x[ax]], y=[x[ay]], z=[x[az]], mode="markers+text", name="Input Anda",
                                   text=["Input Anda"], textfont=dict(color=pal["text"]), marker=star))
        if lines:
            nb = M.neighbors_of(ctx.bundle, x)
            lx, ly, lz = [], [], []
            for _, r in nb.iterrows():
                lx += [x[ax], r[ax], None]; ly += [x[ay], r[ay], None]; lz += [x[az], r[az], None]
            fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode="lines", name="Tetangga terdekat",
                                       line=dict(color=pal["primary"], width=3)))
        fig.update_layout(scene=dict(xaxis_title=NUM_LABEL[ax], yaxis_title=NUM_LABEL[ay], zaxis_title=NUM_LABEL[az]))
        C.style_fig(fig, pal, 440)
        C.plot(fig, "fig3d")

    with card("viz2d"):
        st.markdown("### 🎯 Scatter 2D")
        b1, b2 = st.columns(2)
        x2 = b1.selectbox("Sumbu X", D.NUM_COLS, 0, key="ax2x", format_func=NUM_LABEL.get)
        y2 = b2.selectbox("Sumbu Y", D.NUM_COLS, 2, key="ax2y", format_func=NUM_LABEL.get)
        fig = px.scatter(d, x=x2, y=y2, color="tanaman", color_discrete_map=cmap, opacity=.7,
                         labels=NUM_LABEL)
        fig.add_trace(go.Scatter(x=[x[x2]], y=[x[y2]], mode="markers", name="Input Anda", marker=star))
        C.style_fig(fig, pal, 380)
        C.plot(fig, "fig2d")

    with card("vizdist"):
        st.markdown("### 📦 Distribusi per fitur")
        feat = st.selectbox("Fitur", D.NUM_COLS, 0, key="dist_feat", format_func=NUM_LABEL.get)
        kind = st.radio("Jenis grafik", ["Histogram", "Box"], horizontal=True, key="dist_kind")
        if kind == "Histogram":
            fig = px.histogram(d, x=feat, color="tanaman", color_discrete_map=cmap, barmode="overlay",
                               opacity=.65, nbins=30, labels=NUM_LABEL)
        else:
            fig = px.box(d, x="tanaman", y=feat, color="tanaman", color_discrete_map=cmap, labels=NUM_LABEL)
        C.style_fig(fig, pal, 380)
        C.plot(fig, "figdist")

    c1, c2 = st.columns(2)
    with c1, card("viz_corr"):
        st.markdown("### 🔥 Korelasi fitur")
        corr = d[D.NUM_COLS].corr()
        fig = px.imshow(corr, text_auto=".2f", color_continuous_scale=[pal["bg_lo"], pal["secondary"], pal["primary"]],
                        zmin=-1, zmax=1, aspect="auto")
        fig.update_xaxes(tickvals=list(range(5)), ticktext=[c.replace("_", " ") for c in D.NUM_COLS])
        fig.update_yaxes(tickvals=list(range(5)), ticktext=[c.replace("_", " ") for c in D.NUM_COLS])
        C.style_fig(fig, pal, 360)
        C.plot(fig, "figcorr")
    with c2, card("viz_cls"):
        st.markdown("### 🍀 Distribusi kelas")
        vc = d.tanaman.value_counts().reset_index()
        vc.columns = ["tanaman", "jumlah"]
        fig = px.bar(vc, x="tanaman", y="jumlah", color="tanaman", color_discrete_map=cmap)
        fig.update_layout(showlegend=False)
        C.style_fig(fig, pal, 360)
        C.plot(fig, "figcls")

    c3, c4 = st.columns(2)
    for col, by, nm in ((c3, "kabupaten", "kab"), (c4, "musim", "mus")):
        with col, card(f"viz_by_{nm}"):
            st.markdown(f"### 📍 Tanaman per {by}")
            g = d.groupby([by, "tanaman"]).size().reset_index(name="jumlah")
            fig = px.bar(g, x=by, y="jumlah", color="tanaman", barmode="group", color_discrete_map=cmap)
            C.style_fig(fig, pal, 360)
            C.plot(fig, f"figby_{nm}")

    with card("viz_radar"):
        st.markdown("### 🕸️ Radar: input Anda vs rata-rata tanaman terpilih")
        top = ctx.top
        lo = {c: df[c].min() for c in D.NUM_COLS}
        hi = {c: df[c].max() for c in D.NUM_COLS}
        norm = lambda c, v: float(np.clip((v - lo[c]) / (hi[c] - lo[c] or 1), 0, 1))  # noqa: E731
        mean = df[df.tanaman == top][D.NUM_COLS].mean()
        cats = [NUM_LABEL[c] for c in D.NUM_COLS]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=[norm(c, x[c]) for c in D.NUM_COLS] + [norm(D.NUM_COLS[0], x[D.NUM_COLS[0]])],
                                      theta=cats + cats[:1], fill="toself", name="Input Anda",
                                      line=dict(color=pal["primary"])))
        fig.add_trace(go.Scatterpolar(r=[norm(c, mean[c]) for c in D.NUM_COLS] + [norm(D.NUM_COLS[0], mean[D.NUM_COLS[0]])],
                                      theta=cats + cats[:1], fill="toself", name=f"Rata-rata {top}",
                                      line=dict(color=_color(top)), opacity=.6))
        fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(range=[0, 1], gridcolor=pal["grid"],
                          tickfont=dict(color=pal["muted"])), angularaxis=dict(gridcolor=pal["grid"],
                          tickfont=dict(color=pal["text"]))))
        C.style_fig(fig, pal, 400)
        C.plot(fig, "figradar")


# ============================================================= 3. BEDAH MANUAL
def page_manual(ctx: SimpleNamespace) -> None:
    b, x = ctx.bundle, ctx.x
    k, metric, weights = b["k"], b["metric"], b["weights"]
    with st.spinner("Menghitung jarak ke seluruh data latih..."):
        r = M.manual_knn(b, x)
    st.caption(f"Model aktif: K = {k} | metrik = {metric} | weights = {weights} | data latih = {b['n_train']} baris.")

    with card("m1"):
        st.markdown("### Langkah 1 - Input mentah")
        C.render_table(pd.DataFrame([{D.LABELS[c]: x[c] for c in D.CAT_COLS + D.NUM_COLS}]), key="m1_tbl")
    with card("m2"):
        st.markdown("### Langkah 2 - Normalisasi & One-Hot")
        st.latex(r"z = \frac{x - \mu}{\sigma}")
        rows = []
        for i, c in enumerate(D.NUM_COLS):
            mu, sd, z = r["mean"][i], r["scale"][i], r["q"][r["cols"].index(c)]
            rows.append({"Fitur": c, "x": x[c], "μ": round(float(mu), 4), "σ": round(float(sd), 4),
                         "z = (x−μ)/σ": round(float(z), 4),
                         "Perhitungan": f"({x[c]:g} − {mu:.3f}) / {sd:.3f} = {z:.3f}"})
        C.render_table(pd.DataFrame(rows), key="m2_tbl")
        st.markdown("**One-hot kategorikal** (1 = kategori terpilih):")
        oh = {n: int(round(float(r["q"][i]))) for i, n in enumerate(r["cols"]) if n not in D.NUM_COLS}
        C.render_table(pd.DataFrame([oh]), key="m2_oh")
    with card("m3"):
        st.markdown(f"### Langkah 3 - Jarak ke seluruh {b['n_train']} data latih")
        if metric == "euclidean":
            st.latex(r"d(a,b)=\sqrt{\sum_{i}(a_i-b_i)^2}")
            st.caption("Kolom fitur = kontribusi selisih kuadrat (jumlah kolom one-hot per fitur asal).")
        else:
            st.latex(r"d(a,b)=\sum_{i}|a_i-b_i|")
            st.caption("Kolom fitur = kontribusi selisih absolut (jumlah kolom one-hot per fitur asal).")
        nb = r["neighbors"].copy()
        show = nb[["peringkat", "tanaman", "jarak"] + D.CAT_COLS + D.NUM_COLS].copy()
        for c in show.columns[2:]:
            show[c] = show[c].round(4)
        C.render_table(show, key="m3_tbl")
        first = nb.iloc[0]
        terms = " + ".join(f"{first[c]:.3f}" for c in D.CAT_COLS + D.NUM_COLS)
        if metric == "euclidean":
            st.markdown(f"Contoh tetangga #1: `d = √({terms}) = {first['jarak']:.4f}`")
        else:
            st.markdown(f"Contoh tetangga #1: `d = {terms} = {first['jarak']:.4f}`")
    with card("m4"):
        st.markdown("### Langkah 4 - Pemungutan suara")
        if weights == "distance":
            st.latex(r"w = \frac{1}{d}")
            st.caption("Setiap tetangga memberi suara sebesar 1/d (jarak 0 → bobot 1 dan hanya tetangga berjarak 0 yang dihitung).")
        else:
            st.caption("Setiap tetangga memberi 1 suara (uniform).")
        votes = pd.DataFrame({"Kelas": list(r["votes"]), "Total suara": [round(v, 4) for v in r["votes"].values()]})
        votes = votes.sort_values("Total suara", ascending=False)
        C.render_table(votes, key="m4_tbl")
    with card("m5"):
        st.markdown("### Langkah 5 - Hasil akhir & pembuktian")
        st.success(f"Hasil manual: **{r['winner']}** {PLANT_EMOJI.get(r['winner'], '')}")
        cmp = pd.DataFrame({"Peringkat": np.arange(1, k + 1), "Indeks manual": nb["indeks"].to_numpy(),
                            "Indeks sklearn": r["sk_idx"], "Jarak manual": nb["jarak"].round(6).to_numpy(),
                            "Jarak sklearn": np.round(r["sk_dist"], 6)})
        C.render_table(cmp, key="m5_tbl")
        if r["match_all"]:
            st.markdown(f'<div class="neo-inset">✅ <b>Cocok</b> - jarak, tetangga, dan hasil prediksi manual identik '
                        f'dengan <code>KNeighborsClassifier.kneighbors</code> (prediksi sklearn: {r["sk_pred"]}).</div>',
                        unsafe_allow_html=True)
        else:
            st.warning(f"Selisih terdeteksi (jarak cocok: {r['match_dist']}, indeks sama: {r['match_idx']}, "
                       f"prediksi sama: {r['match_pred']}). Perbedaan indeks dapat terjadi bila ada jarak seri.")


# ============================================================= 4. EVALUASI
def _model_info(b: Dict) -> None:
    m = b["metrics"]
    st.markdown(f'<div class="kv"><span>K = <b>{b["k"]}</b></span><span>metrik: <b>{b["metric"]}</b></span>'
                f'<span>weights: <b>{b["weights"]}</b></span><span>akurasi uji: <b>{m["accuracy"] * 100:.2f}%</b></span>'
                f'<span>dilatih: {html.escape(str(b["trained_at"]))}</span><span>sklearn {b["sklearn_version"]}</span></div>',
                unsafe_allow_html=True)


def page_eval(ctx: SimpleNamespace) -> None:
    df, b, pal = ctx.df, ctx.bundle, ctx.pal
    with card("e_info"):
        st.markdown("### 🧠 Model aktif")
        _model_info(b)
        e1, e2 = st.columns(2)
        if e1.button("🔁 Latih Ulang & Simpan Model (.joblib)", key="retrain", **C.stretch_kw()):
            with C.loading("pelatihan model"):
                with st.spinner("Melatih ulang model & mencari K terbaik..."):
                    M.train_and_save(df)
            _flash("Model dilatih ulang dan disimpan.")
            _refresh_after_data_change(True)
        mp = D.model_path()
        if mp.exists():
            e2.download_button("⬇️ Unduh model .joblib", mp.read_bytes(), mp.name,
                               "application/octet-stream", key="dl_model", **C.stretch_kw())
    with card("e_param"):
        st.markdown("### ⚙️ Parameter evaluasi")
        p1, p2, p3 = st.columns(3)
        ts = p1.slider("Rasio data uji (%)", 10, 40, 20, 5, key="ev_ts", help="Persentase data yang disisihkan untuk pengujian.")
        kmax = p2.slider("K maksimum", 1, 30, 25, key="ev_kmax", help="Mencari K dari 1 hingga nilai ini.")
        folds = p3.slider("Jumlah fold CV", 3, 10, 5, key="ev_folds", help="Cross-validation stratified.")
        q1, q2 = st.columns(2)
        metric = q1.selectbox("Metrik jarak (untuk kurva)", M.METRICS, key="ev_metric")
        weights = q2.selectbox("Weights (untuk kurva)", M.WEIGHTS, 1, key="ev_weights")
        if st.button("▶️ Jalankan Evaluasi", key="run_eval", type="primary"):
            with C.loading("evaluasi & grid search"):
                with st.spinner("Menjalankan grid search K × metrik × weights..."):
                    st.session_state["eval"] = M.evaluate(df, ts / 100, kmax, metric, weights, folds)
    res = st.session_state.get("eval")
    if not res:
        st.info("Atur parameter lalu tekan **Jalankan Evaluasi**.")
        return
    best, m = res["best"], res["metrics"]
    with card("e_res"):
        st.markdown("### 🏁 Hasil")
        a, b2, c, d, e = st.columns(5)
        a.metric("K terbaik", best["k"]); b2.metric("Akurasi uji", f"{m['accuracy'] * 100:.2f}%")
        c.metric("Precision (macro)", f"{m['precision'] * 100:.2f}%"); d.metric("Recall (macro)", f"{m['recall'] * 100:.2f}%")
        e.metric("F1 (macro)", f"{m['f1'] * 100:.2f}%")
        st.caption(f"Kombinasi terbaik: K={best['k']}, metrik={best['metric']}, weights={best['weights']} "
                   f"(akurasi CV {best['cv'] * 100:.2f}%).")
        cur = res["curve"]
        fig = go.Figure()
        for col, nm, colr in (("latih", "Akurasi latih", pal["muted"]), ("uji", "Akurasi uji", pal["secondary"]),
                              ("cv", "Akurasi CV", pal["primary"])):
            fig.add_trace(go.Scatter(x=cur["K"], y=cur[col], mode="lines+markers", name=nm, line=dict(color=colr)))
        fig.update_layout(xaxis_title="K", yaxis_title="Akurasi", title=f"K vs akurasi ({res['params']['metric']}, {res['params']['weights']})")
        C.style_fig(fig, pal, 380)
        C.plot(fig, "fig_kcurve")
    with card("e_cm"):
        st.markdown("### 🧾 Classification report & confusion matrix")
        rep = res["report"].copy()
        for col in rep.columns[1:]:
            rep[col] = rep[col].round(3)
        C.render_table(rep, key="rep_tbl")
        fig = px.imshow(res["cm"], x=res["classes"], y=res["classes"], text_auto=True, aspect="auto",
                        color_continuous_scale=[pal["bg_lo"], pal["secondary"], pal["primary"]],
                        labels=dict(x="Prediksi", y="Aktual", color="Jumlah"))
        C.style_fig(fig, pal, 400)
        C.plot(fig, "fig_cm")
    with card("e_grid"):
        st.markdown("### 🔬 Tabel grid search (berperingkat)")
        g = res["grid"].head(60).copy()
        g["akurasi_cv"] = (g["akurasi_cv"] * 100).round(2)
        g["std"] = (g["std"] * 100).round(2)
        C.render_table(g.rename(columns={"akurasi_cv": "akurasi CV (%)", "std": "std (%)"}), key="grid_tbl")
        if st.button("✅ Terapkan K terbaik & simpan model", key="apply_best", type="primary"):
            with C.loading("penyimpanan model"):
                M.train_and_save(df, best["k"], best["metric"], best["weights"], res["params"]["test_size"])
            _flash(f"Model diperbarui: K={best['k']}, {best['metric']}, {best['weights']}.")
            _refresh_after_data_change(True)


# ============================================================= 5. DATASET
def page_dataset(ctx: SimpleNamespace) -> None:
    df = ctx.df
    with card("d_sum"):
        st.markdown("### 📋 Ringkasan dataset")
        a, b, c, d = st.columns(4)
        a.metric("Baris", len(df)); b.metric("Kolom", df.shape[1])
        c.metric("Nilai kosong", int(df.isna().sum().sum())); d.metric("Duplikat", int(df.duplicated().sum()))
        rng = pd.DataFrame({"fitur": D.NUM_COLS, "min": [df[c].min() for c in D.NUM_COLS],
                            "maks": [df[c].max() for c in D.NUM_COLS], "rata-rata": [round(df[c].mean(), 2) for c in D.NUM_COLS]})
        C.render_table(rng, key="rng_tbl")
        vc = df.tanaman.value_counts().rename_axis("tanaman").reset_index(name="jumlah")
        C.render_table(vc, key="vc_tbl")
        st.markdown('<div class="disclaimer">ℹ️ <b>Catatan kejujuran:</b> data bersifat <b>simulasi (sintetis)</b>, '
                    'bukan hasil pengukuran lapangan.</div>', unsafe_allow_html=True)
    with card("d_tab"):
        st.markdown("### 🗂️ Tabel data")
        s1, s2 = st.columns([2, 1])
        q = s1.text_input("Cari (semua kolom)", key="ds_q", placeholder="mis. sumenep, tembakau, kapur")
        sort_col = s2.selectbox("Urutkan", D.ALL_COLS, 0, key="ds_sort")
        asc = st.radio("Arah urutan", ["Naik", "Turun"], horizontal=True, key="ds_asc") == "Naik"
        f1, f2, f3, f4 = st.columns(4)
        fk = f1.multiselect("Kabupaten", D.CATEGORIES["kabupaten"], key="ds_fk")
        fm = f2.multiselect("Musim", D.CATEGORIES["musim"], key="ds_fm")
        ft = f3.multiselect("Jenis tanah", D.CATEGORIES["jenis_tanah"], key="ds_ft")
        fp = f4.multiselect("Tanaman", D.CATEGORIES["tanaman"], key="ds_fp")
        v = df
        if fk: v = v[v.kabupaten.isin(fk)]
        if fm: v = v[v.musim.isin(fm)]
        if ft: v = v[v.jenis_tanah.isin(ft)]
        if fp: v = v[v.tanaman.isin(fp)]
        if q.strip():
            mask = v.astype(str).apply(lambda col: col.str.contains(q.strip(), case=False, regex=False)).any(axis=1)
            v = v[mask]
        v = v.sort_values(sort_col, ascending=asc)
        C.render_table(v, 50, key="ds_tbl")
    with card("d_add"):
        st.markdown("### ➕ Tambah satu data baru")
        with st.form("form_add", clear_on_submit=False):
            f1, f2, f3 = st.columns(3)
            row = {"kabupaten": f1.selectbox("Kabupaten", D.CATEGORIES["kabupaten"], key="add_kab"),
                   "musim": f2.selectbox("Musim", D.CATEGORIES["musim"], key="add_mus"),
                   "jenis_tanah": f3.selectbox("Jenis tanah", D.CATEGORIES["jenis_tanah"], key="add_tnh")}
            g1, g2, g3, g4, g5 = st.columns(5)
            row["suhu"] = g1.number_input("Suhu (°C)", value=28.0, step=0.1, key="add_suhu", help="Rentang 20-36 °C.")
            row["kelembapan"] = g2.number_input("Kelembapan (%)", value=70.0, step=1.0, key="add_kel", help="Rentang 45-95 %.")
            row["curah_hujan"] = g3.number_input("Curah hujan (mm)", value=100.0, step=1.0, key="add_ch", help="Rentang 10-350 mm/bulan.")
            row["ph_tanah"] = g4.number_input("pH tanah", value=6.0, step=0.1, key="add_ph", help="Rentang 4.5-8.0.")
            row["ketinggian"] = g5.number_input("Ketinggian (mdpl)", value=50.0, step=1.0, key="add_tg", help="Rentang 1-350 mdpl.")
            row["tanaman"] = st.selectbox("Tanaman (label)", D.CATEGORIES["tanaman"], key="add_tan")
            retr = st.checkbox("Latih ulang model setelah menyimpan", True, key="add_retrain")
            ok = st.form_submit_button("💾 Simpan data baru")
        if ok:
            errs = D.validate_row(row)
            if errs:
                st.error("Data ditolak:\n\n" + "\n".join(f"- {e}" for e in errs))
            else:
                try:
                    with C.loading("penyimpanan data"):
                        new = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                        if new.duplicated().any():
                            raise ValueError("Baris yang sama sudah ada di dataset (duplikat).")
                        D.save_dataframe(new)
                        if retr:
                            M.train_and_save(D.load_dataframe())
                    _flash("Data baru disimpan." + (" Model dilatih ulang." if retr else ""))
                    _refresh_after_data_change(retr)
                except Exception as exc:  # pesan ramah
                    st.error(f"Gagal menyimpan data: {exc}")
    with card("d_up"):
        st.markdown("### ⬆️ Unggah data pengganti (xlsx/csv)")
        st.caption("Skema harus persis: " + ", ".join(D.ALL_COLS) + ". Data lama tidak ditimpa bila tidak valid.")
        up = st.file_uploader("Pilih file", ["xlsx", "csv"], key="ds_upload")
        if up is not None:
            try:
                with C.loading("validasi data unggahan"):
                    new = D.read_uploaded(up.getvalue(), up.name)
                    errs = D.validate_schema(new)
            except Exception as exc:
                new, errs = None, [f"File tidak dapat dibaca: {exc}"]
            if errs:
                st.error("Unggahan ditolak. Data lama tetap aman.\n\n" + "\n".join(f"- {e}" for e in errs))
            else:
                st.success(f"File valid: {len(new)} baris.")
                if st.button("✅ Terapkan data unggahan & latih ulang model", key="apply_upload", type="primary"):
                    with C.loading("penyimpanan data"):
                        D.save_dataframe(new)
                        M.train_and_save(D.load_dataframe())
                    _flash("Data unggahan diterapkan dan model dilatih ulang.")
                    _refresh_after_data_change(True)
    with card("d_dl"):
        st.markdown("### ⬇️ Unduh & pulihkan")
        u1, u2, u3 = st.columns(3)
        u1.download_button("Unduh data (xlsx)", D.to_xlsx_bytes(df), D.DATA_NAME, key="dl_xlsx", **C.stretch_kw())
        u2.download_button("Unduh data (csv)", df.to_csv(index=False).encode("utf-8"), "data_tanaman_madura.csv",
                           "text/csv", key="dl_csv", **C.stretch_kw())
        if D.has_backup():
            if u3.button("↩️ Kembalikan data asli", key="restore", **C.stretch_kw()):
                with C.loading("pemulihan data"):
                    D.restore_backup()
                    M.train_and_save(D.load_dataframe())
                _flash("Data asli dikembalikan dan model dilatih ulang.")
                _refresh_after_data_change(True)
        else:
            u3.caption("Cadangan data asli dibuat otomatis saat data pertama kali diubah.")
        st.info("☁️ Di Streamlit Community Cloud, perubahan file lewat aplikasi **tidak permanen** setelah app "
                "reboot. Untuk perubahan permanen, ubah file xlsx lalu `git push` ke GitHub.")


# ============================================================= 6. PROFIL TANAMAN
def page_profile(ctx: SimpleNamespace) -> None:
    df, pal = ctx.df, ctx.pal
    with card("p_pick"):
        plant = st.selectbox("Pilih tanaman", D.CATEGORIES["tanaman"], index=D.CATEGORIES["tanaman"].index(ctx.top)
                             if ctx.top in D.CATEGORIES["tanaman"] else 0, key="prof_plant",
                             format_func=lambda p: f"{PLANT_EMOJI[p]} {p}")
    info, sub = PLANTS[plant], df[df.tanaman == plant]
    with card("p_card"):
        st.markdown(f'<div class="plant-card"><div class="result-emoji">{PLANT_EMOJI[plant]}</div><div>'
                    f'<div class="result-name" style="color:{_color(plant)}">{plant}</div>'
                    f'<div>{info["deskripsi"]}</div></div></div>', unsafe_allow_html=True)
        st.markdown(f"**Potensi di Madura:** {info['potensi']}")
        st.markdown(f"**Catatan musim tanam:** {info['musim']}")
        st.markdown("**Tips budidaya:**\n" + "\n".join(f"- {t}" for t in info["tips"]))
        st.caption("Informasi umum dan bersifat sebagai pedoman awal; sesuaikan dengan kondisi lahan setempat.")
    with card("p_req"):
        st.markdown("### 🌡️ Syarat tumbuh ideal (berdasarkan data)")
        rows = []
        for c in D.NUM_COLS:
            p10, p90 = np.percentile(sub[c], [10, 90])
            rows.append({"Parameter": NUM_LABEL[c], "Rata-rata": round(sub[c].mean(), 2),
                         "P10": round(p10, 2), "P90": round(p90, 2)})
        C.render_table(pd.DataFrame(rows), key="req_tbl")
    c1, c2, c3 = st.columns(3)
    for col, by, nm in ((c1, "kabupaten", "k"), (c2, "musim", "m"), (c3, "jenis_tanah", "t")):
        with col, card(f"p_by_{nm}"):
            st.markdown(f"##### Per {by.replace('_', ' ')}")
            vc = sub[by].value_counts().rename_axis(by).reset_index(name="jumlah")
            fig = px.bar(vc, x=by, y="jumlah", color_discrete_sequence=[_color(plant)])
            C.style_fig(fig, pal, 300)
            C.plot(fig, f"fig_prof_{nm}")
    with card("p_map"):
        st.markdown("### 🗺️ Peta sebaran data")
        cnt = sub.kabupaten.value_counts()
        mp = pd.DataFrame([{"kabupaten": k, "lat": v[0], "lon": v[1], "jumlah": int(cnt.get(k, 0))}
                           for k, v in KOORDINAT.items()])
        kw = dict(lat="lat", lon="lon", size="jumlah", hover_name="kabupaten", size_max=45, zoom=7.4,
                  center=dict(lat=-7.1, lon=113.3), color_discrete_sequence=[_color(plant)])
        try:
            fig = px.scatter_map(mp, map_style="carto-positron", **kw)
        except Exception:
            fig = px.scatter_mapbox(mp, mapbox_style="carto-positron", **kw)
        C.style_fig(fig, pal, 400)
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        C.plot(fig, "fig_map")
        st.caption("Ukuran bubble = jumlah data tanaman terpilih di tiap kabupaten (peta dasar memerlukan internet).")
    with card("p_cmp"):
        st.markdown("### ⚖️ Perbandingan semua tanaman (rata-rata fitur)")
        avg = df.groupby("tanaman")[D.NUM_COLS].mean().round(2).reset_index()
        C.render_table(avg, key="avg_tbl")
        r1, r2 = st.columns(2)
        pa = r1.selectbox("Tanaman A", D.CATEGORIES["tanaman"], 0, key="cmp_a")
        pb = r2.selectbox("Tanaman B", D.CATEGORIES["tanaman"], 1, key="cmp_b")
        lo, hi = df[D.NUM_COLS].min(), df[D.NUM_COLS].max()
        fig = go.Figure()
        cats = [NUM_LABEL[c] for c in D.NUM_COLS]
        for p in (pa, pb):
            m = df[df.tanaman == p][D.NUM_COLS].mean()
            vals = [float((m[c] - lo[c]) / (hi[c] - lo[c])) for c in D.NUM_COLS]
            fig.add_trace(go.Scatterpolar(r=vals + vals[:1], theta=cats + cats[:1], fill="toself", name=p,
                                          line=dict(color=_color(p)), opacity=.65))
        fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(range=[0, 1], gridcolor=pal["grid"],
                          tickfont=dict(color=pal["muted"])), angularaxis=dict(gridcolor=pal["grid"],
                          tickfont=dict(color=pal["text"]))))
        C.style_fig(fig, pal, 400)
        C.plot(fig, "fig_cmp_radar")
    with card("p_fact"):
        st.markdown("### 📜 Fakta khas Madura")
        st.markdown("\n".join(f"- {f}" for f in FAKTA_MADURA))


# ============================================================= 7. TENTANG
def page_about(ctx: SimpleNamespace) -> None:
    b = ctx.bundle
    with card("a_prof"):
        st.markdown("### 👤 Profil pembuat")
        st.markdown(f"**{C.AUTHOR}** - NIM **{C.NIM}**  \n{C.PRODI}, {C.FAKULTAS}, {C.UNIV} 2026")
        st.markdown("**TANDUR** = *Teknologi Analisis dan Rekomendasi untuk Dunia Usaha Pertanian Madura* "
                    "(kata \"tandur\" berarti menanam). Judul: **Smart Crop Recommendation System for Madura Island** - "
                    "Sistem Pendukung Keputusan Rekomendasi Tanaman Berbasis K-Nearest Neighbors (KNN).")
    with card("a_goal"):
        st.markdown("### 🎯 Tujuan sistem")
        st.markdown("Membantu menentukan tanaman yang paling sesuai (jagung, tembakau, kacang tanah, cabai rawit, "
                    "singkong, padi gogo) berdasarkan kabupaten, musim, jenis tanah, suhu, kelembapan, curah hujan, "
                    "pH tanah, dan ketinggian lahan di Pulau Madura.")
    with card("a_knn"):
        st.markdown("### 🧭 Alur kerja KNN")
        st.markdown("1. Data dibersihkan dan dibagi 80% latih / 20% uji (stratified).\n"
                    "2. Fitur numerik dinormalisasi (z-score), fitur kategorikal di-one-hot.\n"
                    "3. Untuk input baru, dihitung jarak ke seluruh data latih.\n"
                    "4. K tetangga terdekat dipilih dan memberi suara (uniform atau berbobot 1/d).\n"
                    "5. Kelas dengan suara terbanyak menjadi rekomendasi; proporsi suara = tingkat keyakinan.")
        st.latex(r"d_{euclid}(a,b)=\sqrt{\sum_i (a_i-b_i)^2}\qquad d_{manhattan}(a,b)=\sum_i |a_i-b_i|")
        st.latex(r"z=\frac{x-\mu}{\sigma}")
        st.markdown("**Normalisasi** mencegah fitur berskala besar (mis. curah hujan) mendominasi jarak. "
                    "**One-hot** mengubah kategori menjadi kolom 0/1 sehingga bisa dihitung jaraknya.")
    with card("a_read"):
        st.markdown("### 📖 Cara membaca hasil")
        st.markdown("- **Keyakinan ≥ 75%**: tetangga sangat sepakat. **50-75%**: cukup. **< 50%**: ragu-ragu, gunakan hati-hati.\n"
                    "- **Kecocokan lahan** membandingkan input dengan rentang P10-P90 tanaman terpilih.\n"
                    "- Tab **Bedah Perhitungan Manual** membuktikan hasil dengan perhitungan numpy.")
        st.markdown("### ⚠️ Keterbatasan")
        st.markdown("- Data bersifat **simulasi (sintetis)**, bukan pengukuran lapangan.\n"
                    "- Hanya menilai **kecocokan agronomi**; belum memuat harga pasar atau ketersediaan air irigasi.\n"
                    "- Hasil adalah saran pendukung keputusan, bukan keputusan akhir.")
    with card("a_guide"):
        st.markdown("### 🧑‍🏫 Panduan penggunaan")
        st.markdown("1. Buka sidebar **Panel Kondisi Lahan** (di ponsel: ikon panah di kiri atas).\n"
                    "2. Pilih skenario cepat atau atur kabupaten, musim, tanah, dan slider.\n"
                    "3. Lihat rekomendasi di **Dashboard**; jelajahi grafik di halaman lain.\n"
                    "4. Ubah **Tampilan** (siang/malam & 25 tema) kapan saja.\n"
                    "5. Kelola data di **Manajemen Dataset** dan optimalkan K di **Evaluasi & Optimasi K**.")
    with card("a_gloss"):
        with st.expander("📚 Glosarium"):
            st.markdown("- **KNN**: algoritma klasifikasi berdasarkan K data terdekat.\n- **K**: jumlah tetangga.\n"
                        "- **Normalisasi (z-score)**: menyamakan skala fitur.\n- **One-hot**: representasi kategori 0/1.\n"
                        "- **Cross-validation**: pengujian berulang pada lipatan data.\n- **P10-P90**: rentang tengah 80% data.\n"
                        "- **mdpl**: meter di atas permukaan laut.")
        with st.expander("❓ FAQ"):
            st.markdown("**Apakah hasil ini pasti benar?** Tidak; ini saran pendukung keputusan berbasis data simulasi.\n\n"
                        "**Mengapa hasil berubah saat saya ganti kabupaten?** Kabupaten ikut dihitung dalam jarak (one-hot).\n\n"
                        "**Bagaimana menambah data?** Lewat halaman Manajemen Dataset.")
    with card("a_ver"):
        st.markdown("### 🧩 Versi aplikasi & library")
        C.render_table(pd.DataFrame([
            {"Komponen": "TANDUR", "Versi": "1.0.0"}, {"Komponen": "Python", "Versi": sys.version.split()[0]},
            {"Komponen": "Streamlit", "Versi": st.__version__}, {"Komponen": "scikit-learn", "Versi": sklearn.__version__},
            {"Komponen": "pandas", "Versi": pd.__version__}, {"Komponen": "numpy", "Versi": np.__version__},
            {"Komponen": "Model dilatih dengan sklearn", "Versi": b["sklearn_version"]}]), key="ver_tbl")
        st.caption("Data bersifat simulasi (sintetis).")


PAGE_FUNCS = {PAGES[0]: page_dashboard, PAGES[1]: page_viz, PAGES[2]: page_manual, PAGES[3]: page_eval,
              PAGES[4]: page_dataset, PAGES[5]: page_profile, PAGES[6]: page_about}
