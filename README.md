
# Boutique Consulting (India, SMEs) — Live Competitor Map Dashboard

This Streamlit app lets you **upload/edit a CSV** of boutique consulting firms, visualize an **interactive 2×2 competitor map**, compute a **white-space score**, and generate **recommended differentiators**. It also includes an **AI prompt transparency log** export.

## How to run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
The app will open in your browser (usually http://localhost:8501).

## CSV format
Required columns: `Firm, Offering_Nature, Value_Proposition, SME_Focus`
Optional column: `Evidence_Notes`

Scales:
- Offering_Nature: 1 = Functional/Specialist → 10 = Holistic/End-to-end
- Value_Proposition: 1 = Cost Efficiency → 10 = Innovation/Transformation
- SME_Focus: 1–10 (higher = stronger SME focus)

## Deploy to Streamlit Community Cloud
1. Push these files to a new GitHub repo.
2. Go to share.streamlit.io → "New app" → select your repo → set "app.py" as the entry point.
3. Add requirements.txt if prompted.
4. Click Deploy.

## What to attach in Annexure
- Screenshot of the interactive plot
- Downloaded CSV (cleaned) and AI prompt log (TXT)
- Link to your live dashboard
