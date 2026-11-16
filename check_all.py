"""Pemeriksaan otomatis TANDUR (cetak tabel PASS/FAIL).

Jalankan:  python check_all.py
Pengujian aplikasi memakai SALINAN data & model di folder sementara (.check_tmp/),
sehingga file asli tidak berubah.
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
os.environ["TANDUR_LOAD_SECONDS"] = "0"   # loading tanpa jeda agar tes cepat

import joblib  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from core import data as D  # noqa: E402
from core import model as M  # noqa: E402
from core import themes as T  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail else ""), flush=True)


def guarded(fn):
    def wrap(*a, **k):
        try:
            return fn(*a, **k)
        except Exception as exc:  # noqa: BLE001
            record(fn.__name__, False, f"exception: {exc!r}")
            traceback.print_exc()
    return wrap


# ------------------------------------------------------------------ 1. data
@guarded
def check_data() -> None:
    print("1) Data")
    df = pd.read_excel(ROOT / D.DATA_NAME, sheet_name="data tanaman")
    record("file data ada", (ROOT / D.DATA_NAME).exists())
    record("kolom lengkap & berurutan", list(df.columns) == D.ALL_COLS, str(list(df.columns)))
    record("tanpa nilai kosong", int(df.isna().sum().sum()) == 0)
    record("tanpa duplikat", int(df.duplicated().sum()) == 0)
    record("6 kelas target", df[D.TARGET].nunique() == 6, str(sorted(df[D.TARGET].unique())))
    record("validasi skema lolos", D.validate_schema(df) == [])
    xl = pd.ExcelFile(ROOT / D.DATA_NAME)
    record("sheet 'Keterangan' ada", "Keterangan" in xl.sheet_names)


# ---------------------------------------------------------------- 2. model
@guarded
def check_model() -> None:
    print("2) Model & joblib")
    p = ROOT / "models" / "knn_crop_madura.joblib"
    record("joblib terbentuk", p.exists())
    b = joblib.load(p)
    keys = {"pipeline", "k", "metric", "weights", "classes", "feature_names", "metrics", "n_train",
            "n_test", "trained_at", "sklearn_version", "data_file"}
    record("isi joblib lengkap", keys <= set(b), str(sorted(keys - set(b))))
    df = D.load_dataframe()
    _, Xte, _, yte = M.split(df, 0.2)
    acc = float((b["pipeline"].predict(Xte) == yte).mean())
    record("akurasi data uji >= 0.70", acc >= 0.70, f"{acc:.4f} (K={b['k']}, {b['metric']}, {b['weights']})")
    pred = b["pipeline"].predict(Xte.iloc[:1])[0]
    record("prediksi uji berjalan", pred in b["classes"], str(pred))
    # grid search efisien harus sama dengan cross_val_score scikit-learn
    from sklearn.model_selection import StratifiedKFold, cross_val_score
    Xtr, _, ytr, _ = M.split(df, 0.2)
    g = M.grid_search(Xtr, ytr, kmax=10, folds=5)
    for (k, m, w) in [(7, "euclidean", "uniform"), (9, "manhattan", "distance")]:
        ref = cross_val_score(M.build_pipeline(k, m, w), Xtr, ytr, scoring="accuracy",
                              cv=StratifiedKFold(5, shuffle=True, random_state=M.SEED)).mean()
        mine = float(g[(g.K == k) & (g.metrik == m) & (g.weights == w)].akurasi_cv.iloc[0])
        record(f"grid search = cross_val_score ({k},{m},{w})", abs(ref - mine) < 0.01, f"{mine:.4f} vs {ref:.4f}")


# ---------------------------------------------------------------- 3. tema
@guarded
def check_themes() -> None:
    print("3) Tema & kontras")
    record("25 tema", len(T.THEMES) == 25 and len(set(T.THEME_NAMES)) == 25)
    hex_ok = all(T.is_hex(v) for t in T.THEMES.values() for v in t.values())
    record("semua warna hex valid", hex_ok)
    bad = []
    for name in T.THEME_NAMES:
        for mode in ("siang", "malam"):
            for k, v in T.contrast_report(name, mode).items():
                if v < 4.5:
                    bad.append((name, mode, k, round(v, 2)))
    record("kontras >= 4.5:1 (25 tema x siang/malam)", not bad, str(bad[:3]))
    p = T.palette("Sakera Madura", "siang")
    record("tema default Sakera Madura", T.DEFAULT_THEME == "Sakera Madura" and p["night"] == "0")


# ---------------------------------------------------------------- 4-7. app
def _txt(at) -> str:
    return " ".join(m.value for m in at.markdown)


def _no_exc(at, label: str) -> bool:
    ok = not at.exception and not at.error
    if not ok:
        msgs = [e.value for e in at.exception] + [e.value for e in at.error]
        record(label, False, str(msgs)[:200])
    return ok


@guarded
def check_app(tmp: Path) -> None:
    from streamlit.testing.v1 import AppTest
    from ui.pages import PAGES

    print("4) Aplikasi (AppTest)")
    at = AppTest.from_file("app.py", default_timeout=120).run()
    record("app berjalan tanpa exception", _no_exc(at, "app berjalan"))
    all_ok = True
    for pg in PAGES:
        at.radio(key="page").set_value(pg).run()
        if not _no_exc(at, f"halaman {pg}"):
            all_ok = False
        t = _txt(at)
        if "Fajar Setya Adhi - 20251233022" not in t:
            all_ok = False
            record(f"footer identitas di {pg}", False)
    record("7 halaman tanpa exception & footer identitas", all_ok)
    at.radio(key="page").set_value(PAGES[0]).run()
    record("hasil rekomendasi muncul", "result-card" in _txt(at))
    ok = True
    for i in range(5):
        at.button(key=f"sc_{i}").click().run()
        ok &= _no_exc(at, f"skenario {i}") and "result-card" in _txt(at)
    record("5 skenario cepat", ok)
    at.button(key="sc_0").click().run()
    exp = (at.selectbox(key="in_kab").value, at.slider(key="in_suhu").value, at.slider(key="in_ch").value)
    record("skenario menyetel nilai (Kapur Kering Sumenep)", exp == ("Sumenep", 29.0, 75), str(exp))
    at.button(key="sc_rand").click().run()
    record("tombol Acak", _no_exc(at, "acak") and "result-card" in _txt(at))
    at.button(key="sc_reset").click().run()
    record("tombol Reset", at.selectbox(key="in_kab").value == "Sumenep" and _no_exc(at, "reset"))
    at.slider(key="in_suhu").set_value(33.5).run()
    at.slider(key="in_kel").set_value(50).run()
    at.selectbox(key="in_kab").set_value("Bangkalan").run()
    at.selectbox(key="in_mus").set_value("Hujan").run()
    at.selectbox(key="in_tnh").set_value("grumusol").run()
    record("ubah slider & selectbox", _no_exc(at, "ubah input") and "result-card" in _txt(at))
    at.toggle(key="night").set_value(True).run()
    record("toggle malam (CSS malam aktif)", _no_exc(at, "malam")
           and T.palette("Sakera Madura", "malam")["bg"].lower() in _txt(at).lower())
    at.toggle(key="night").set_value(False).run()
    ok = True
    for name in ["Kerapan Sapi", "Laut Madura", "Midnight Indigo", "Rose Pastel", "Batik Tanean Lanjhang"]:
        at.selectbox(key="theme").set_value(name).run()
        ok &= _no_exc(at, f"tema {name}") and T.palette(name, "siang")["primary"].lower() in _txt(at).lower()
    record("ganti 5 tema (CSS ikut berubah)", ok)
    at.selectbox(key="theme").set_value("Sakera Madura").run()

    print("5) Bedah perhitungan manual")
    b, _ = M.load_or_train()
    ok = True
    rng = np.random.default_rng(1)
    df = D.load_dataframe()
    for _ in range(25):
        r = df.iloc[int(rng.integers(len(df)))]
        x = {c: r[c] for c in D.CAT_COLS + D.NUM_COLS}
        x = {k: (float(v) if k in D.NUM_COLS else v) for k, v in x.items()}
        res = M.manual_knn(b, x)
        ok &= res["match_dist"] and res["match_pred"]
    record("manual cocok kneighbors (jarak & prediksi, 25 sampel acak)", ok)
    for metric in M.METRICS:
        for w in M.WEIGHTS:
            bb = M.train_and_save(df, 9, metric, w, save=False)
            x = {"kabupaten": "Sampang", "musim": "Hujan", "jenis_tanah": "aluvial", "suhu": 26.5,
                 "kelembapan": 84.0, "curah_hujan": 210.0, "ph_tanah": 5.8, "ketinggian": 15.0}
            res = M.manual_knn(bb, x)
            record(f"manual cocok ({metric}, {w}) termasuk indeks", res["match_all"])
    at.radio(key="page").set_value(PAGES[2]).run()
    record("halaman manual menampilkan '✅ Cocok'", "Cocok" in _txt(at))

    print("6) Tambah / unggah data")
    D_ok = D.validate_schema(df) == []
    bad1 = df.drop(columns=["suhu"])
    bad2 = df.copy(); bad2.loc[0, "suhu"] = 99
    bad3 = df.copy(); bad3.loc[0, "kabupaten"] = "Surabaya"
    bad4 = df.copy(); bad4.loc[0, "ph_tanah"] = None
    record("unggahan valid diterima", D_ok)
    record("unggahan tidak valid ditolak (4 jenis)", all(D.validate_schema(x) for x in (bad1, bad2, bad3, bad4)),
           str(D.validate_schema(bad2)))
    at.radio(key="page").set_value(PAGES[4]).run()
    n0 = len(D.load_dataframe())
    submit = [b_ for b_ in at.button if "Simpan data baru" in b_.label]
    at.number_input(key="add_suhu").set_value(99.0)
    at.checkbox(key="add_retrain").uncheck()
    submit[0].click().run()
    rejected = any("ditolak" in e.value for e in at.error) and len(D.load_dataframe()) == n0
    record("form tambah data tidak valid ditolak dgn pesan jelas", rejected)
    at.number_input(key="add_suhu").set_value(27.3)
    at.number_input(key="add_ph").set_value(5.55)
    at.number_input(key="add_ch").set_value(101.0)
    submit = [b_ for b_ in at.button if "Simpan data baru" in b_.label]
    submit[0].click().run()
    n1 = len(D.load_dataframe())
    record("form tambah data valid diterima & tersimpan ke xlsx", n1 == n0 + 1 and _no_exc(at, "tambah valid"), f"{n0}->{n1}")
    xl = pd.ExcelFile(D.data_path())
    ket = pd.read_excel(D.data_path(), sheet_name="Keterangan") if "Keterangan" in xl.sheet_names else []
    record("sheet 'Keterangan' tetap utuh setelah simpan", len(ket) > 0)
    record("cadangan data asli dibuat", D.has_backup())
    at.radio(key="page").set_value(PAGES[4]).run()
    rs = [b_ for b_ in at.button if "Kembalikan data asli" in b_.label]
    if rs:
        rs[0].click().run()
    record("'Kembalikan data asli' memulihkan", len(D.load_dataframe()) == n0 and _no_exc(at, "restore"))

    print("7) Latih ulang dari aplikasi")
    mp = D.model_path()
    t_before = mp.stat().st_mtime_ns
    time.sleep(0.05)
    at.radio(key="page").set_value(PAGES[3]).run()
    at.button(key="retrain").click().run()
    record("latih ulang membuat joblib baru tanpa error", mp.stat().st_mtime_ns > t_before and _no_exc(at, "retrain"))
    at.button(key="run_eval").click().run()
    record("jalankan evaluasi (grid search) & hasil tampil", _no_exc(at, "evaluasi") and len(at.get("plotly_chart")) >= 2)
    t_before = mp.stat().st_mtime_ns
    ab = at.button(key="apply_best")
    ab.click().run()
    record("terapkan K terbaik & simpan model", mp.stat().st_mtime_ns > t_before and _no_exc(at, "apply best"))

    print("8) Ketahanan")
    bad_model = tmp / "rusak.joblib"
    bad_model.write_bytes(b"bukan joblib")
    os.environ["TANDUR_MODEL_FILE"] = str(bad_model)
    bundle, retrained = M.load_or_train()
    record("joblib rusak -> latih ulang otomatis tanpa crash", retrained and bundle["k"] >= 1)
    os.environ["TANDUR_MODEL_FILE"] = str(mp)
    os.environ["TANDUR_DATA_FILE"] = str(tmp / "tidak_ada.xlsx")
    at2 = AppTest.from_file("app.py", default_timeout=60).run()
    record("data hilang -> pesan ramah + uploader (tanpa crash)",
           not at2.exception and any("belum ditemukan" in w.value for w in at2.warning))
    os.environ["TANDUR_DATA_FILE"] = str(tmp / D.DATA_NAME)


@guarded
def check_static() -> None:
    print("9) Statis")
    src = (ROOT / "app.py").read_text() + (ROOT / "ui" / "pages.py").read_text() + (ROOT / "ui" / "components.py").read_text()
    record("tidak memakai st.tabs / st.dataframe / data_editor", not any(s in src for s in ("st.tabs(", "st.dataframe(", "st.data_editor(")))
    record("tidak ada fitur IoT", "iot" not in src.lower().replace("riot", ""))
    record("tidak ada path absolut di kode", "/home/" not in src and "C:\\" not in src and "/run/media" not in src)
    hits = [p.name for p in list(ROOT.glob("*.md")) + [ROOT / "app.py"] + list((ROOT / "ui").glob("*.py"))
            if "Smart Crop Madura" in p.read_text() and p.name != "LAPORAN_PEMERIKSAAN.md"]
    record("nama lama 'Smart Crop Madura' tidak muncul di UI/README/panduan", not hits, str(hits))
    css = (ROOT / "ui" / "styles.py").read_text()
    record("CSS responsif (breakpoint 1024/768/480)", all(f"max-width:{w}px" in css for w in (1024, 768, 480)))


def main() -> int:
    t0 = time.time()
    check_data()
    check_model()
    check_themes()
    tmp = ROOT / ".check_tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir()
    shutil.copy2(ROOT / D.DATA_NAME, tmp / D.DATA_NAME)
    (tmp / "models").mkdir()
    shutil.copy2(ROOT / "models" / "knn_crop_madura.joblib", tmp / "models" / "knn_crop_madura.joblib")
    os.environ["TANDUR_DATA_FILE"] = str(tmp / D.DATA_NAME)
    os.environ["TANDUR_MODEL_FILE"] = str(tmp / "models" / "knn_crop_madura.joblib")
    try:
        check_app(tmp)
    finally:
        os.environ.pop("TANDUR_DATA_FILE", None)
        os.environ.pop("TANDUR_MODEL_FILE", None)
    check_static()
    shutil.rmtree(tmp, ignore_errors=True)
    print("\n" + "=" * 78)
    print(f"{'PEMERIKSAAN':<64}{'HASIL':>8}")
    print("-" * 78)
    for n, ok, d in RESULTS:
        print(f"{n[:62]:<64}{'PASS' if ok else 'FAIL':>8}")
    npass = sum(ok for _, ok, _ in RESULTS)
    print("-" * 78)
    print(f"TOTAL: {npass}/{len(RESULTS)} PASS  ({time.time() - t0:.1f} dtk)")
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
