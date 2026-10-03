# UtilityHub

A modular, free-to-run Streamlit utility website for common file, text, data, calculator, and developer tasks. Core features work locally without paid APIs, API keys, a database, or an external backend.

## Included tools

- **PDF & documents:** merge PDFs, export page ranges, inspect metadata, extract selectable text, images to PDF, text-file maker.
- **Images:** inspect image metadata, resize while preserving aspect ratio, convert PNG/JPEG/WebP, grayscale/rotate/flip/brightness/contrast.
- **Text:** case conversion, whitespace cleanup, duplicate/blank line handling, line sorting, slug generation, find/replace, approximate statistics, text diff.
- **Developer:** JSON formatting/validation, JSON↔CSV conversion, Base64/URL encoding, hashing, UUID/token generation, regex testing, number bases.
- **Calculators:** arithmetic, percentage, discount/GST estimate, interest, loan EMI estimate, date difference, descriptive statistics.
- **Converters:** length, mass, temperature, area, volume, speed, time, digital storage, pressure, energy, power, frequency, angle.
- **Generators:** QR codes, secure random passwords/tokens, random numbers/choices, color picker, Lorem ipsum, sample CSV/JSON.
- **CSV/data:** preview, missing-value summary, duplicate count/removal, drop missing rows, fill missing values, sort, select/rename columns, numeric conversion, CSV export.
- **Productivity:** temporary notes/checklist, Pomodoro session planner, time-zone conversion.

Tools are registered in `utils/registry.py`; the UI and processing logic are separated into modules.

## Requirements

- Python 3.10 or newer recommended.
- Windows, macOS, or Linux.
- Internet is only needed to install packages and publish/deploy the project; tool operations themselves do not call external APIs.

## Windows PowerShell: run locally

```powershell
cd UtilityHub
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, use a process-only policy for the current PowerShell session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

You can avoid activation altogether:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL printed by Streamlit (usually `http://localhost:8501`).

## Run tests

```powershell
python -m pytest -q
```

Tests use generated in-memory fixtures and do not download datasets.

## Deploy to Streamlit Community Cloud

1. Extract the ZIP and inspect the `UtilityHub` folder.
2. Create a GitHub repository. If you want the deployed app to be public, check the repository visibility and included files first.
3. From inside the project folder, run:
   ```powershell
   git init
   git add .
   git commit -m "Add UtilityHub"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
   git push -u origin main
   ```
4. Sign in to Streamlit Community Cloud and create a new app.
5. Select the repository, branch `main`, and main file path `app.py`.
6. Deploy. The cloud service installs packages from `requirements.txt`.

Deployment was not performed by this project generator. Free hosting may sleep, restart, limit CPU/RAM, or impose platform-specific constraints.

## File limits and privacy

- Streamlit upload limit is configured to 25 MB. Some image tools enforce a 15 MB per-file limit and 25-megapixel image processing limit.
- Uploaded data is processed by the running app and is not intentionally saved to a database or repository. In-memory data can persist for the session; temporary infrastructure behavior depends on the host.
- Public deployment is not suitable for confidential documents unless you independently review the hosting and security configuration. Do not log or share passwords, tokens, Wi-Fi credentials, or private files.
- Download results before leaving the tool. Session-only notes and tasks may be lost after a session ends or server restart.

## Adding a tool

1. Put reusable transformation logic in `utils/core.py` (or a new focused module).
2. Add its category, name, description, and keywords to `utils/registry.py`.
3. Implement its Streamlit UI function in `pages/tools.py`.
4. Register the function in `run_tool`.
5. Add unit tests in `tests/`.
6. Run `python -m pytest -q` and manually test the UI.

## Limitations

- Scanned PDF OCR is not included; text extraction works for selectable text.
- PDF-to-Word and Word-to-PDF fidelity conversion is not included.
- No live currency rates, cloud storage, login, database persistence, or cross-device synchronization.
- Pomodoro is a planning aid, not a background timer; no browser-closed notifications.
- Regex matching has input limits, but this is not a hardened sandbox for arbitrary hostile patterns.
- Browser-level tests and a live cloud deployment are not included.
- Some optional tools from the initial feature wishlist are intentionally omitted rather than shown as nonfunctional buttons.

## Project structure

```text
UtilityHub/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/config.toml
├── assets/logo.svg
├── utils/
│   ├── __init__.py
│   ├── core.py
│   ├── registry.py
│   └── ui.py
├── pages/
│   ├── __init__.py
│   └── tools.py
└── tests/
    └── test_core.py
```
