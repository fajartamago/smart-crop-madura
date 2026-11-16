"""Tema TANDUR: 25 tema + turunan warna siang/malam + pemeriksaan kontras WCAG."""
from __future__ import annotations

import colorsys
import re
from typing import Dict, List, Tuple

# (nama, primary, secondary, accent-tua)
THEME_LIST: List[Tuple[str, str, str, str]] = [
    ("Sakera Madura", "#B5403A", "#D9A441", "#3E2A24"),
    ("Kerapan Sapi", "#C0392B", "#F4D03F", "#2C3E50"),
    ("Tembakau Pamekasan", "#8B5E3C", "#C9A66B", "#4E342E"),
    ("Garam Sumenep", "#5DADE2", "#ECF0F1", "#34495E"),
    ("Batik Tanean Lanjhang", "#A93226", "#1B4F72", "#D4AC0D"),
    ("Pantai Lombang", "#2E86AB", "#F6C85F", "#6F4E37"),
    ("Api Tak Kunjung Padam", "#E67E22", "#C0392B", "#2C2C2C"),
    ("Bukit Jaddih", "#A1887F", "#D7CCC8", "#5D4037"),
    ("Jagung Emas", "#E0A800", "#7A9A3B", "#5B4B1E"),
    ("Padi Gogo", "#7FA650", "#C5D86D", "#3C5A2A"),
    ("Cabai Rawit", "#D63031", "#FF7675", "#2D3436"),
    ("Kacang Tanah", "#B98B5E", "#E8C9A0", "#6D4C41"),
    ("Singkong", "#A0856C", "#E6D5C3", "#5D4E3E"),
    ("Laut Madura", "#1F7A8C", "#BFDBF7", "#022B3A"),
    ("Suramadu", "#3D5A80", "#98C1D9", "#EE6C4D"),
    ("Keraton Sumenep", "#7B5EA7", "#D4AF37", "#3B2A50"),
    ("Hutan Mangrove", "#2D6A4F", "#95D5B2", "#1B4332"),
    ("Senja Pesisir", "#F4845F", "#F7B267", "#5C374C"),
    ("Zamrud", "#00A878", "#A8E6CF", "#064E3B"),
    ("Lavender Lembut", "#9B8FC7", "#D7CFF0", "#4A4063"),
    ("Rose Pastel", "#E58F9E", "#F8D7DC", "#6B3A45"),
    ("Mint Segar", "#6CC5B0", "#D5F2EB", "#2F5D54"),
    ("Ocean Blue", "#4A90E2", "#BBD8F7", "#1F3A5F"),
    ("Slate Minimal", "#6C7A89", "#D0D6DC", "#2C3A47"),
    ("Midnight Indigo", "#4B4E9E", "#A9ABE0", "#1E2050"),
]
THEMES: Dict[str, Dict[str, str]] = {
    n: {"primary": p, "secondary": s, "accent": a} for n, p, s, a in THEME_LIST
}
THEME_NAMES: List[str] = [t[0] for t in THEME_LIST]
DEFAULT_THEME = "Sakera Madura"
MIN_CONTRAST = 4.5
_HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def is_hex(value: str) -> bool:
    return bool(_HEX.match(value or ""))


# ----------------------------------------------------------------- util warna
def hex_to_rgb(h: str) -> Tuple[float, float, float]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore


def rgb_to_hex(rgb: Tuple[float, float, float]) -> str:
    return "#" + "".join(f"{max(0, min(255, round(c * 255))):02X}" for c in rgb)


def mix(c1: str, c2: str, w2: float) -> str:
    """Campur c1 dan c2; w2 = porsi c2 (0..1)."""
    a, b = hex_to_rgb(c1), hex_to_rgb(c2)
    return rgb_to_hex(tuple(x * (1 - w2) + y * w2 for x, y in zip(a, b)))  # type: ignore


def _hls(c: str):
    r, g, b = hex_to_rgb(c)
    return colorsys.rgb_to_hls(r, g, b)


def _from_hls(h: float, l: float, s: float) -> str:
    return rgb_to_hex(colorsys.hls_to_rgb(h, max(0, min(1, l)), max(0, min(1, s))))


def lighten(c: str, amt: float) -> str:
    h, l, s = _hls(c)
    return _from_hls(h, l + amt, s)


def darken(c: str, amt: float) -> str:
    return lighten(c, -amt)


def set_lightness(c: str, lo: float, hi: float, sat_scale: float = 1.0) -> str:
    h, l, s = _hls(c)
    return _from_hls(h, max(lo, min(hi, l)), s * sat_scale)


def rgba(c: str, alpha: float) -> str:
    r, g, b = (round(v * 255) for v in hex_to_rgb(c))
    return f"rgba({r},{g},{b},{alpha})"


def luminance(c: str) -> float:
    def f(v: float) -> float:
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (f(v) for v in hex_to_rgb(c))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(c1: str, c2: str) -> float:
    l1, l2 = sorted((luminance(c1), luminance(c2)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def ensure_contrast(fg: str, bg: str, minimum: float = MIN_CONTRAST) -> str:
    """Sesuaikan fg (gelap/terang) hingga kontras terhadap bg >= minimum."""
    if contrast(fg, bg) >= minimum:
        return fg
    direction = -1 if luminance(bg) > 0.4 else 1
    cur = fg
    for _ in range(100):
        cur = lighten(cur, 0.02 * direction)
        if contrast(cur, bg) >= minimum:
            return cur
    return "#000000" if direction < 0 else "#FFFFFF"


def best_on(bg: str) -> str:
    return "#FFFFFF" if contrast("#FFFFFF", bg) >= contrast("#000000", bg) else "#000000"


# --------------------------------------------------------------- turunan tema
def palette(theme: str, mode: str) -> Dict[str, str]:
    """Hasilkan seluruh variabel warna untuk tema & mode ('siang'/'malam')."""
    t = THEMES.get(theme, THEMES[DEFAULT_THEME])
    pri, sec, acc = t["primary"], t["secondary"], t["accent"]
    night = mode == "malam"
    if not night:
        bg = set_lightness(mix(sec, "#FFFFFF", 0.89), 0.92, 0.95, 0.6)
        bg_hi, bg_lo = lighten(bg, 0.03), darken(bg, 0.03)
        sh_light = rgba("#FFFFFF", 0.90)
        sh_dark = rgba(darken(bg, 0.14), 0.75)
        text = ensure_contrast(acc, bg)
        muted = ensure_contrast(mix(text, bg, 0.45), bg)
        primary = pri
    else:
        bg = set_lightness(mix(acc, "#000000", 0.55), 0.12, 0.17)
        bg_hi, bg_lo = lighten(bg, 0.03), darken(bg, 0.03)
        sh_light = rgba(lighten(bg, 0.07), 0.55)
        sh_dark = rgba("#000000", 0.55)
        text = ensure_contrast(mix(sec, "#FFFFFF", 0.85), bg)
        muted = ensure_contrast(mix(text, bg, 0.45), bg)
        primary = lighten(pri, 0.12)
    on_primary = best_on(primary)
    if contrast(on_primary, primary) < MIN_CONTRAST:
        primary = ensure_contrast(primary, on_primary)
    # primary sebagai warna TEKS di atas bg harus terbaca juga
    primary_text = ensure_contrast(primary, bg)
    surface = mix(bg, "#FFFFFF" if night else "#000000", 0.06 if night else 0.04)
    return {
        "bg": bg, "bg_hi": bg_hi, "bg_lo": bg_lo,
        "sh_light": sh_light, "sh_dark": sh_dark,
        "text": text, "muted": muted,
        "primary": primary, "on_primary": on_primary, "primary_text": primary_text,
        "secondary": sec, "accent": acc, "surface": surface,
        "grid": rgba(text, 0.18), "night": "1" if night else "0",
    }


def contrast_report(theme: str, mode: str) -> Dict[str, float]:
    p = palette(theme, mode)
    return {
        "text/bg": contrast(p["text"], p["bg"]),
        "muted/bg": contrast(p["muted"], p["bg"]),
        "primary_text/bg": contrast(p["primary_text"], p["bg"]),
        "on_primary/primary": contrast(p["on_primary"], p["primary"]),
    }
