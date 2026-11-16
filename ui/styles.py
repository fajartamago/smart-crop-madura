"""CSS neumorphism lembut + 3D yang mengikuti palet tema (siang/malam)."""
from __future__ import annotations

from typing import Dict


def build_css(p: Dict[str, str]) -> str:
    css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@500;600;700;800&display=swap');
:root{
  --bg:%(bg)s; --bg-hi:%(bg_hi)s; --bg-lo:%(bg_lo)s;
  --sh-light:%(sh_light)s; --sh-dark:%(sh_dark)s;
  --text:%(text)s; --muted:%(muted)s;
  --primary:%(primary)s; --on-primary:%(on_primary)s; --primary-text:%(primary_text)s;
  --secondary:%(secondary)s; --accent:%(accent)s; --surface:%(surface)s; --grid:%(grid)s;
  --raise: 9px 9px 18px var(--sh-dark), -9px -9px 18px var(--sh-light);
  --raise-sm: 5px 5px 10px var(--sh-dark), -5px -5px 10px var(--sh-light);
  --inset: inset 5px 5px 10px var(--sh-dark), inset -5px -5px 10px var(--sh-light);
  --grad: linear-gradient(145deg, var(--bg-hi), var(--bg-lo));
}
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"]{
  background:var(--bg) !important; color:var(--text);
  font-family:'Inter',sans-serif; transition:background .3s,color .3s;
}
.stApp *{ scrollbar-color: var(--primary) var(--bg-lo); }
header[data-testid="stHeader"]{ background:transparent !important; }
.stAppDeployButton, [data-testid="stAppDeployButton"], div[data-testid="stAppDeployButton"],
[data-testid="stToolbar"]{ display:none !important; visibility:hidden !important; }
[data-testid="stToolbar"], [data-testid="stDecoration"]{ background:transparent !important; }
[data-testid="stToolbar"] *{ color:var(--text) !important; }
footer, [data-testid="stFooter"], .viewerBadge_container__1QSob{ display:none !important; visibility:hidden; }
.block-container{ max-width:1240px; padding-top:2.2rem; padding-bottom:1rem; }
h1,h2,h3,h4,h5{ font-family:'Poppins',sans-serif !important; color:var(--text) !important; letter-spacing:-.01em; }
h3{ color:var(--primary-text) !important; }
p, li, label, span, div, td, th, small, caption{ color:var(--text); }
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li{ color:var(--text); line-height:1.6; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] *{ color:var(--muted) !important; }
a{ color:var(--primary-text) !important; }
hr{ border-color:var(--grid) !important; }
code{ background:var(--bg-lo) !important; color:var(--text) !important; border-radius:8px; padding:1px 6px; }
pre{ background:var(--bg-lo) !important; border-radius:16px; box-shadow:var(--inset); }
pre code{ background:transparent !important; }

/* ---------------- Sidebar ---------------- */
[data-testid="stSidebar"]{ background:var(--bg) !important; box-shadow:6px 0 18px var(--sh-dark); border-right:0; }
[data-testid="stSidebar"] > div:first-child{ background:var(--bg) !important; }
[data-testid="stSidebarContent"]{ background:var(--bg) !important; }
[data-testid="stSidebarCollapseButton"] button, [data-testid="stExpandSidebarButton"]{ background:var(--bg) !important; color:var(--text) !important; }
[data-testid="stSidebarCollapseButton"] *, [data-testid="stExpandSidebarButton"] *{ color:var(--text) !important; fill:var(--text) !important; }
.tandur-logo{ font-family:'Poppins',sans-serif; font-weight:800; font-size:1.5rem; letter-spacing:.14em; color:var(--primary-text);
  display:flex; align-items:center; gap:8px; margin:0; }
.tandur-logo small{ display:block; font-family:'Inter'; font-weight:500; letter-spacing:0; font-size:.78rem; color:var(--muted); }
.side-author{ border-radius:18px; padding:12px 14px; box-shadow:var(--inset); font-size:.78rem; line-height:1.5; color:var(--muted); margin-top:10px; }
.side-author b{ color:var(--text); }

/* ---------------- Neumorphism: kartu ---------------- */
.neo-card, div[data-testid="stExpander"], div[data-testid="stForm"], [class*="st-key-card_"]{
  background:var(--grad) !important; border-radius:24px !important; box-shadow:var(--raise) !important;
  border:0 !important; padding:1.1rem 1.3rem; margin-bottom:1rem; transition:transform .25s, box-shadow .25s;
}
div[data-testid="stExpander"]{ padding:.2rem .6rem; }
div[data-testid="stExpander"] details, div[data-testid="stExpander"] summary{ background:transparent !important; border:0 !important; }
div[data-testid="stExpander"] summary *{ color:var(--text) !important; }
.neo-card.tilt:hover{ transform:perspective(900px) rotateX(2deg) rotateY(-2deg) translateY(-3px);
  box-shadow:14px 14px 28px var(--sh-dark), -10px -10px 22px var(--sh-light), 0 18px 28px -14px var(--sh-dark) !important; }
.neo-inset{ border-radius:18px; box-shadow:var(--inset); padding:.8rem 1rem; background:var(--bg); }

/* ---------------- Banner ---------------- */
.st-key-banner{ background:var(--grad) !important; border-radius:28px; padding:1.4rem 1.8rem .6rem;
  box-shadow:var(--raise), 0 22px 34px -22px var(--sh-dark); margin-bottom:1rem; position:relative; overflow:hidden;
  border-left:10px solid var(--primary); }
.banner-grid{ display:grid; grid-template-columns: 1fr auto; gap:1rem; align-items:center; }
.banner-title{ font-family:'Poppins',sans-serif; font-weight:800; font-size:clamp(2.1rem,6vw,3.6rem); line-height:1;
  letter-spacing:.12em; color:var(--primary-text); margin:0; text-shadow:2px 2px 0 var(--sh-light), 4px 5px 8px var(--sh-dark); }
.banner-tag{ font-family:'Poppins',sans-serif; font-weight:600; font-size:clamp(.92rem,2.4vw,1.2rem); color:var(--text); margin:.35rem 0 0; }
.banner-en{ font-family:'Poppins',sans-serif; font-variant:small-caps; letter-spacing:.09em; font-weight:600; font-size:clamp(.78rem,2vw,.98rem); color:var(--muted); margin:.15rem 0 0; }
.banner-sub{ font-size:clamp(.82rem,2vw,.95rem); color:var(--text); margin:.15rem 0 .6rem; }
.chips{ display:flex; flex-wrap:wrap; gap:8px; margin:.2rem 0 .6rem; }
.chip{ font-size:.76rem; font-weight:600; padding:5px 12px; border-radius:999px; background:var(--bg); box-shadow:var(--raise-sm); color:var(--text); }
.chip b{ color:var(--primary-text); }
.mascot{ width:150px; filter:drop-shadow(6px 8px 8px var(--sh-dark)); }
.mascot svg{ width:100%%; height:auto; transform-origin:50%% 92%%; animation:sway 3.4s ease-in-out infinite; }
@keyframes sway{ 0%%,100%%{ transform:rotate(-3deg);} 50%%{ transform:rotate(3deg);} }
@media (prefers-reduced-motion: reduce){ .mascot svg{ animation:none; } }

/* ---------------- Tombol ---------------- */
div.stButton > button, div.stDownloadButton > button, div[data-testid="stFormSubmitButton"] > button,
button[data-testid^="stBaseButton"]{
  background:var(--grad) !important; color:var(--text) !important; border:0 !important; border-radius:18px !important;
  box-shadow:var(--raise-sm) !important; min-height:44px; font-weight:600; transition:all .2s; padding:.45rem 1rem;
}
div.stButton > button *, div.stDownloadButton > button *, div[data-testid="stFormSubmitButton"] > button *{ color:var(--text) !important; }
div.stButton > button:hover, div.stDownloadButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover{
  transform:translateY(-2px); box-shadow:8px 8px 16px var(--sh-dark), -8px -8px 16px var(--sh-light) !important; }
div.stButton > button:active, div.stDownloadButton > button:active, div[data-testid="stFormSubmitButton"] > button:active{
  transform:translateY(0); box-shadow:var(--inset) !important; }
div.stButton > button:focus-visible, div.stDownloadButton > button:focus-visible, div[data-testid="stFormSubmitButton"] > button:focus-visible,
.stApp :focus-visible{ outline:3px solid var(--primary-text) !important; outline-offset:2px; }
button[kind="primary"], button[data-testid="stBaseButton-primary"], div[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"]{
  background:var(--primary) !important; color:var(--on-primary) !important; }
button[data-testid="stBaseButton-primary"] *, button[kind="primary"] *{ color:var(--on-primary) !important; }

/* ---------------- Navigasi pill ---------------- */
.st-key-page{ margin:.2rem 0 1rem; }
.st-key-page [data-testid="stWidgetLabel"]{ display:none !important; }
.st-key-page [data-testid="stRadioGroup"]{ display:flex; flex-wrap:nowrap; gap:12px; overflow-x:auto; padding:10px 8px 16px; scrollbar-width:thin; -webkit-overflow-scrolling:touch; }
.st-key-page [data-testid="stRadioGroup"] > div{ flex:0 0 auto; }
.st-key-page label[data-testid="stRadioOption"]{ background:var(--grad); border-radius:999px; box-shadow:var(--raise-sm); padding:.55rem 1.1rem !important;
  min-height:44px; display:flex; align-items:center; cursor:pointer; transition:all .2s; margin:0 !important; white-space:nowrap; }
.st-key-page label[data-testid="stRadioOption"]:hover{ transform:translateY(-2px); }
.st-key-page label[data-testid="stRadioOption"] > div > div:first-child{ display:none !important; }
.st-key-page label[data-testid="stRadioOption"] p{ color:var(--text); font-weight:600; font-size:.9rem; margin:0; }
.st-key-page label[data-testid="stRadioOption"]:has(input:checked){ background:var(--primary); box-shadow:inset 4px 4px 9px rgba(0,0,0,.28), inset -3px -3px 8px rgba(255,255,255,.18); }
.st-key-page label[data-testid="stRadioOption"]:has(input:checked) p{ color:var(--on-primary) !important; }
.st-key-page label[data-testid="stRadioOption"]:has(input:focus-visible){ outline:3px solid var(--primary-text); outline-offset:2px; }

/* ---------------- Input (inset) ---------------- */
div[data-baseweb="select"] > div, div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="textarea"],
[data-testid="stNumberInputContainer"], input, textarea{
  background:var(--bg) !important; color:var(--text) !important; border:0 !important; border-radius:16px !important; }
div[data-baseweb="select"] > div, div[data-baseweb="input"], [data-testid="stNumberInputContainer"], div[data-baseweb="textarea"]{ box-shadow:var(--inset) !important; }
div[data-baseweb="select"] *{ color:var(--text) !important; }
div[data-baseweb="select"], div[data-baseweb="select"] div, div[data-baseweb="select"] input{ background:transparent !important; box-shadow:none !important; border:0 !important; }
div[data-baseweb="select"] > div{ overflow:hidden; background:var(--bg) !important; box-shadow:var(--inset) !important; }
div[data-baseweb="select"] svg, [data-testid="stNumberInputContainer"] svg{ fill:var(--text) !important; }
input::placeholder, textarea::placeholder{ color:var(--muted) !important; opacity:1; }
[data-testid="stNumberInputContainer"] button{ background:var(--bg) !important; color:var(--text) !important; }
div[data-baseweb="tag"]{ background:var(--primary) !important; border-radius:12px !important; }
div[data-baseweb="tag"] *{ color:var(--on-primary) !important; }
/* portal dropdown / popover / tooltip */
div[data-baseweb="popover"], div[data-baseweb="popover"] > div, div[data-baseweb="menu"], ul[role="listbox"], div[data-baseweb="calendar"]{
  background:var(--bg) !important; color:var(--text) !important; border-radius:18px !important; box-shadow:var(--raise) !important; border:0 !important; }
li[role="option"], ul[role="listbox"] li{ background:transparent !important; color:var(--text) !important; }
li[role="option"]:hover, li[role="option"][aria-selected="true"], ul[role="listbox"] li:hover{ background:var(--bg-lo) !important; }
div[data-baseweb="tooltip"], div[data-baseweb="tooltip"] > div, [data-testid="stTooltipContent"]{ background:var(--bg) !important; color:var(--text) !important; border-radius:14px !important; box-shadow:var(--raise-sm) !important; }
[data-testid="stTooltipContent"] *{ color:var(--text) !important; }
[data-testid="stTooltipIcon"] svg{ fill:var(--muted) !important; color:var(--muted) !important; }
/* slider */
div[data-baseweb="slider"] > div > div:first-child{ background:var(--bg) !important; box-shadow:var(--inset); border-radius:10px; height:8px; }
div[data-baseweb="slider"] > div > div:first-child > div{ background:var(--primary) !important; border-radius:10px; }
div[data-baseweb="slider"] div[role="slider"]{ background:var(--primary) !important; box-shadow:var(--raise-sm) !important; border:0 !important; }
div[data-baseweb="slider"] div[role="slider"] div{ color:var(--primary-text) !important; background:transparent !important; }
[data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"]{ color:var(--muted) !important; }
[data-testid="stSliderThumbValue"]{ color:var(--primary-text) !important; font-weight:700; }
/* toggle / checkbox */
label[data-baseweb="checkbox"] > span:first-child{ background:var(--bg) !important; box-shadow:var(--inset); border:0 !important; }
div[data-baseweb="checkbox"] [role="checkbox"][aria-checked="true"], label[data-baseweb="checkbox"]:has(input:checked) > span:first-child{ background:var(--primary) !important; }
[data-testid="stCheckbox"] label p, [data-testid="stToggle"] label p{ color:var(--text) !important; }
/* radio biasa (selain navigasi) */
[data-testid="stRadio"] label[data-testid="stRadioOption"] p{ color:var(--text) !important; }
/* ---- DOM Streamlit baru (role=group, virtual dropdown, dll.) ---- */
[data-testid="stSelectbox"] div[role="group"], [data-testid="stMultiSelect"] div[role="group"], [data-testid="stNumberInput"] div[role="group"],
[data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"], [data-testid="stDateInputField"]{
  background:var(--bg) !important; border:0 !important; border-radius:16px !important; box-shadow:var(--inset) !important; color:var(--text) !important; }
[data-testid="stSelectbox"] input, [data-testid="stMultiSelect"] input, [data-testid="stNumberInput"] input, [data-testid="stTextInputRootElement"] input{
  background:transparent !important; color:var(--text) !important; box-shadow:none !important; }
[data-testid="stSelectbox"] div[role="group"] button, [data-testid="stMultiSelect"] div[role="group"] button, [data-testid="stNumberInput"] button{
  background:transparent !important; color:var(--text) !important; }
[data-testid="stSelectbox"] button svg, [data-testid="stSelectbox"] button svg path, [data-testid="stMultiSelect"] button svg, [data-testid="stMultiSelect"] button svg path, [data-testid="stNumberInput"] button svg{
  fill:var(--text) !important; color:var(--text) !important; }
[data-testid="stSelectbox"] [data-testid="stSelectboxValue"], [data-testid="stSelectbox"] div[role="group"] *{ color:var(--text) !important; }
[data-testid="stSelectboxVirtualDropdown"], [data-testid="stSelectboxVirtualDropdown"] *, [role="listbox"], [role="listbox"] *{
  background:var(--bg) !important; color:var(--text) !important; }
[data-testid="stSelectboxVirtualDropdown"]{ border-radius:18px !important; box-shadow:var(--raise) !important; }
[role="option"]:hover, [role="option"]:hover *, [role="option"][aria-selected="true"], [role="option"][aria-selected="true"] *{ background:var(--bg-lo) !important; }
[data-testid="stRadio"] label[data-testid="stRadioOption"] > div > div:first-child > div{ background:var(--bg) !important; box-shadow:var(--inset); border-color:transparent !important; }
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] *{ color:var(--text) !important; }

[data-testid="stRadio"] [class*="ex50key4"], [data-testid="stRadio"] [class*="ex50key5"] {
  background: var(--bg-lo) !important;
  border-color: var(--grid) !important;
}
[data-testid="stRadio"] [data-selected="true"] [class*="ex50key4"] {
  background: var(--primary) !important;
}
/* alerts, toast, progress */
div[data-testid="stAlert"], div[data-testid="stNotification"]{ background:var(--grad) !important; border-radius:18px !important; box-shadow:var(--raise-sm); border:0 !important; border-left:6px solid var(--primary) !important; }
div[data-testid="stAlert"] *, div[data-testid="stToast"] *{ color:var(--text) !important; }
div[data-testid="stAlert"] > div, div[data-testid="stAlertContainer"], div[data-testid="stAlert"] [role="alert"]{ background:transparent !important; }
div[data-testid="stToast"]{ background:var(--bg) !important; border-radius:18px !important; box-shadow:var(--raise) !important; }
[data-testid="stSpinner"] *{ color:var(--text) !important; }
[data-testid="stFileUploader"] section, [data-testid="stFileUploaderDropzone"]{ background:var(--bg) !important; box-shadow:var(--inset); border:0 !important; border-radius:18px !important; }
[data-testid="stFileUploaderDropzone"] *{ color:var(--text) !important; }
[data-testid="stFileUploaderDropzone"] button{ background:var(--bg-lo) !important; }
[data-testid="stMetric"]{ background:var(--grad); border-radius:20px; box-shadow:var(--raise-sm); padding:.8rem 1rem; }
[data-testid="stMetricValue"], [data-testid="stMetricValue"] *{ color:var(--primary-text) !important; font-family:'Poppins'; }
[data-testid="stMetricLabel"] *{ color:var(--muted) !important; }
[data-testid="stLatex"], .katex{ color:var(--text) !important; }
[data-testid="stPlotlyChart"]{ border-radius:20px; overflow:hidden; }
[data-testid="stPlotlyChart"] iframe{ background:transparent; }
.modebar{ background:transparent !important; }
.modebar-btn path{ fill:var(--muted) !important; }
/* menu Streamlit (portal) */
[data-testid="stMainMenuPopover"] *, ul[data-testid="main-menu-list"], ul[data-testid="main-menu-list"] *{ background:var(--bg) !important; color:var(--text) !important; }

/* ---------------- Hasil rekomendasi ---------------- */
.result-card{ background:var(--grad); border-radius:28px; padding:1.4rem 1.6rem; display:flex; align-items:center; gap:1.2rem;
  box-shadow:var(--raise), 0 24px 32px -22px var(--sh-dark); transition:transform .3s; border-bottom:8px solid var(--rc,var(--primary)); }
.result-card:hover{ transform:perspective(900px) rotateX(2.5deg) rotateY(-3deg) translateY(-3px); }
.result-emoji{ font-size:4rem; filter:drop-shadow(4px 6px 5px var(--sh-dark)); line-height:1; }
.result-label{ font-size:.82rem; color:var(--muted); font-weight:600; letter-spacing:.08em; text-transform:uppercase; }
.result-name{ font-family:'Poppins'; font-weight:800; font-size:clamp(1.7rem,5vw,2.6rem); color:var(--primary-text); text-transform:capitalize; line-height:1.1; }
.result-conf{ font-size:1rem; color:var(--text); font-weight:600; }
.bar-row{ display:flex; align-items:center; gap:10px; margin:10px 0; }
.bar-name{ width:112px; font-weight:600; font-size:.88rem; text-transform:capitalize; }
.bar-track{ flex:1; height:16px; border-radius:10px; box-shadow:var(--inset); background:var(--bg); overflow:hidden; }
.bar-fill{ height:100%%; border-radius:10px; box-shadow:2px 0 6px var(--sh-dark); }
.bar-val{ width:54px; text-align:right; font-weight:700; font-size:.88rem; }
.badge{ display:inline-block; padding:3px 12px; border-radius:999px; font-size:.76rem; font-weight:700; background:var(--bg); box-shadow:var(--raise-sm); }
.badge.ok{ color:var(--primary-text); } .badge.warn{ color:var(--text); border:1.5px solid var(--primary-text); }
.fit-row{ display:grid; grid-template-columns: 1.4fr .9fr 1fr 3fr; gap:8px; align-items:center; padding:7px 4px; border-bottom:1px dashed var(--grid); font-size:.88rem; }
.fit-head{ font-weight:700; color:var(--muted); font-size:.78rem; text-transform:uppercase; }
.disclaimer{ font-size:.82rem; color:var(--muted); border-radius:16px; padding:.7rem 1rem; box-shadow:var(--inset); margin:.8rem 0; }
.plant-card{ display:flex; gap:1rem; align-items:center; }
.kv{ display:flex; flex-wrap:wrap; gap:10px; margin:.4rem 0; }
.kv span{ padding:6px 12px; border-radius:14px; box-shadow:var(--inset); font-size:.84rem; }

/* ---------------- Tabel HTML ---------------- */
.tbl-wrap{ overflow-x:auto; max-height:520px; border-radius:20px; box-shadow:var(--inset); background:var(--bg); padding:6px; -webkit-overflow-scrolling:touch; }
.tbl{ border-collapse:separate; border-spacing:0; width:100%%; font-size:.84rem; color:var(--text); }
.tbl th{ position:sticky; top:0; background:var(--bg-hi); color:var(--primary-text); text-align:left; padding:9px 12px; font-family:'Poppins'; font-weight:600; white-space:nowrap; z-index:1; border-bottom:2px solid var(--grid); }
.tbl td{ padding:7px 12px; white-space:nowrap; border-bottom:1px solid var(--grid); color:var(--text); }
.tbl tr:nth-child(even) td{ background:var(--bg-lo); }
.tbl tr:hover td{ background:var(--grid); }

/* ---------------- Overlay loading ---------------- */
.load-ov{ position:fixed; inset:0; z-index:999999; background:var(--bg); opacity:.93; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:14px;
  backdrop-filter:blur(3px); animation:fadein .15s ease; }
.load-box{ background:var(--grad); border-radius:28px; box-shadow:var(--raise); padding:26px 40px; display:flex; flex-direction:column; align-items:center; gap:10px; }
.load-text{ font-family:'Poppins'; font-weight:600; color:var(--text); font-size:1rem; text-align:center; }
.grow{ width:64px; height:64px; position:relative; }
.grow .stem{ position:absolute; left:50%%; bottom:6px; width:6px; height:6px; background:var(--primary); border-radius:3px; transform:translateX(-50%%); animation:stem 1.4s ease-in-out infinite; }
.grow .leaf{ position:absolute; bottom:30px; width:22px; height:14px; background:var(--primary); opacity:0; border-radius:14px 0 14px 0; animation:leaf 1.4s ease-in-out infinite; }
.grow .l1{ left:50%%; transform-origin:0 100%%; } .grow .l2{ right:50%%; transform:scaleX(-1); transform-origin:100%% 100%%; animation-delay:.1s; }
.grow .soil{ position:absolute; left:6px; right:6px; bottom:0; height:8px; border-radius:6px; background:var(--accent); opacity:.8; }
@keyframes stem{ 0%%{ height:4px; } 55%%,100%%{ height:40px; } }
@keyframes leaf{ 0%%,35%%{ opacity:0; transform:scale(.2);} 70%%,100%%{ opacity:1; transform:scale(1);} }
@keyframes fadein{ from{ opacity:0;} to{ opacity:.93;} }

/* ---------------- Footer ---------------- */
.tandur-footer{ text-align:center; font-size:.8rem; color:var(--muted); padding:1.2rem .5rem .4rem; margin-top:1.5rem; border-top:1px solid var(--grid); }

/* ---------------- Responsif ---------------- */
html, body, .stApp{ overflow-x:hidden; }
@media (max-width:1024px){ .block-container{ padding-left:1.4rem; padding-right:1.4rem; } .mascot{ width:128px; } }
@media (max-width:768px){
  .block-container{ padding:1rem .8rem .5rem; }
  .st-key-banner{ padding:1rem 1rem .4rem; }
  .banner-grid{ grid-template-columns:1fr; }
  .banner-grid .mascot{ order:-1; width:96px; margin:0 auto; }
  div[data-testid="stHorizontalBlock"]{ flex-wrap:wrap !important; gap:.6rem !important; }
  div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]{ min-width:100%% !important; flex:1 1 100%% !important; }
  div.stButton > button, div.stDownloadButton > button, div[data-testid="stFormSubmitButton"] > button{ min-height:44px; min-width:44px; }
  .result-card{ flex-direction:column; text-align:center; } .result-emoji{ font-size:3rem; }
  .fit-row{ grid-template-columns:1fr 1fr; } .fit-head{ display:none; }
  .bar-name{ width:92px; font-size:.8rem; }
  .neo-card, div[data-testid="stForm"]{ padding:.9rem; border-radius:20px !important; }
  h1{ font-size:1.6rem !important; } h2{ font-size:1.35rem !important; } h3{ font-size:1.1rem !important; }
}
@media (max-width:480px){ .banner-title{ letter-spacing:.06em; } .chip{ font-size:.7rem; padding:4px 9px; } .mascot{ width:84px; } }
</style>
"""
    return css % p
