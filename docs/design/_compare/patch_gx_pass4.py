from pathlib import Path

css = Path(r"C:\dev\Repositories\Online-Lerncampus\app\web\static\gx.css")
c = css.read_text(encoding="utf-8")

# Force Figma-like line-heights on gx chrome to kill vertical drift
needle = """.gx-screen {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  background: #f8fafc;
  color: #0f172a;
  font-family: Inter, "Segoe UI", system-ui, sans-serif;
}"""
repl = """.gx-screen {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  background: #f8fafc;
  color: #0f172a;
  font-family: Inter, "Segoe UI", system-ui, sans-serif;
  line-height: normal;
  -webkit-font-smoothing: antialiased;
}"""
if needle not in c:
    raise SystemExit("gx-screen block missing")
c = c.replace(needle, repl)

# Tighten header/title metrics
for old, new in [
(".gx-page-header h2 {\n  margin: 0;\n  font-size: 20px;\n  font-weight: 800;\n  color: #0f172a;\n}",
 ".gx-page-header h2 {\n  margin: 0;\n  font-size: 20px;\n  font-weight: 800;\n  color: #0f172a;\n  line-height: normal;\n}"),
(".gx-page-header p { margin: 0; color: #475569; font-size: 14px; }",
 ".gx-page-header p { margin: 0; color: #475569; font-size: 14px; line-height: normal; }"),
(".gx-welcome strong { color: #0f172a; font-size: 18px; font-weight: 800; }",
 ".gx-welcome strong { color: #0f172a; font-size: 18px; font-weight: 800; line-height: normal; }"),
(".gx-progress-block.light .gx-progress-meta strong { color: #fff; }",
 ".gx-progress-block.light .gx-progress-meta strong,\n.gx-progress-block.light .gx-progress-meta strong span { color: #fff; }"),
]:
    if old not in c:
        print("WARN missing", old[:40])
    else:
        c = c.replace(old, new)

# Slightly compress page-header vertical padding if still drifted: keep 16 but ensure no extra margins on children
if ".gx-page-header h2, .gx-page-header p { margin: 0; }" not in c:
    c = c.replace(
        ".gx-page-header p { margin: 0; color: #475569; font-size: 14px; line-height: normal; }",
        ".gx-page-header h2, .gx-page-header p { margin: 0; }\n.gx-page-header p { color: #475569; font-size: 14px; line-height: normal; }",
    )

# Reduce pruefung header by 4px if needed via negative? Better: padding 14px 20px for page-header only on pruefung/fortschritt
extra = """
.gx-pruefung .gx-page-header,
.gx-fortschritt .gx-page-header { padding: 14px 20px 12px; }
.gx-exam-hero-top { align-items: flex-start; }
.gx-exam-hero-top .gx-kicker { margin: 0; }
.gx-exam-hero-top strong { margin-top: 4px; line-height: normal; }
.gx-sim img { display: block; }
"""
if ".gx-pruefung .gx-page-header" not in c:
    c += "\n" + extra

css.write_text(c, encoding="utf-8")
print("line-height + header tighten applied")
