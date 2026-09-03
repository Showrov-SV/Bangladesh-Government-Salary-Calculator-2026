# Bangladesh Government Salary Calculator 2026

A bilingual (English/বাংলা) Streamlit calculator based on
**"চাকরি (বেতন ও ভাতাদি) আদেশ, ২০২৬"** (Bangladesh Gazette, Extraordinary,
31 August 2026). Calculates previous vs. new basic salary, allowances,
GPF deduction, gross and net salary, and generates a detailed bilingual PDF
report.

> ⚠️ **Unofficial, independent tool.** Not a government application. Verify
> individual entitlements with your accounts office. Income tax is not
> calculated. See in-app "Calculation Rules" for source clauses and known
> data-verification flags (`# VERIFY` in `data/salary_rules.py`).

## Features
- Grade 1–20 pay-scale step-matching per Section 5 of the gazette
- 3 dated implementation stages (30% / 65% / 100%) + an optional 4th-stage
  slot clearly marked "not defined in source"
- Allowances: House Rent, Medical, Tiffin, Transport, Washing, Charge,
  Domestic Aid, Hill, Education Assistance, Entertainment/Hosting,
  Bangla New Year (shown separately as an annual amount)
- GPF deduction (5/10/15/20%)
- Full previous-vs-new comparison with formulas shown
- Bilingual UI (English / বাংলা) with a single translation dictionary
- Bilingual, detailed PDF report download
- No database, no login, no personal data storage — everything is
  session-only

## Technology
Python + Streamlit (UI/logic) + ReportLab (PDF). No database required.

## Project Structure
```
salary-calculator-2026/
├── app.py
├── requirements.txt
├── calculator/          # pure calculation logic
├── ui/                  # translations + UI helpers
├── pdf/                 # PDF report generator
├── data/                # salary_rules.py — single source of truth for figures
├── assets/fonts/        # place NotoSansBengali-Regular.ttf here
└── tests/
```

## Local Setup
```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Bengali PDF font (required for readable Bengali PDFs)
Download **Noto Sans Bengali** (free, Google Fonts, Regular weight) and
place it at:
```
assets/fonts/NotoSansBengali-Regular.ttf
```
If missing, Bengali PDFs still generate but show a warning banner and fall
back to a non-Bengali font (glyphs will not render correctly). The UI itself
(Streamlit) renders Bengali natively regardless of this font file.

## Run Locally
```bash
streamlit run app.py
```
Open the URL Streamlit prints (usually http://localhost:8501).

## Run Tests
```bash
python tests/test_salary_calculator.py
# or
python -m pytest tests/ -v
```

## Deploy: GitHub
```bash
git init
git add .
git commit -m "Initial salary calculator"
git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

## Deploy: Streamlit Community Cloud
1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click "New app" → select your repository, branch `main`, file `app.py`.
3. Deploy. No secrets or database configuration needed.
4. (Optional) Add the Bengali font file to the repo before deploying so
   Bengali PDFs render correctly on the hosted app too.

## How the Calculation Works
1. **New Basic Salary** — the user's current (old, 2015-scale) basic is
   matched to the nearest lower step of the old grade scale; the same
   position's difference is projected onto the 2026 scale, rounding up to
   the next step if needed (Section 5).
2. **Stage phasing** — the increase (New − Old) is scaled by the selected
   stage's fraction (30% / 65% / 100%) per Section 1(3). This phasing
   fraction-of-increase is an interpretation of the gazette wording, flagged
   in-app.
3. **Allowances** — each allowance is computed only if its eligibility
   condition (grade, location, government housing, toggles) is met — see
   `calculator/allowances.py`, each function cites its gazette section.
4. **Gross Salary** = New Basic (at stage) + applicable allowances.
5. **GPF** = New Basic × selected GPF%.
6. **Net Salary** = Gross Salary − GPF (income tax not included).

## Data Verification Checklist
Before relying on this for real payroll decisions, cross-check
`data/salary_rules.py` entries marked `# VERIFY` (Grades 3, 8, 12, 15, 18
pay-scale steps, and the ৳7,000 "Other area" house-rent minimum for the
৳32,001–৳71,000 basic band) against the original gazette PDF, since these
were visually ambiguous in the scanned document.

## Testing Checklist
- [x] Grade 1 (fixed pay) basic mapping
- [x] Grade 9 starting-step and mid-step mapping
- [x] Out-of-range basic salary validation
- [x] All 3 implementation stages produce increasing basic salary
- [x] House Rent excluded when in government housing
- [x] Gross/Net/Increase formula consistency
- [x] Tiffin/Transport restricted to Grade 11–20
- [x] GPF amount matches percentage × basic for 5/10/15/20%
- [x] All 20 grades calculate without error
- [x] PDF generates in English and Bengali
