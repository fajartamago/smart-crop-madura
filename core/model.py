"""Model KNN TANDUR: pelatihan, grid search CV efisien, penyimpanan .joblib, hitung manual."""
from __future__ import annotations

from datetime import datetime
from itertools import product
from typing import Any, Dict, List, Sequence

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             precision_recall_fscore_support)
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.neighbors import KNeighborsClassifier, NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from . import data as D

METRICS = ["euclidean", "manhattan"]
WEIGHTS = ["uniform", "distance"]
SEED = 42


def build_pipeline(k: int = 5, metric: str = "euclidean", weights: str = "uniform") -> Pipeline:
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), D.CAT_COLS),
        ("num", StandardScaler(), D.NUM_COLS),
    ])
    knn = KNeighborsClassifier(n_neighbors=k, metric=metric, weights=weights)
    return Pipeline([("pre", pre), ("knn", knn)])


def split(df: pd.DataFrame, test_size: float = 0.2):
    return train_test_split(df[D.CAT_COLS + D.NUM_COLS], df[D.TARGET], test_size=test_size,
                            stratify=df[D.TARGET], random_state=SEED)


# ---------------------------------------------------------------- grid search
def _votes_accuracy(dist: np.ndarray, idx: np.ndarray, ytr: np.ndarray, yev: np.ndarray,
                    n_classes: int, kmax: int) -> Dict[str, np.ndarray]:
    """Akurasi untuk k=1..kmax (uniform & distance) memakai tetangga terurut."""
    onehot = np.eye(n_classes)[ytr[idx[:, :kmax]]]            # (n, kmax, C)
    uni = np.cumsum(onehot, axis=1)
    zero = dist[:, :kmax] == 0
    inv = np.where(zero, 0.0, 1.0 / np.where(zero, 1.0, dist[:, :kmax]))
    dist_votes = np.cumsum(onehot * inv[..., None], axis=1)
    zero_votes = np.cumsum(onehot * zero[..., None], axis=1)
    has_zero = np.cumsum(zero, axis=1) > 0
    dist_votes = np.where(has_zero[..., None], zero_votes, dist_votes)
    out = {}
    for name, v in (("uniform", uni), ("distance", dist_votes)):
        pred = v.argmax(axis=2)                                # (n, kmax)
        out[name] = (pred == yev[:, None]).mean(axis=0)
    return out


def knn_curve(Xtr: np.ndarray, ytr: np.ndarray, Xev: np.ndarray, yev: np.ndarray,
              n_classes: int, kmax: int, metric: str) -> Dict[str, np.ndarray]:
    nn = NearestNeighbors(n_neighbors=kmax, metric=metric).fit(Xtr)
    dist, idx = nn.kneighbors(Xev)
    return _votes_accuracy(dist, idx, ytr, yev, n_classes, kmax)


def grid_search(X: pd.DataFrame, y: pd.Series, kmax: int = 25, folds: int = 5,
                metrics: Sequence[str] = METRICS, weights: Sequence[str] = WEIGHTS) -> pd.DataFrame:
    """CV stratified: akurasi rata-rata tiap (K, metrik, weights). Preprocessor di-fit per fold."""
    classes = sorted(y.unique())
    yi = y.map({c: i for i, c in enumerate(classes)}).to_numpy()
    acc: Dict[tuple, List[float]] = {}
    skf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=SEED)
    for tr, va in skf.split(X, yi):
        pre = build_pipeline().named_steps["pre"].fit(X.iloc[tr])
        Xtr, Xva = pre.transform(X.iloc[tr]), pre.transform(X.iloc[va])
        for m in metrics:
            res = knn_curve(Xtr, yi[tr], Xva, yi[va], len(classes), kmax, m)
            for w in weights:
                for k in range(1, kmax + 1):
                    acc.setdefault((k, m, w), []).append(res[w][k - 1])
    rows = [{"K": k, "metrik": m, "weights": w, "akurasi_cv": float(np.mean(v)),
             "std": float(np.std(v))} for (k, m, w), v in acc.items()]
    t = pd.DataFrame(rows)
    t = t.sort_values(["akurasi_cv", "K"], ascending=[False, True]).reset_index(drop=True)
    t.insert(0, "peringkat", np.arange(1, len(t) + 1))
    return t


def eval_metrics(pipe: Pipeline, Xte: pd.DataFrame, yte: pd.Series) -> Dict[str, Any]:
    pred = pipe.predict(Xte)
    p, r, f, _ = precision_recall_fscore_support(yte, pred, average="macro", zero_division=0)
    return {"accuracy": float(accuracy_score(yte, pred)), "precision": float(p),
            "recall": float(r), "f1": float(f)}


# ---------------------------------------------------------------- training
def train_and_save(df: pd.DataFrame, k: int | None = None, metric: str | None = None,
                   weights: str | None = None, test_size: float = 0.2, kmax: int = 25,
                   folds: int = 5, save: bool = True) -> Dict[str, Any]:
    """Latih KNN. Bila k/metric/weights kosong -> cari terbaik dengan CV. Simpan .joblib."""
    df = D.clean(df)
    errs = D.validate_schema(df)
    if errs:
        raise ValueError("; ".join(errs))
    Xtr, Xte, ytr, yte = split(df, test_size)
    grid = None
    if k is None or metric is None or weights is None:
        grid = grid_search(Xtr, ytr, kmax=kmax, folds=folds)
        best = grid.iloc[0]
        k, metric, weights = int(best["K"]), str(best["metrik"]), str(best["weights"])
    pipe = build_pipeline(k, metric, weights).fit(Xtr, ytr)
    metrics = eval_metrics(pipe, Xte, yte)
    if grid is not None:
        metrics["cv_accuracy"] = float(grid.iloc[0]["akurasi_cv"])
    train_df = Xtr.copy()
    train_df[D.TARGET] = ytr
    bundle = {
        "pipeline": pipe, "k": int(k), "metric": metric, "weights": weights,
        "classes": [str(c) for c in pipe.named_steps["knn"].classes_],
        "feature_names": {"categorical": D.CAT_COLS, "numeric": D.NUM_COLS, "target": D.TARGET},
        "metrics": metrics, "n_train": int(len(Xtr)), "n_test": int(len(Xte)),
        "trained_at": datetime.now().isoformat(timespec="seconds"),
        "sklearn_version": sklearn.__version__, "data_file": D.data_path().name,
        "train_df": train_df.reset_index(drop=True),
    }
    if save:
        p = D.model_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(bundle, p)
    return bundle


def load_bundle() -> Dict[str, Any]:
    """Muat joblib; jika hilang/rusak/beda versi -> ValueError agar pemanggil melatih ulang."""
    p = D.model_path()
    if not p.exists():
        raise FileNotFoundError(str(p))
    b = joblib.load(p)
    need = {"pipeline", "k", "metric", "weights", "classes", "metrics", "train_df"}
    if not need <= set(b):
        raise ValueError("Isi joblib tidak lengkap")
    if b.get("sklearn_version") != sklearn.__version__:
        raise ValueError("Versi scikit-learn berbeda")
    return b


def load_or_train() -> tuple[Dict[str, Any], bool]:
    """Kembalikan (bundle, dilatih_ulang)."""
    try:
        return load_bundle(), False
    except Exception:
        return train_and_save(D.load_dataframe()), True


def evaluate(df: pd.DataFrame, test_size: float, kmax: int, metric: str, weights: str,
             folds: int) -> Dict[str, Any]:
    """Evaluasi penuh untuk halaman 'Evaluasi & Optimasi K'."""
    df = D.clean(df)
    Xtr, Xte, ytr, yte = split(df, test_size)
    grid = grid_search(Xtr, ytr, kmax=kmax, folds=folds)
    classes = sorted(df[D.TARGET].unique())
    ci = {c: i for i, c in enumerate(classes)}
    pre = build_pipeline().named_steps["pre"].fit(Xtr)
    A, B = pre.transform(Xtr), pre.transform(Xte)
    ytr_i, yte_i = ytr.map(ci).to_numpy(), yte.map(ci).to_numpy()
    test_curve = knn_curve(A, ytr_i, B, yte_i, len(classes), kmax, metric)[weights]
    train_curve = knn_curve(A, ytr_i, A, ytr_i, len(classes), kmax, metric)[weights]
    sel = grid[(grid.metrik == metric) & (grid.weights == weights)].sort_values("K")
    best = grid.iloc[0]
    pipe = build_pipeline(int(best["K"]), str(best["metrik"]), str(best["weights"])).fit(Xtr, ytr)
    pred = pipe.predict(Xte)
    m = eval_metrics(pipe, Xte, yte)
    return {
        "grid": grid, "best": {"k": int(best["K"]), "metric": str(best["metrik"]),
                               "weights": str(best["weights"]), "cv": float(best["akurasi_cv"])},
        "curve": pd.DataFrame({"K": np.arange(1, kmax + 1), "latih": train_curve, "uji": test_curve,
                               "cv": sel["akurasi_cv"].to_numpy()}),
        "metrics": m, "classes": classes,
        "report": pd.DataFrame(classification_report(yte, pred, output_dict=True,
                                                     zero_division=0)).T.reset_index()
                    .rename(columns={"index": "kelas"}),
        "cm": confusion_matrix(yte, pred, labels=classes),
        "params": {"test_size": test_size, "kmax": kmax, "metric": metric, "weights": weights,
                   "folds": folds},
    }


# ------------------------------------------------------------ hitung manual
def manual_knn(bundle: Dict[str, Any], x: Dict[str, Any]) -> Dict[str, Any]:
    """Hitung KNN secara manual (numpy) & bandingkan dengan kneighbors scikit-learn."""
    pipe: Pipeline = bundle["pipeline"]
    pre, knn = pipe.named_steps["pre"], pipe.named_steps["knn"]
    train_df: pd.DataFrame = bundle["train_df"]
    k, metric, weights = bundle["k"], bundle["metric"], bundle["weights"]
    xdf = pd.DataFrame([x])[D.CAT_COLS + D.NUM_COLS]
    T = pre.transform(train_df[D.CAT_COLS + D.NUM_COLS])
    q = pre.transform(xdf)[0]
    diff = T - q
    d = np.sqrt((diff ** 2).sum(axis=1)) if metric == "euclidean" else np.abs(diff).sum(axis=1)
    order = np.lexsort((np.arange(len(d)), d))[:k]
    contrib = diff ** 2 if metric == "euclidean" else np.abs(diff)
    # Gabungkan kolom one-hot per fitur asal
    cat_names = list(pre.named_transformers_["cat"].get_feature_names_out(D.CAT_COLS))
    cols = cat_names + D.NUM_COLS
    grouped = {}
    for c in D.CAT_COLS:
        grouped[c] = contrib[:, [i for i, n in enumerate(cols) if n.startswith(c + "_")]].sum(axis=1)
    for c in D.NUM_COLS:
        grouped[c] = contrib[:, cols.index(c)]
    ytr = train_df[D.TARGET].to_numpy()
    neigh = pd.DataFrame({"peringkat": np.arange(1, k + 1), "indeks": order,
                          "tanaman": ytr[order], "jarak": d[order]})
    for c in D.CAT_COLS + D.NUM_COLS:
        neigh[c] = grouped[c][order]
    if weights == "distance":
        w = np.where(d[order] == 0, 1.0, 1.0 / np.where(d[order] == 0, 1, d[order]))
        if (d[order] == 0).any():
            w = (d[order] == 0).astype(float)
    else:
        w = np.ones(k)
    neigh["bobot"] = w
    votes = {c: float(w[neigh["tanaman"].to_numpy() == c].sum()) for c in bundle["classes"]}
    winner = max(bundle["classes"], key=lambda c: (votes[c], -bundle["classes"].index(c)))
    sk_dist, sk_idx = knn.kneighbors(pre.transform(xdf), n_neighbors=k)
    match_dist = bool(np.allclose(sk_dist[0], d[order], atol=1e-9))
    match_idx = bool(np.array_equal(sk_idx[0], order)) or match_dist and \
        bool(np.array_equal(np.sort(ytr[sk_idx[0]]), np.sort(ytr[order])))
    sk_pred = str(pipe.predict(xdf)[0])
    return {"q": q, "cols": cols, "neighbors": neigh, "votes": votes, "winner": winner,
            "sk_dist": sk_dist[0], "sk_idx": sk_idx[0], "match_dist": match_dist,
            "match_idx": bool(np.array_equal(sk_idx[0], order)), "match_pred": winner == sk_pred,
            "match_all": match_dist and match_idx and winner == sk_pred, "sk_pred": sk_pred,
            "mean": pre.named_transformers_["num"].mean_, "scale": pre.named_transformers_["num"].scale_}


def neighbors_of(bundle: Dict[str, Any], x: Dict[str, Any]) -> pd.DataFrame:
    """K tetangga terdekat (tanaman, jarak, data latih) lewat kneighbors sklearn."""
    pipe = bundle["pipeline"]
    xdf = pd.DataFrame([x])[D.CAT_COLS + D.NUM_COLS]
    dist, idx = pipe.named_steps["knn"].kneighbors(pipe.named_steps["pre"].transform(xdf))
    t = bundle["train_df"].iloc[idx[0]].copy()
    t.insert(0, "jarak", dist[0])
    return t.reset_index(drop=True)


def predict(bundle: Dict[str, Any], x: Dict[str, Any]) -> Dict[str, float]:
    """Probabilitas tiap kelas untuk satu input."""
    pipe = bundle["pipeline"]
    xdf = pd.DataFrame([x])[D.CAT_COLS + D.NUM_COLS]
    p = pipe.predict_proba(xdf)[0]
    return dict(zip([str(c) for c in pipe.named_steps["knn"].classes_], map(float, p)))
