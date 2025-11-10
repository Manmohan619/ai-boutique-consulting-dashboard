
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Boutique Consulting – SME Competitor Map", layout="wide")
st.title("AI-Integrated Competitor Map • Boutique Consulting (India, SMEs)")

with st.expander("About this dashboard", expanded=False):
    st.markdown(
        "- **Purpose:** Map boutique consulting firms serving Indian SMEs and suggest differentiators.\n"
        "- **How it works:** Upload or edit a CSV of firms with 1–10 scores. The app builds an interactive 2×2 map, ranks white-space, and recommends differentiators.\n"
        "- **Scales:**\n"
        "  - *Offering_Nature*: 1 = Functional/Specialist → 10 = Holistic/End-to-end\n"
        "  - *Value_Proposition*: 1 = Cost Efficiency → 10 = Innovation/Transformation\n"
        "  - *SME_Focus*: 1–10 (higher = stronger SME focus)"
    )

# -------- Helper: dynamic explanation generator (no API) --------
def explain_row(on: float, vp: float, sme: float) -> str:
    # Buckets
    def b(x):
        if x >= 8: return "high"
        if x >= 6: return "mid"
        if x >= 4: return "moderate"
        return "low"

    on_b, vp_b, sme_b = b(on), b(vp), b(sme)

    phrases = []

    # Offering Nature
    if on_b == "high":
        phrases.append("holistic, end-to-end advisory")
    elif on_b in ("mid", "moderate"):
        phrases.append("balanced scope across strategy and functions")
    else:
        phrases.append("specialist, function-focused services")

    # Value Proposition
    if vp_b == "high":
        phrases.append("innovation-led value (transformation, analytics, digital)")
    elif vp_b in ("mid", "moderate"):
        phrases.append("mixed value (cost and improvement initiatives)")
    else:
        phrases.append("cost-efficiency driven engagements")

    # SME focus
    if sme_b == "high":
        tail = "with strong SME orientation"
    elif sme_b in ("mid", "moderate"):
        tail = "with selective SME penetration"
    else:
        tail = "with limited SME focus"

    return f"{phrases[0]} with {phrases[1]}, {tail}."

# -------- Data Input --------
st.subheader("1) Load or Edit Data")

# Expecting at least Firm, Offering_Nature, Value_Proposition, SME_Focus in CSV
default = pd.read_csv("firms.csv")
uploaded = st.file_uploader("Upload firms.csv (optional)", type=["csv"])
if uploaded:
    df = pd.read_csv(uploaded)
else:
    df = default.copy()

# Ensure required columns exist; create missing ones gracefully
for col in ["Firm","Offering_Nature","Value_Proposition","SME_Focus"]:
    if col not in df.columns:
        if col == "Firm":
            df[col] = ""
        else:
            df[col] = 5

# Inline editor
edited = st.data_editor(
    df[["Firm","Offering_Nature","Value_Proposition","SME_Focus"]],
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "Firm": st.column_config.TextColumn(required=True),
        "Offering_Nature": st.column_config.NumberColumn(min_value=1, max_value=10, step=1),
        "Value_Proposition": st.column_config.NumberColumn(min_value=1, max_value=10, step=1),
        "SME_Focus": st.column_config.NumberColumn(min_value=1, max_value=10, step=1),
    },
)

required_cols = {"Firm","Offering_Nature","Value_Proposition","SME_Focus"}
if not required_cols.issubset(edited.columns):
    st.error("CSV must include columns: Firm, Offering_Nature, Value_Proposition, SME_Focus")
    st.stop()

# -------- Dynamic AI_Explanation --------
explanations = []
for _, r in edited.iterrows():
    try:
        explanations.append(explain_row(float(r["Offering_Nature"]), float(r["Value_Proposition"]), float(r["SME_Focus"])))
    except Exception:
        explanations.append("Automatic explanation unavailable (check numeric inputs).")
edited["AI_Explanation"] = explanations

st.caption("📝 **Dynamic note:** The *AI_Explanation* is auto-generated from the three scores; update scores to refresh the narrative.")

# -------- Analysis: Map --------
st.subheader("2) Competitor Map (Interactive)")
fig = px.scatter(
    edited,
    x="Offering_Nature",
    y="Value_Proposition",
    text="Firm",
    size="SME_Focus",
    hover_data=["SME_Focus","AI_Explanation"],
    labels={
        "Offering_Nature": "Nature of Offering (Functional → Holistic)",
        "Value_Proposition": "Value Proposition (Cost Efficiency → Innovation)",
    },
)
fig.update_traces(textposition="top center")
fig.update_layout(height=600, xaxis=dict(range=[0.5, 10.5]), yaxis=dict(range=[0.5, 10.5]), hovermode="closest")
st.plotly_chart(fig, use_container_width=True)

x_mean = float(edited["Offering_Nature"].mean())
y_mean = float(edited["Value_Proposition"].mean())
st.caption(f"Mean lines — Offering_Nature: **{x_mean:.2f}**, Value_Proposition: **{y_mean:.2f}**")

# -------- White-space & Differentiators --------
st.subheader("3) White-Space & Differentiators")

edited["White_Space_Score"] = (edited["Offering_Nature"] + edited["Value_Proposition"]) / 2 - (10 - edited["SME_Focus"]) * 0.1

left, right = st.columns([1, 1])
with left:
    st.markdown("**Computed White_Space_Score (higher suggests potential opportunity)**")
    st.dataframe(
        edited[["Firm","Offering_Nature","Value_Proposition","SME_Focus","AI_Explanation","White_Space_Score"]]
        .sort_values("White_Space_Score", ascending=False),
        use_container_width=True
    )

with right:
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
    value="""Core Prompt: List Indian boutique consulting firms serving SMEs and score them (1–10) on:
(a) Nature of Offering (functional → holistic),
(b) Value Proposition (cost-efficiency → innovation),
(c) SME focus.
Provide 1–2 lines of evidence per firm.

Follow-ups:
1) Suggest a 2×2 competitor map and quadrant meanings.
2) Based on clustering, identify white spaces and two differentiators.""",
    height=160,
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

st.success("✅ Dashboard ready. The AI_Explanation column updates automatically from your scores.")
