
import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Dashboard | Boutique Consulting (India, SMEs)", layout="wide")

# ---------------- TOP BANNER ----------------
st.markdown("""
<style>
.top-banner {
  background: linear-gradient(90deg, #8B0000 0%, #A51D1D 100%);
  color: #fff; padding: 14px 20px; border-radius: 12px; margin-bottom: 18px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.12);
}
.top-banner .title { font-size: 22px; font-weight: 800; letter-spacing: .2px; }
.top-banner .meta { font-size: 14px; opacity: .95; margin-top: 4px; }
.section-title { color: #111; font-weight: 800; margin-top: 6px; }
.small-note { color: #444; font-size: 13px; }
</style>
<div class="top-banner">
  <div class="title">AI-Integrated Competitor Map • Boutique Consulting (India, SMEs)</div>
  <div class="meta"><strong>Developed by:</strong> Manmohan Mahapatra &nbsp;|&nbsp;
  <strong>For:</strong> Entrepreneurship Individual Project – IIM Ranchi &nbsp;|&nbsp;
  <strong>Roll No:</strong> M16D-25</div>
</div>
""", unsafe_allow_html=True)

with st.expander("What this dashboard does", expanded=False):
    st.markdown("""
    - **Purpose:** Visualize competitive positioning of boutique consulting firms serving Indian SMEs; identify white-space and suggest differentiators.
    - **How:** Use sliders (1–10) to set scores. The map, white-space scores, and recommendations update instantly.
    - **Scales:**  
      • *Offering_Nature*: 1 = Functional → 10 = Holistic  
      • *Value_Proposition*: 1 = Cost → 10 = Innovation  
      • *SME_Focus*: 1–10 = Strength of SME orientation
    """)

# ---------------- Helper: dynamic explanation logic ----------------
def explain_row(on, vp, sme):
    def bucket(x):
        if x >= 8: return "high"
        elif x >= 6: return "moderate"
        elif x >= 4: return "mid"
        return "low"
    on_b, vp_b, sme_b = bucket(on), bucket(vp), bucket(sme)
    desc = []
    desc.append("holistic, end-to-end advisory" if on_b=="high"
                else "balanced multi-functional advisory" if on_b=="moderate"
                else "specialist functional consulting")
    desc.append("innovation-led transformation" if vp_b=="high"
                else "balanced cost & improvement focus" if vp_b=="moderate"
                else "cost-efficiency oriented")
    tail = "with strong SME engagement." if sme_b=="high" else "with selective SME reach." if sme_b=="moderate" else "with limited SME focus."
    return f"{desc[0]}, {desc[1]} {tail}"

# ---------------- Load CSV (default or upload) ----------------
st.markdown("<h3 class='section-title'>1) Load Data</h3>", unsafe_allow_html=True)

default = pd.read_csv("firms.csv")
uploaded = st.file_uploader("Upload firms.csv (optional)", type=["csv"])
base_df = pd.read_csv(uploaded) if uploaded else default.copy()

# Ensure required cols
for c in ["Firm","Offering_Nature","Value_Proposition","SME_Focus"]:
    if c not in base_df.columns:
        base_df[c] = 5 if c != "Firm" else ""

# Keep in session state so sliders persist
if "df" not in st.session_state:
    st.session_state.df = base_df.copy()

# Option to reset to uploaded/default
if st.button("Reset to Loaded Data"):
    st.session_state.df = base_df.copy()
    st.success("Data reset from loaded CSV.")

df = st.session_state.df

# ---------------- Add / Delete Firms ----------------
st.markdown("<h3 class='section-title'>2) Manage Firms (Add / Edit with Sliders / Delete)</h3>", unsafe_allow_html=True)

with st.expander("➕ Add New Firm", expanded=False):
    new_name = st.text_input("Firm name", placeholder="Enter firm name")
    c1, c2, c3 = st.columns(3)
    with c1:
        new_on = st.slider("Offering_Nature (1–10)", 1, 10, 6, key="add_on")
    with c2:
        new_vp = st.slider("Value_Proposition (1–10)", 1, 10, 6, key="add_vp")
    with c3:
        new_sme = st.slider("SME_Focus (1–10)", 1, 10, 6, key="add_sme")
    if st.button("Add firm"):
        if new_name.strip():
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([{
                "Firm": new_name.strip(),
                "Offering_Nature": new_on,
                "Value_Proposition": new_vp,
                "SME_Focus": new_sme
            }])], ignore_index=True)
            st.success(f"Added: {new_name.strip()}")
        else:
            st.error("Please enter a firm name.")

with st.expander("🗑️ Delete Firms", expanded=False):
    to_delete = st.multiselect("Select firm(s) to delete", options=df["Firm"].tolist())
    if st.button("Delete selected"):
        st.session_state.df = st.session_state.df[~st.session_state.df["Firm"].isin(to_delete)].reset_index(drop=True)
        st.success("Selected firms deleted.")

# ---------------- Slider Editor Per Row ----------------
st.markdown("<div class='small-note'>Use the sliders below to update each firm's scores. Changes apply instantly.</div>", unsafe_allow_html=True)

for i in range(len(st.session_state.df)):
    row = st.session_state.df.loc[i]
    with st.expander(f"✏️ Edit: {row['Firm'] if row['Firm'] else f'Firm {i+1}'}", expanded=False):
        name = st.text_input("Firm", value=row["Firm"], key=f"name_{i}")
        c1, c2, c3 = st.columns(3)
        with c1:
            on = st.slider("Offering_Nature", 1, 10, int(row["Offering_Nature"]), key=f"on_{i}")
        with c2:
            vp = st.slider("Value_Proposition", 1, 10, int(row["Value_Proposition"]), key=f"vp_{i}")
        with c3:
            sme = st.slider("SME_Focus", 1, 10, int(row["SME_Focus"]), key=f"sme_{i}")
        # Apply changes
        st.session_state.df.loc[i, ["Firm","Offering_Nature","Value_Proposition","SME_Focus"]] = [name, on, vp, sme]

edited = st.session_state.df.copy()
edited["AI_Explanation"] = [
    explain_row(float(r["Offering_Nature"]), float(r["Value_Proposition"]), float(r["SME_Focus"]))
    for _, r in edited.iterrows()
]

# ---------------- High-contrast Competitor Map ----------------
st.markdown("<h3 class='section-title'>3) Competitor Map (High-Contrast Interactive)</h3>", unsafe_allow_html=True)

fig = px.scatter(
    edited,
    x="Offering_Nature",
    y="Value_Proposition",
    size="SME_Focus",
    color="SME_Focus",
    text="Firm",
    color_continuous_scale=px.colors.sequential.Inferno,  # high contrast
    hover_data=["AI_Explanation"],
    template="plotly_white",
    labels={
        "Offering_Nature": "Nature of Offering (Functional → Holistic)",
        "Value_Proposition": "Value Proposition (Cost → Innovation)",
        "SME_Focus": "SME Focus"
    }
)
fig.update_traces(
    textposition="top center",
    textfont=dict(color="#111", size=12),
    marker=dict(line=dict(width=1.8, color="#111"))
)
fig.update_layout(
    height=640,
    font=dict(color="#111", size=13),
    xaxis=dict(range=[0.5, 10.5], showgrid=True, gridcolor="#b7b7b7", zeroline=False, linecolor="#111", linewidth=1.2, mirror=True),
    yaxis=dict(range=[0.5, 10.5], showgrid=True, gridcolor="#b7b7b7", zeroline=False, linecolor="#111", linewidth=1.2, mirror=True),
    coloraxis_colorbar=dict(title="SME Focus", tickcolor="#111", titlefont=dict(color="#111"), tickfont=dict(color="#111")),
    margin=dict(l=10, r=10, t=30, b=10)
)
st.plotly_chart(fig, use_container_width=True)

x_mean = float(edited["Offering_Nature"].mean())
y_mean = float(edited["Value_Proposition"].mean())
st.caption(f"Mean reference (for clustering): Offering_Nature **{x_mean:.2f}**, Value_Proposition **{y_mean:.2f}**")

# ---------------- White-space & Differentiators ----------------
st.markdown("<h3 class='section-title'>4) White-Space Analysis & Recommendations</h3>", unsafe_allow_html=True)

edited["White_Space_Score"] = (edited["Offering_Nature"] + edited["Value_Proposition"]) / 2 - (10 - edited["SME_Focus"]) * 0.1

col1, col2 = st.columns(2)
with col1:
    st.markdown("#### White-Space Scores (higher = more opportunity)")
    st.dataframe(
        edited[["Firm","Offering_Nature","Value_Proposition","SME_Focus","AI_Explanation","White_Space_Score"]]
        .sort_values("White_Space_Score", ascending=False),
        use_container_width=True
    )

with col2:
    st.markdown("#### Suggested Differentiators")
    sme_mean = edited["SME_Focus"].mean()
    diffs = []
    if (edited["Value_Proposition"] > y_mean).sum() >= len(edited)//2 and (edited["SME_Focus"] < sme_mean).sum() >= len(edited)//3:
        diffs.append("Implementation-linked pricing for SMEs (fees tied to measurable outcomes).")
    else:
        diffs.append("AI-Enabled SME Strategy Studio (diagnostics dashboard + simulations).")
    if (edited["Offering_Nature"] < x_mean).sum() >= len(edited)//3:
        diffs.append("Holistic transformation packages for Tier-2/Tier-3 SMEs.")
    else:
        diffs.append("Sector playbooks with KPI blueprints for fast rollout.")
    st.success("\n".join([f"• {d}" for d in diffs]))

# ---------------- Transparency Log & Exports ----------------
st.markdown("<h3 class='section-title'>5) AI Transparency & Export</h3>", unsafe_allow_html=True)
prompt_text = st.text_area(
    "Paste your prompts/interactions with AI (for annexure transparency):",
    value="""Core Prompt: List Indian boutique consulting firms serving SMEs and score them (1–10) on Offering_Nature, Value_Proposition, SME_Focus.

Follow-ups:
1) Suggest a 2×2 competitor map and quadrant meanings.
2) Identify white spaces and two differentiators for a new entrant.""",
    height=150
)

csv_data = edited.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download Current Data (CSV)", data=csv_data, file_name="firms_clean.csv", mime="text/csv")
st.download_button("📜 Download AI Prompt Log (TXT)", data=prompt_text.encode("utf-8"), file_name="AI_prompt_log.txt", mime="text/plain")

