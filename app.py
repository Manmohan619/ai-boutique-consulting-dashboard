
import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
import base64

st.set_page_config(page_title="Boutique Consulting – SME Competitor Map", layout="wide")

st.title("AI-Integrated Competitor Map • Boutique Consulting (India, SMEs)")

with st.expander("About this dashboard", expanded=False):
    st.markdown(
        "- **Purpose:** Map boutique consulting firms serving Indian SMEs and suggest differentiators.\n"
        "- **How it works:** Upload or edit a CSV of firms with 1–10 scores. The app builds an interactive 2×2 map, clusters, and recommendations.\n"
        "- **Scales:**\n"
        "  - *Offering_Nature*: 1 = Functional/Specialist → 10 = Holistic/End-to-end\n"
        "  - *Value_Proposition*: 1 = Cost Efficiency → 10 = Innovation/Transformation\n"
        "  - *SME_Focus*: 1–10 (higher = stronger SME focus)"
    )

# -------- Data Input --------
st.subheader("1) Load or Edit Data")
default = pd.read_csv("firms.csv")
uploaded = st.file_uploader("Upload firms.csv (optional)", type=["csv"])
if uploaded:
    df = pd.read_csv(uploaded)
else:
    df = default.copy()

# Inline editor
edited = st.data_editor(
    df,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "Firm": st.column_config.TextColumn(required=True),
        "Offering_Nature": st.column_config.NumberColumn(min_value=1, max_value=10, step=1),
        "Value_Proposition": st.column_config.NumberColumn(min_value=1, max_value=10, step=1),
        "SME_Focus": st.column_config.NumberColumn(min_value=1, max_value=10, step=1),
    }
)

# Validate
required_cols = {"Firm","Offering_Nature","Value_Proposition","SME_Focus"}
if not required_cols.issubset(edited.columns):
    st.error("CSV must include columns: Firm, Offering_Nature, Value_Proposition, SME_Focus")
    st.stop()

# -------- Analysis --------
st.subheader("2) Competitor Map (Interactive)")
fig = px.scatter(
    edited,
    x="Offering_Nature",
    y="Value_Proposition",
    text="Firm",
    size="SME_Focus",
    hover_data=["SME_Focus","Evidence_Notes"] if "Evidence_Notes" in edited.columns else ["SME_Focus"],
    labels={
        "Offering_Nature":"Nature of Offering (Functional → Holistic)",
        "Value_Proposition":"Value Proposition (Cost Efficiency → Innovation)",
    },
)
fig.update_traces(textposition="top center")
fig.update_layout(height=600, xaxis=dict(range=[0.5,10.5]), yaxis=dict(range=[0.5,10.5]), hovermode="closest")
st.plotly_chart(fig, use_container_width=True)

# Quadrant lines
x_mean = float(edited["Offering_Nature"].mean())
y_mean = float(edited["Value_Proposition"].mean())

st.caption(f"Mean lines — Offering_Nature: **{x_mean:.2f}**, Value_Proposition: **{y_mean:.2f}**")

# -------- White-space & Differentiators --------
st.subheader("3) White-Space & Differentiators")

edited["White_Space_Score"] = (edited["Offering_Nature"] + edited["Value_Proposition"]) / 2 - (10 - edited["SME_Focus"]) * 0.1

left, right = st.columns([1,1])
with left:
    st.markdown("**Computed White_Space_Score (higher suggests potential opportunity)**")
    st.dataframe(
        edited[["Firm","Offering_Nature","Value_Proposition","SME_Focus","White_Space_Score"]]
        .sort_values("White_Space_Score", ascending=False),
        use_container_width=True
    )

with right:
    # Rule-based differentiators
    sme_mean = float(edited["SME_Focus"].mean())
    diffs = []
    if (edited["Value_Proposition"] > y_mean).sum() >= len(edited) // 2 and (edited["SME_Focus"] < sme_mean).sum() >= len(edited) // 3:
        diffs.append("Implementation-linked pricing for SMEs (tie fees to measurable outcomes).")
    else:
        diffs.append("AI-Enabled SME Strategy Studio (diagnostics dashboard + scenario simulations).")
    if (edited["Offering_Nature"] < x_mean).sum() >= len(edited) // 3:
        diffs.append("Holistic transformation packages (strategy + process + analytics) for Tier-2/Tier-3 SMEs.")
    else:
        diffs.append("Sector playbooks with industry KPIs for rapid rollout.")
    st.markdown("**Recommended Differentiators**")
    st.write("- " + "\n- ".join(diffs))

# -------- Transparency Log --------
st.subheader("4) AI Transparency Log (paste your prompts)")
prompt_text = st.text_area(
    "Paste prompts/interactions with AI (this will be downloadable as a TXT)",
    value=(
        "Core Prompt: List Indian boutique consulting firms serving SMEs and score them (1–10) on:
"
        " (a) Nature of Offering (functional → holistic),
 (b) Value Proposition (cost-efficiency → innovation),
 (c) SME focus.
"
        "Provide 1–2 lines of evidence per firm.

"
        "Follow-ups:
"
        "1) Suggest a 2×2 competitor map and quadrant meanings.
"
        "2) Based on clustering, identify white spaces and two differentiators."
    ),
    height=160
)

# -------- Downloads --------
st.subheader("5) Export for Annexure")
def make_downloadable_csv(df: pd.DataFrame):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download current data (CSV)", data=csv, file_name="firms_clean.csv", mime="text/csv")

def make_downloadable_txt(txt: str, name: str):
    st.download_button(name, data=txt.encode("utf-8"), file_name="AI_prompt_log.txt", mime="text/plain")

make_downloadable_csv(edited)
make_downloadable_txt(prompt_text, "Download AI Prompt Log (TXT)")

st.success("Done. Add the PNG screenshot(s) of the plot and these downloads to your Annexure.")

