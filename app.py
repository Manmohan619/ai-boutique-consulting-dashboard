
import streamlit as st
import pandas as pd
import plotly.express as px

# --------- PAGE CONFIG ---------
st.set_page_config(page_title="AI Dashboard | Boutique Consulting (India, SMEs)", layout="wide")

# --------- CUSTOM CSS ---------
st.markdown("""
    <style>
        body {
            background: linear-gradient(180deg, #f9fafc 0%, #eef1f5 100%);
        }
        h1, h2, h3 {
            color: #8B0000;
            font-weight: 700;
        }
        .stDataFrame {border: 1px solid #ddd; border-radius: 10px;}
        .st-emotion-cache-1v0mbdj, .stDownloadButton button {
            background-color: #8B0000 !important;
            color: white !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }
        .st-emotion-cache-1v0mbdj:hover, .stDownloadButton button:hover {
            background-color: #a81c1c !important;
            color: #fff !important;
        }
        .footer {
            background-color: rgba(139, 0, 0, 0.08);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin-top: 40px;
            font-size: 15px;
            line-height: 1.5;
        }
    </style>
""", unsafe_allow_html=True)

# --------- TITLE ---------
st.markdown("<h1 style='text-align:center;'>AI-Integrated Competitor Map 🌐<br>Boutique Consulting Firms Serving Indian SMEs</h1>", unsafe_allow_html=True)

with st.expander("📘 About this Dashboard", expanded=False):
    st.markdown("""
    - **Purpose:** Visualize how boutique consulting firms serving Indian SMEs are positioned, and identify differentiation opportunities.
    - **How it works:** Input or edit firm data (1–10 scale). The dashboard builds an interactive competitor map, computes white-space scores, and suggests differentiators.
    - **Scales:**  
      • *Offering_Nature*: 1 = Functional → 10 = Holistic  
      • *Value_Proposition*: 1 = Cost Efficiency → 10 = Innovation  
      • *SME_Focus*: 1–10 = Strength of SME orientation
    """)

# -------- Helper: explanation logic --------
def explain_row(on, vp, sme):
    def bucket(x):
        if x >= 8: return "high"
        elif x >= 6: return "moderate"
        elif x >= 4: return "mid"
        return "low"

    on_b, vp_b, sme_b = bucket(on), bucket(vp), bucket(sme)

    desc = []
    if on_b == "high": desc.append("holistic, end-to-end advisory")
    elif on_b == "moderate": desc.append("balanced multi-functional advisory")
    else: desc.append("specialist functional consulting")

    if vp_b == "high": desc.append("focused on innovation and transformation")
    elif vp_b == "moderate": desc.append("balancing cost and improvement focus")
    else: desc.append("cost-efficiency-oriented solutions")

    if sme_b == "high": tail = "with strong SME engagement."
    elif sme_b == "moderate": tail = "with selective SME reach."
    else: tail = "with limited SME focus."

    return f"{desc[0]}, {desc[1]} {tail}"

# -------- Load / Edit Data --------
st.markdown("## 🧾 1. Load or Edit Firm Data")

default = pd.read_csv("firms.csv")
uploaded = st.file_uploader("Upload firms.csv (optional)", type=["csv"])
df = pd.read_csv(uploaded) if uploaded else default.copy()

for c in ["Firm","Offering_Nature","Value_Proposition","SME_Focus"]:
    if c not in df.columns:
        df[c] = 5 if c != "Firm" else ""

edited = st.data_editor(
    df[["Firm","Offering_Nature","Value_Proposition","SME_Focus"]],
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "Firm": st.column_config.TextColumn(required=True),
        "Offering_Nature": st.column_config.NumberColumn(min_value=1, max_value=10, step=1),
        "Value_Proposition": st.column_config.NumberColumn(min_value=1, max_value=10, step=1),
        "SME_Focus": st.column_config.NumberColumn(min_value=1, max_value=10, step=1),
    }
)

edited["AI_Explanation"] = [
    explain_row(float(r["Offering_Nature"]), float(r["Value_Proposition"]), float(r["SME_Focus"])) for _, r in edited.iterrows()
]

st.info("🧠 The *AI Explanation* column automatically interprets your scores into qualitative descriptions.")

# -------- Competitor Map --------
st.markdown("## 📊 2. Competitor Map (Interactive)")

fig = px.scatter(
    edited,
    x="Offering_Nature",
    y="Value_Proposition",
    size="SME_Focus",
    color="SME_Focus",
    text="Firm",
    color_continuous_scale=px.colors.sequential.Reds,
    hover_data=["AI_Explanation"],
    labels={
        "Offering_Nature": "Nature of Offering (Functional → Holistic)",
        "Value_Proposition": "Value Proposition (Cost → Innovation)",
        "SME_Focus": "SME Focus"
    }
)
fig.update_traces(textposition="top center")
fig.update_layout(
    height=600,
    plot_bgcolor="#fafafa",
    paper_bgcolor="#f6f6f6",
    font=dict(size=12),
    xaxis=dict(showgrid=True, gridcolor="#ddd"),
    yaxis=dict(showgrid=True, gridcolor="#ddd")
)
st.plotly_chart(fig, use_container_width=True)

# -------- White-space & Differentiators --------
st.markdown("## 🎯 3. White-Space Analysis & Recommendations")

edited["White_Space_Score"] = (edited["Offering_Nature"] + edited["Value_Proposition"]) / 2 - (10 - edited["SME_Focus"]) * 0.1

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 📈 White-Space Scores")
    st.dataframe(
        edited[["Firm","Offering_Nature","Value_Proposition","SME_Focus","AI_Explanation","White_Space_Score"]]
        .sort_values("White_Space_Score", ascending=False),
        use_container_width=True
    )

with col2:
    st.markdown("### 💡 Suggested Differentiators")
    x_mean, y_mean, sme_mean = edited["Offering_Nature"].mean(), edited["Value_Proposition"].mean(), edited["SME_Focus"].mean()
    diffs = []
    if (edited["Value_Proposition"] > y_mean).sum() >= len(edited)//2 and (edited["SME_Focus"] < sme_mean).sum() >= len(edited)//3:
        diffs.append("Implementation-linked pricing for SMEs (tie fees to measurable outcomes).")
    else:
        diffs.append("AI-Enabled SME Strategy Studio (diagnostics dashboard + simulations).")
    if (edited["Offering_Nature"] < x_mean).sum() >= len(edited)//3:
        diffs.append("Holistic transformation packages for Tier-2/Tier-3 SMEs.")
    else:
        diffs.append("Sector playbooks with KPI blueprints for fast rollout.")
    st.success("\n".join([f"• {d}" for d in diffs]))

# -------- Transparency Log --------
st.markdown("## 🧮 4. AI Transparency Log")
prompt_text = st.text_area(
    "Paste your prompts/interactions with AI (for annexure transparency):",
    value="""Core Prompt: List Indian boutique consulting firms serving SMEs and score them (1–10) on Offering_Nature, Value_Proposition, SME_Focus.

Follow-ups:
1) Suggest a 2×2 competitor map and quadrant meanings.
2) Identify white spaces and two differentiators for a new entrant.""",
    height=150
)

# -------- Downloads --------
st.markdown("## 💾 5. Export for Annexure")
csv_data = edited.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download Current Data (CSV)", data=csv_data, file_name="firms_clean.csv", mime="text/csv")
st.download_button("📜 Download AI Prompt Log (TXT)", data=prompt_text.encode("utf-8"), file_name="AI_prompt_log.txt", mime="text/plain")

# -------- Footer --------
st.markdown("---")
st.markdown("""
<div class='footer'>
    <strong>Developed by:</strong> Manmohan Mahapatra<br>
    <strong>For:</strong> Entrepreneurship Individual Project – IIM Ranchi<br>
    <strong>Roll No:</strong> M16D-25<br>
    <em>Designed using Streamlit & Plotly | © 2025</em>
</div>
""", unsafe_allow_html=True)

