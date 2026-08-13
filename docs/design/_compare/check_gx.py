from pathlib import Path
t = Path(r"C:\dev\Repositories\Online-Lerncampus\app\web\static\screens.js").read_text(encoding="utf-8")
keys = [
    's19_1-home-dashboard": ()',
    's19_2-lernen-journey": ()',
    's19_3-pruefung-hub": ()',
    's19_4-fortschritt-stats": ()',
    's19_5-profil-settings": ()',
]
for k in keys:
    print(k, k in t)
print("gx-screen count", t.count("gx-screen"))
print("around s03_1", t.find('"s03_1-dashboard-default"'))
# find OLC_SCREENS
idx = t.find("window.OLC_SCREENS")
print("OLC_SCREENS", idx)
print(t[idx:idx+200] if idx>=0 else "missing")
