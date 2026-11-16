"""Akses & validasi dataset TANDUR (xlsx). Semua path relatif terhadap root proyek."""
from __future__ import annotations

import os
import shutil
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_NAME = "data_rekomendasi_tanaman_madura.xlsx"
SHEET = "data tanaman"
SHEET_KET = "Keterangan"

CAT_COLS = ["kabupaten", "musim", "jenis_tanah"]
NUM_COLS = ["suhu", "kelembapan", "curah_hujan", "ph_tanah", "ketinggian"]
TARGET = "tanaman"
ALL_COLS = CAT_COLS + NUM_COLS + [TARGET]

CATEGORIES: Dict[str, List[str]] = {
    "kabupaten": ["Bangkalan", "Sampang", "Pamekasan", "Sumenep"],
    "musim": ["Hujan", "Kemarau"],
    "jenis_tanah": ["kapur", "aluvial", "regosol", "grumusol"],
    "tanaman": ["jagung", "tembakau", "kacang tanah", "cabai rawit", "singkong", "padi gogo"],
}
RANGES: Dict[str, tuple] = {
    "suhu": (20.0, 36.0), "kelembapan": (45.0, 95.0), "curah_hujan": (10.0, 350.0),
    "ph_tanah": (4.5, 8.0), "ketinggian": (1.0, 350.0),
}
LABELS = {
    "kabupaten": "Kabupaten", "musim": "Musim", "jenis_tanah": "Jenis tanah",
    "suhu": "Suhu (°C)", "kelembapan": "Kelembapan (%)", "curah_hujan": "Curah hujan (mm/bln)",
    "ph_tanah": "pH tanah", "ketinggian": "Ketinggian (mdpl)", "tanaman": "Tanaman",
}


def data_path() -> Path:
    """Lokasi file data (dapat dialihkan dengan env TANDUR_DATA_FILE untuk pengujian)."""
    env = os.environ.get("TANDUR_DATA_FILE")
    return Path(env) if env else ROOT / DATA_NAME


def backup_path() -> Path:
    p = data_path()
    return p.parent / "data_backup" / (p.stem + ".asli.xlsx")


def model_path() -> Path:
    env = os.environ.get("TANDUR_MODEL_FILE")
    return Path(env) if env else ROOT / "models" / "knn_crop_madura.joblib"


def validate_schema(df: pd.DataFrame) -> List[str]:
    """Validasi ketat skema; kembalikan daftar kesalahan (kosong = valid)."""
    errors: List[str] = []
    missing = [c for c in ALL_COLS if c not in df.columns]
    if missing:
        return [f"Kolom wajib tidak ada: {', '.join(missing)}."]
    d = df[ALL_COLS]
    if len(d) == 0:
        return ["Data kosong (0 baris)."]
    nulls = d.isna().sum()
    for c in ALL_COLS:
        if nulls[c]:
            errors.append(f"Kolom '{c}' memiliki {int(nulls[c])} nilai kosong.")
    if errors:
        return errors
    for c in NUM_COLS:
        conv = pd.to_numeric(d[c], errors="coerce")
        bad = int(conv.isna().sum())
        if bad:
            errors.append(f"Kolom '{c}' memiliki {bad} nilai non-numerik.")
            continue
        lo, hi = RANGES[c]
        out = int(((conv < lo) | (conv > hi)).sum())
        if out:
            errors.append(f"Kolom '{c}': {out} nilai di luar rentang {lo:g}-{hi:g}.")
    for c in CAT_COLS + [TARGET]:
        allowed = CATEGORIES[c]
        bad_vals = sorted(set(map(str, d[c].unique())) - set(allowed))
        if bad_vals:
            errors.append(f"Kolom '{c}': kategori tidak dikenal {bad_vals}. Diizinkan: {allowed}.")
    return errors


def clean(df: pd.DataFrame) -> pd.DataFrame:
    d = df[ALL_COLS].copy().dropna().drop_duplicates().reset_index(drop=True)
    for c in NUM_COLS:
        d[c] = pd.to_numeric(d[c])
    return d


def validate_row(row: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for c in CAT_COLS + [TARGET]:
        if row.get(c) not in CATEGORIES[c]:
            errors.append(f"{LABELS[c]} tidak valid: {row.get(c)!r}.")
    for c in NUM_COLS:
        try:
            v = float(row.get(c))
        except (TypeError, ValueError):
            errors.append(f"{LABELS[c]} harus berupa angka.")
            continue
        lo, hi = RANGES[c]
        if not lo <= v <= hi:
            errors.append(f"{LABELS[c]} harus di rentang {lo:g}-{hi:g} (diterima {v:g}).")
    return errors


def read_uploaded(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Baca xlsx/csv unggahan menjadi DataFrame (sheet pertama untuk xlsx)."""
    if filename.lower().endswith(".csv"):
        return pd.read_csv(BytesIO(file_bytes))
    names = pd.ExcelFile(BytesIO(file_bytes)).sheet_names
    return pd.read_excel(BytesIO(file_bytes), sheet_name=SHEET if SHEET in names else names[0])


def load_dataframe(path: Path | None = None) -> pd.DataFrame:
    p = path or data_path()
    names = pd.ExcelFile(p).sheet_names
    return clean(pd.read_excel(p, sheet_name=SHEET if SHEET in names else names[0]))


def _ensure_backup() -> None:
    b = backup_path()
    if not b.exists() and data_path().exists():
        b.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(data_path(), b)


def has_backup() -> bool:
    return backup_path().exists()


def restore_backup() -> bool:
    if not has_backup():
        return False
    shutil.copy2(backup_path(), data_path())
    return True


def save_dataframe(df: pd.DataFrame) -> None:
    """Tulis ulang sheet 'data tanaman' tanpa merusak sheet 'Keterangan'."""
    from openpyxl import Workbook, load_workbook

    p = data_path()
    _ensure_backup()
    df = clean(df)
    if p.exists():
        wb = load_workbook(p)
        if SHEET in wb.sheetnames:
            idx = wb.sheetnames.index(SHEET)
            del wb[SHEET]
            ws = wb.create_sheet(SHEET, idx)
        else:
            ws = wb.create_sheet(SHEET, 0)
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = SHEET
    ws.append(ALL_COLS)
    for rec in df.itertuples(index=False):
        ws.append([x.item() if hasattr(x, "item") else x for x in rec])
    p.parent.mkdir(parents=True, exist_ok=True)
    wb.save(p)


def to_xlsx_bytes(df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, sheet_name=SHEET, index=False)
    return buf.getvalue()
