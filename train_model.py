"""Melatih KNN TANDUR dan menyimpan models/knn_crop_madura.joblib.

Jalankan mandiri:  python train_model.py
Juga diimpor oleh app.py (fungsi train_and_save).
"""
from __future__ import annotations

import sys
import time

from core import data as D
from core.model import train_and_save, load_bundle


def main() -> int:
    t0 = time.time()
    if not D.data_path().exists():
        print(f"[GAGAL] File data tidak ditemukan: {D.data_path()}")
        return 1
    df = D.load_dataframe()
    errs = D.validate_schema(df)
    if errs:
        print("[GAGAL] Validasi data:", *errs, sep="\n  - ")
        return 1
    b = train_and_save(df)
    m = b["metrics"]
    print("=" * 60)
    print("TANDUR - Pelatihan KNN selesai")
    print("=" * 60)
    print(f"Data           : {len(df)} baris | kelas: {', '.join(b['classes'])}")
    print(f"Latih / Uji    : {b['n_train']} / {b['n_test']}")
    print(f"Parameter      : K={b['k']} | metrik={b['metric']} | weights={b['weights']}")
    print(f"Akurasi CV(5x) : {m.get('cv_accuracy', float('nan')):.4f}")
    print(f"Akurasi uji    : {m['accuracy']:.4f}")
    print(f"Precision macro: {m['precision']:.4f} | Recall macro: {m['recall']:.4f} | F1 macro: {m['f1']:.4f}")
    print(f"Disimpan di    : {D.model_path()}")
    print(f"Waktu          : {time.time() - t0:.1f} dtk")
    loaded = load_bundle()
    print("Verifikasi muat ulang: OK, K =", loaded["k"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
