# UEFN Toolbelt — UI Style Guide

> **This is the canonical reference for all windowed UI in the UEFN Toolbelt.**
> Every tool, plugin, or feature that opens a PySide6 window — whether built by Ocean,
> a third-party plugin author, or an AI agent — **must follow this guide exactly.**
> Consistency is non-negotiable. Users should never be able to tell which window came from
> which tool.

---

## TL;DR (Copy-Paste Start)

```python
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PySide6.QtGui import QFont, QColor

# 1. Import the dashboard QSS (single source of truth)
try:
    from ..dashboard_pyside6 import _QSS as _DASH_QSS
except Exception:
    # Inline fallback — copy from verse_device_graph.py _DASH_QSS block
    _DASH_QSS = (
        "QMainWindow,QDialog{background:#181818;}"
        "QWidget{background:#181818;color:#CCCCCC;"
        "font-family:'Segoe UI','Roboto',sans-serif;font-size:12px;}"
        "QPushButton{background:#262626;border:1px solid #363636;"
        "color:#CCCCCC;padding:5px 10px;border-radius:3px;min-height:28px;}"
        "QPushButton:hover{background:#333333;border-color:#4A4A4A;color:#FFFFFF;}"
        "QPushButton:pressed{background:#3A3AFF;border-color:#3A3AFF;color:#FFFFFF;}"
        "QLineEdit{background:#212121;border:1px solid #363636;"
        "color:#CCCCCC;padding:3px 7px;border-radius:3px;min-height:24px;}"
        "QLineEdit:focus{border-color:#3A3AFF;}"
        "QTextEdit{background:#212121;border:1px solid #2A2A2A;color:#CCCCCC;}"
        "QScrollBar:vertical{background:#1A1A1A;width:8px;border-radius:4px;margin:2px 1px;}"
        "QScrollBar::handle:vertical{background:#404040;border-radius:4px;min-height:32px;}"
        "QScrollBar::handle:vertical:hover{background:#606060;}"
        "QScrollBar::handle:vertical:pressed{background:#3A3AFF;}"
        "QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;}"
        "QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical{background:none;}"
        "QStatusBar{background:#111111;color:#555555;font-size:11px;"
        "border-top:1px solid #2A2A2A;}"
    )

# 2. Apply to your window
class MyToolWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(_DASH_QSS)
        self._build_ui()
```

That's all you need. The QSS handles every standard widget automatically.

---

## Color Palette

These are the **only** colors to use in Toolbelt UI. Do not invent new ones.

| Token | Hex | QColor | Use |
|---|---|---|---|
| `bg` | `#181818` | `QColor("#181818")` | Window/root background |
| `panel` | `#212121` | `QColor("#212121")` | Input fields, text areas, secondary panels |
| `card` | `#1E1E1E` | `QColor("#1E1E1E")` | Cards, node bodies, elevated surfaces |
| `border` | `#2A2A2A` | `QColor("#2A2A2A")` | Subtle borders, dividers, splitters |
| `border2` | `#363636` | `QColor("#363636")` | Heavier borders, node outlines, button borders |
| `text` | `#CCCCCC` | `QColor("#CCCCCC")` | Primary text |
| `muted` | `#555555` | `QColor("#555555")` | Secondary / hint text, disabled labels |
| `accent` | `#3A3AFF` | `QColor("#3A3AFF")` | Primary action buttons, focus rings, pressed states |
| `brand` | `#e94560` | `QColor("#e94560")` | Toolbelt brand red — window titles **only** |
| `warn` | `#f1c40f` | `QColor("#f1c40f")` | Warning text and icons |
| `error` | `#FF4444` | `QColor("#FF4444")` | Error text and icons |
| `ok` | `#44FF88` | `QColor("#44FF88")` | Success / healthy state |
| `grid` | `#1A1A1A` | `QColor("#1A1A1A")` | Canvas grid lines, scrollbar track |
| `topbar` | `#111111` | `QColor("#111111")` | Top bar / status bar background |

### Python palette dict (copy into any tool with PySide6 graphics)

```python
_P = {
    "bg":     QColor("#181818"),
    "panel":  QColor("#212121"),
    "card":   QColor("#1E1E1E"),
    "border": QColor("#2A2A2A"),
    "border2":QColor("#363636"),
    "text":   QColor("#CCCCCC"),
    "muted":  QColor("#555555"),
    "accent": QColor("#3A3AFF"),
    "brand":  QColor("#e94560"),
    "warn":   QColor("#f1c40f"),
    "error":  QColor("#FF4444"),
    "ok":     QColor("#44FF88"),
    "grid":   QColor("#1A1A1A"),
}
```

---

## Typography

| Role | Font | Size | Weight |
|---|---|---|---|
| Window title | Segoe UI | 12pt | Bold |
| Section header | Segoe UI | 9–10pt | Bold |
| Body / labels | Segoe UI | 9pt | Normal |
| Monospaced output | Consolas | 8pt | Normal |
| Status bar | Segoe UI | 11px | Normal |

Font family fallback stack (already in `_DASH_QSS`):
```
'Segoe UI', 'Roboto', sans-serif
```

---

## Spacing & Layout

- **Root margins**: `0, 0, 0, 0` — let the top bar / panels handle padding
- **Top bar height**: `46px`
- **Inner content margins**: `12px` horizontal, `8–12px` vertical
- **Widget spacing**: `5–6px`
- **Button height**: `28px` standard, `26px` compact (inline toolbar)
- **Scrollbar width**: `8px` (handled by QSS)
- **Splitter handle**: `1px` wide, color `#2A2A2A`

---

## Standard Widget Recipes

### Top Bar
```python
bar = QWidget()
bar.setFixedHeight(46)
bar.setStyleSheet("background:#111111; border-bottom:1px solid #2A2A2A;")
bl = QHBoxLayout(bar)
bl.setContentsMargins(12, 0, 12, 0)
bl.setSpacing(6)

# Brand title (always use brand red #e94560)
title = QLabel("MY TOOL NAME")
title.setFont(QFont("Segoe UI", 12, QFont.Bold))
title.setStyleSheet("color:#e94560;")
bl.addWidget(title)
```

### Primary (Accent) Button
```python
btn = QPushButton("ACTION")
btn.setFixedHeight(28)
btn.setProperty("accent", "true")   # QSS picks this up automatically
btn.setCursor(Qt.PointingHandCursor)
```

### Secondary Button
```python
btn = QPushButton("Cancel")
btn.setFixedHeight(28)
btn.setCursor(Qt.PointingHandCursor)
# No extra style needed — QSS default handles it
```

### Read-Only Text Area (Monospaced Output)
```python
area = QTextEdit()
area.setReadOnly(True)
area.setStyleSheet(
    "background:#212121; color:#CCCCCC; border:1px solid #2A2A2A; "
    "font-family:Consolas; font-size:8pt; padding:4px;"
)
```

### Editable Notes Area
```python
notes = QTextEdit()
notes.setStyleSheet(
    "background:#212121; color:#CCCCCC; border:1px solid #2A2A2A; "
    "font-family:'Segoe UI'; font-size:9pt; padding:4px;"
)
```

### Divider Line
```python
sep = QFrame()
sep.setFrameShape(QFrame.HLine)
sep.setStyleSheet("color:#363636;")
```

### Status Bar
```python
# QMainWindow status bar is styled by QSS automatically.
# Just call:
self.statusBar().showMessage("Ready")
# Or set it up with a persistent label:
self._status = QLabel("Idle")
self._status.setStyleSheet("color:#555555; font-size:11px;")
```

### Global Health / Progress Bar (4px accent)
```python
hbar = QLabel()
hbar.setFixedHeight(4)
hbar.setStyleSheet("background:#2A2A2A;")

# To show fill at 70%:
pct = 0.70
col = "#27ae60"  # or #f1c40f warn, #FF4444 error
hbar.setStyleSheet(
    f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
    f"stop:0 {col},stop:{pct:.3f} {col},"
    f"stop:{min(pct+0.001,1):.3f} #2A2A2A,stop:1 #2A2A2A);"
    f"border-radius:2px;"
)
```

### Scroll Area with Side Panel
```python
scroll = QScrollArea()
scroll.setWidgetResizable(True)
scroll.setFixedWidth(314)
scroll.setStyleSheet("background:#181818; border:none; border-left:1px solid #2A2A2A;")
panel = QWidget()
panel.setStyleSheet("background:#181818;")
scroll.setWidget(panel)
```

---

## The UEFN Slate Tick Requirement

> **CRITICAL — All PySide6 windows in UEFN need a Slate tick driver or they will be
> invisible/blank.**

UEFN runs Unreal's Slate event loop, not Qt's. Without driving `app.processEvents()` from
a Slate callback, Qt windows open but never render.

**Always include this block when showing a QMainWindow or QDialog:**

```python
import unreal
from PySide6.QtWidgets import QApplication

app = QApplication.instance() or QApplication([])

win = MyToolWindow()
win.show()

# Drive Qt's event loop from Unreal's Slate tick
tick_handle: list = [None]
def _tick(dt: float) -> None:
    try:
        if not win.isVisible():
            unreal.unregister_slate_post_tick_callback(tick_handle[0])
            return
        app.processEvents()
    except Exception:
        try:
            unreal.unregister_slate_post_tick_callback(tick_handle[0])
        except Exception:
            pass

tick_handle[0] = unreal.register_slate_post_tick_callback(_tick)
```

Without this the window will be reported as "opened" in logs but will not appear on screen.

---

## Semantic Color Usage

Use the right color for the right meaning — always:

| Situation | Color |
|---|---|
| Window / tool title | `#e94560` brand red |
| Success, healthy, passing | `#44FF88` ok green |
| Warning, degraded | `#f1c40f` yellow |
| Error, failed, broken | `#FF4444` error red |
| Primary action | `#3A3AFF` accent blue |
| Data output / labels | `#CCCCCC` text |
| Hint / disabled / secondary | `#555555` muted |
| `@editable` / device refs | `#e94560` brand red |
| Events / `.Subscribe` | `#2ecc71` |
| Functions / `.calls` | `#3498db` |

---

## What NOT to Do

- **No purple, blue-grey, or dark navy tints** — no `#0a0a1a`, `#1a1a30`, `#2a2a45`,
  `#3a3a5a`, `#888899`, `#444466`, `#d0d0e0`, or any hex with unequal R/G/B that shifts
  toward blue/purple. The palette is strictly neutral dark grey + accent.
- **No custom button colors** — use `setProperty("accent", "true")` for primary, default
  QSS for secondary. Never hardcode a background on a button.
- **No inline font overrides** — always use the font family fallback stack from `_DASH_QSS`.
- **No bright white backgrounds** — minimum surface brightness is `#181818`.
- **Do not redefine the palette** — import `_QSS` from `dashboard_pyside6`, don't copy-paste
  it and then modify values. The inline fallback in `verse_device_graph.py` exists for
  robustness only and mirrors the source exactly.

---

## For AI Agents

If you are an AI agent (Claude, GPT, Gemini, or any other model) generating code for this
project, apply these rules unconditionally:

1. Every `QMainWindow` or `QDialog` opened by a tool **must** call
   `self.setStyleSheet(_DASH_QSS)` — no exceptions.
2. Import `_DASH_QSS` from `..dashboard_pyside6` with the inline fallback shown above.
3. Use **only** the hex values in the Color Palette table above. Do not introduce new colors.
4. Include the **Slate tick driver** block for every window. UEFN windows without it are invisible.
5. Window title label must use `color:#e94560` (brand red) and `QFont("Segoe UI", 12, QFont.Bold)`.
6. When in doubt, look at `tools/verse_device_graph.py` — it is the reference implementation.

---

## Reference Implementation

`Content/Python/UEFN_Toolbelt/tools/verse_device_graph.py` is the canonical example of a
fully-themed Toolbelt window. It demonstrates:

- `_DASH_QSS` import with inline fallback (line ~664)
- `_P` palette dict (line ~690)
- Top bar layout with brand title + buttons + search (line ~1100)
- 4px health bar with gradient fill (line ~1162)
- `QGraphicsScene/View` canvas with `#181818` background (line ~914)
- `_InfoPanel` side panel with typed text areas (line ~936)
- Slate tick driver (search `register_slate_post_tick_callback`)
