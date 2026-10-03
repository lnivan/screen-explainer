<div align="center">

# Screen Explainer

*A hotkey desktop helper: drag a box around anything on screen and a Gemini model explains it in a floating window.*

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-30363D?style=flat-square)
![google-genai](https://img.shields.io/badge/google--genai-30363D?style=flat-square)
![keyboard](https://img.shields.io/badge/keyboard-30363D?style=flat-square)
![Status](https://img.shields.io/badge/status-prototype-BF8700?style=flat-square)
![Year](https://img.shields.io/badge/year-2026-8250DF?style=flat-square)

</div>

## About

A small PyQt6 app that waits in the background for <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>A</kbd>. The hotkey dims the screen and lets you select a rectangle. The selected pixels go to Google's Gemini API with a fixed request for a short explanation with examples, and the answer appears as formatted text in a dark, always-on-top window next to the selection. On first launch, a small dialog asks for the API key and saves it locally.

> [!WARNING]
> The app installs a system-wide keyboard hook, needs a Gemini API key (saved in plain text in `.env`), and uploads every region you select to Google. It has no window or tray icon while it waits. Stop it by closing the terminal that started it or by ending the Python process.

## Quick start

```bash
python -m pip install -r requirements.txt markdown
python main.py
```

Before the first launch, copy `.env.example` to `.env` and fill in `GEMINI_API_KEY`; otherwise the setup dialog saves the key but the process then hangs, and the app has to be started again from the repository folder after ending that process. `markdown` is installed separately because `requirements.txt` does not list it.

## Controls

| Input | Action |
| --- | --- |
| <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>A</kbd> | Open the capture overlay, from any application |
| Left-drag on the overlay | Select the region to explain (larger than 10 × 10 px) |
| Right-click or <kbd>Esc</kbd> on the overlay | Cancel the capture |
| Drag the answer window by its title bar or border | Move it |
| <kbd>Esc</kbd> or the ✕ button | Hide the answer window |

## How it works

- **Global hotkey.** `keyboard.add_hotkey` fires on the keyboard library's own thread, so the callback only schedules the overlay on the Qt main thread with `QTimer.singleShot(0, …)`.
- **Capture overlay.** Before it appears, the overlay takes a screenshot of the primary screen. It then covers the whole virtual desktop with a frameless, always-on-top window that paints the screenshot under a black tint (alpha 100 of 255) and clears the tint inside the selection, outlined in blue. The crop comes from that screenshot, so the overlay never shows up in the capture.
- **Hand-off.** The cropped `QPixmap` is saved as PNG into an in-memory buffer and reopened with Pillow, because the Gemini SDK accepts Pillow images directly.
- **API call.** A `QThread` worker calls `generate_content` on the hard-coded model `gemini-3.1-pro-preview` with the image, the fixed prompt and the thinking level set to `HIGH`, so the interface stays responsive while it waits. Errors come back as text instead of exceptions.
- **Answer window.** The reply is Markdown, converted to HTML with the `markdown` package and shown in a 450 × 600 px frameless `QTextEdit` panel placed 10 px to the right of the selection and pushed back inside the screen if it would overflow.
- **Key setup.** If `GEMINI_API_KEY` is neither in the environment nor in `.env`, a setup dialog with a masked input field writes `GEMINI_API_KEY="…"` to `.env`.

## Code map

| Path | Role |
| --- | --- |
| `main.py` | Start-up, key check, hotkey registration and the capture → request → answer wiring |
| `src/capture_overlay.py` | Full-screen selection overlay |
| `src/ai_client.py` | Gemini client, model id and prompt |
| `src/response_window.py` | Floating answer window |
| `src/setup_window.py` | First-run API-key dialog |
| `.env.example` | Template for the key file |

## Limitations

- `requirements.txt` does not list `markdown`, which `src/response_window.py` imports, so `pip install -r requirements.txt` alone is not enough.
- Only the primary screen is captured, although the overlay spans every monitor, so selections on other monitors are not captured correctly.
- The prompt is fixed: there is no way to type your own question or ask a follow-up, and each new capture replaces the previous answer.
- The first-run dialog saves the key, but the app does not carry on afterwards: `setQuitOnLastWindowClosed(False)` is set before the dialog's event loop starts, so closing the dialog never returns from it. The dialog also writes `.env` to the current working directory, while the app looks for it next to `main.py`.
- The model id is hard-coded in `src/ai_client.py`. Preview models are retired over time, so it may need updating.
- The `keyboard` package needs administrator rights for global hooks on Linux.

## Background

Written in February 2026; all files date from 24 February 2026.

---

<div align="center"><sub>Part of <a href="https://github.com/lnivan">lnivan's projects</a> · <b>Tools</b></sub></div>
