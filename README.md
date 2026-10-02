# Screen Explainer

A desktop prototype that captures a screen region and asks Gemini to explain it.

## What it contains

- Ctrl+Shift+A capture overlay and a floating response window.
- Local API-key setup and Markdown response rendering.

## Setup

Use Python 3.12. From the repository folder:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS / Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

## Project status

Requires a locally configured GEMINI_API_KEY. The hard-coded model and live API behavior have not been verified. Captured regions are sent to the configured provider when used.

Copy `.env.example` to `.env` and configure the key locally, or use the setup window. `.env` is excluded from version control.

## Project collection

Part of [lnivan's projects](https://github.com/lnivan), under **Tools**.
