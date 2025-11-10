
import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Dashboard | Boutique Consulting (India, SMEs)", layout="wide")

# ---------------- THEME & STYLES (light + cards) ----------------
st.markdown("""
<style>
:root{
  --accent:#0F766E;        /* teal */
  --accent-strong:#0B5E57;
  --muted:#64748B;         /* slate */
  --title:#0F172A;         /* deep slate */
  --text:#111827;          /* near-black */
  --card:#FFFFFF;          /* white */
  --bg:#F7FAFC;            /* very light */
  --border:#E5E7EB;        /* light border */
}
html, body, [class*="stApp"] { background: var(--bg); }

/* Header banner */
.header {
  background: linear-gradient(90deg, #0F766E 0%, #14B8A6 100%);
  color:#fff; padding:18px 22px; border-radius:14px; margin: 6px 0 18px 0;
  box-shadow: 0 6px 18px rgba(15,118,110,0.18);
}
.header .title { font-size: 24px; font-weight:800; letter-spacing:.2px; }
.header .meta { font-size:14px; opacity:.96; margin-top:6px; }

/* Section card */
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 18px 18px 14px 18px;
  box-shadow: 0 6px 22px rgba(2,8,23,0.05);
  margin-bottom: 16px;
}
.section-title{
  color: var(--title);
  font-weight:800;
  font-size: 18px;
  margin: 0 0 12px 0;
  padding-bottom:6px;
  border-bottom: 1px solid var(--border);
}
.subtle{ color: var(--muted); font-size: 13px; }

/* Buttons */
.stDownloadButton button, .stButton > button{
  background: var(--accent) !important; color:#fff !important;
  border-radius:10px !important; font-weight:700 !important; border:0 !important;
}
.stDownloadButton button:hover, .stButton > button:hover{
  background: var(--accent-strong) !important;
}

/* Dataframe rounded */
.stDataFrame, .st-emotion-cache-1v0mbdj {
  border-radius: 10px !important;
}

/* Make select/slider labels darker */
.stMarkdown, .stText, .stSelectbox, .stSlider { color: var(--text); }
</style>
""", unsafe_allow_html=True)

# ---------------- TOP BANNER ----------------
st.markdown("""
<div class="header">
  <div class="title">AI-Integrated Competitor Map • Boutique Consulting (India, SMEs)</div>
  <div class="meta"><strong>Developed by:</strong> Manmohan Mahapatra &nbsp;|&nbsp;
  <strong>For:</strong> Entrepreneurship Individual Project – IIM Ranchi &nbsp;|&nbsp;
  <strong>Roll No:</strong> M16D-25</div>
</div>
""", unsafe_allow_html=True)

# ---------------- ABOUT (card) ----------------
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">About this dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        "- **Purpose:** Visualize competitive positioning of boutique consulting firms serving Indian SMEs; identify white-space and suggest strategy levers.\n"
        "- **How:** Use **sliders (1–10)** to set scores. The map, white-space scores, and recommendations update instantly.\n"
        "- **Scales:**  \n"
        "  • *Offering_Nature*: 1 = Functional → 10 = Holistic  \n"
        "  • *Value_Proposition*: 1 = Cost → 10 = Innovation  \n"
        "  • *SME_Focus*: 1–10 = Strength of SME orientation"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Helper: dynamic explanation logic ----------------
def explain_row(on, vp, sme):
    def bucket(x):
        if x >= 8: return "high"
        elif x >= 6: return "moderate"
        elif x >= 4: return "mid"
        return "low"
    on_b, vp_b, sme_b = bucket(on), bucket(vp), bucket(sme)
    part1 = "holistic, end-to-end advisory" if on_b=="high" else \
            "balanced multi-functional advisory" if on_b=="moderate" else \
            "specialist functional consulting"
    part2 = "innovation-led transformation" if vp_b=="high" else \
            "balanced cost & improvement focus" if vp_b=="moderate" else \
            "cost-efficiency oriented"
    tail = "with strong SME engagement." if sme_b=="high" else \
           "with selective SME reach." if sme_b=="moderate" else \
           "with limited SME focus."
    return f"{part1}, {part2} {tail}"

# ---------------- LOAD DATA (card) ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">1) Load Data</div>', unsafe_allow_html=True)

default = pd.read_csv("firms.csv")
uploaded = st.file_uploader("Upload firms.csv (optional)", type=["csv"])
base_df = pd.read_csv(uploaded) if uploaded else default.copy()
for c in ["Firm","Offering_Nature","Value_Proposition","SME_Focus"]:
    if c not in base_df.columns:
        base_df[c] = 5 if c != "Firm" else ""

if "df" not in st.session_state:
    st.session_state.df = base_df.copy()

c_reset, _ = st.columns([1,3])
with c_reset:
    if st.button("Reset to Loaded Data"):
        st.session_state.df = base_df.copy()
        st.success("Data reset from loaded CSV.")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- MANAGE FIRMS (cards) ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">2) Manage Firms (Add / Edit with Sliders / Delete)</div>', unsafe_allow_html=True)

# Add firm (visible card)
st.markdown("**Add New Firm**")
colA, colB, colC, colD = st.columns([3,1,1,1])
with colA:
    new_name = st.text_input("Firm name", placeholder="Enter firm name")
with colB:
    new_on = st.slider("Offering_Nature", 1, 10, 6, key="add_on")
with colC:
    new_vp = st.slider("Value_Proposition", 1, 10, 6, key="add_vp")
with colD:
    new_sme = st.slider("SME_Focus", 1, 10, 6, key="add_sme")
add_col, _ = st.columns([1,3])
with add_col:
    if st.button("Add firm"):
        if new_name.strip():
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([{
                "Firm": new_name.strip(),
                "Offering_Nature": new_on, "Value_Proposition": new_vp, "SME_Focus": new_sme
            }])], ignore_index=True)
            st.success(f"Added: {new_name.strip()}")
        else:
            st.error("Please enter a firm name.")

st.markdown("---")

# Delete firms (visible card)
st.markdown("**Delete Firms**")
del_sel = st.multiselect("Select firm(s) to delete", options=st.session_state.df["Firm"].tolist())
del_btn, _ = st.columns([1,3])
with del_btn:
    if st.button("Delete selected"):
        st.session_state.df = st.session_state.df[~st.session_state.df["Firm"].isin(del_sel)].reset_index(drop=True)
        st.success("Selected firms deleted.")

st.markdown("---")

# Inline sliders per row (visible, not hidden)
st.markdown("**Edit Firms (sliders update instantly)**")
for i in range(len(st.session_state.df)):
    r = st.session_state.df.loc[i]
    row_c1, row_c2, row_c3, row_c4 = st.columns([3,1,1,1])
    with row_c1:
        name = st.text_input("Firm", value=str(r["Firm"]), key=f"name_{i}")
    with row_c2:
        on = st.slider("Offering", 1, 10, int(r["Offering_Nature"]), key=f"on_{i}")
    with row_c3:
        vp = st.slider("Value", 1, 10, int(r["Value_Proposition"]), key=f"vp_{i}")
    with row_c4:
        sme = st.slider("SME", 1, 10, int(r["SME_Focus"]), key=f"sme_{i}")
    st.session_state.df.loc[i, ["Firm","Offering_Nature","Value_Proposition","SME_Focus"]] = [name, on, vp, sme]

st.markdown('</div>', unsafe_allow_html=True)

# Work copy + explanations
edited = st.session_state.df.copy()
edited["AI_Explanation"] = [
    explain_row(float(r["Offering_Nature"]), float(r["Value_Proposition"]), float(r["SME_Focus"]))
    for _, r in edited.iterrows()
]

# ---------------- COMPETITOR MAP (card) ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">3) Competitor Map (White Background + Smart Labels)</div>', unsafe_allow_html=True)

show_labels = st.checkbox("Show firm labels on chart", value=True)

def choose_positions(df, xcol="Offering_Nature", ycol="Value_Proposition"):
    positions = []
    order = ["top center", "top left", "top right", "bottom left",
             "bottom right", "middle left", "middle right", "bottom center"]
    for i, r in df.iterrows():
        pos = "top center"
        for j in range(0, i):
            dx = abs(r[xcol] - df.iloc[j][xcol])
            dy = abs(r[ycol] - df.iloc[j][ycol])
            if dx < 0.45 and dy < 0.45:
                k = int((dx + dy) * 10) % len(order)
                pos = order[k]
                break
        positions.append(pos)
    return positions

fig = px.scatter(
    edited,
    x="Offering_Nature", y="Value_Proposition",
    size="SME_Focus", color="SME_Focus",
    text="Firm" if show_labels else None,
    color_continuous_scale=px.colors.sequential.Viridis,   # clean light-friendly palette
    hover_data=["AI_Explanation"],
    template="plotly_white",
    labels={
        "Offering_Nature":"Nature of Offering (Functional → Holistic)",
        "Value_Proposition":"Value Proposition (Cost → Innovation)",
        "SME_Focus":"SME Focus"
    }
)

if show_labels:
    fig.update_traces(textposition=choose_positions(edited),
                      textfont=dict(color="#111111", size=12))
fig.update_traces(marker=dict(line=dict(width=2, color="#111111")), cliponaxis=False)

fig.update_layout(
    height=640,
    paper_bgcolor="white", plot_bgcolor="white",
    font=dict(color="#111111", size=14),
    xaxis=dict(range=[0.5,10.5], showgrid=True, gridcolor="#D1D5DB",
               zeroline=False, linecolor="#111111", linewidth=1.2, mirror=True,
               titlefont=dict(color="#111111", size=16), tickfont=dict(color="#111111", size=13)),
    yaxis=dict(range=[0.5,10.5], showgrid=True, gridcolor="#D1D5DB",
               zeroline=False, linecolor="#111111", linewidth=1.2, mirror=True,
               titlefont=dict(color="#111111", size=16), tickfont=dict(color="#111111", size=13)),
    margin=dict(l=10, r=10, t=20, b=10),
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={"displaylogo": False,
            "toImageButtonOptions":{"format":"png","filename":"competitor_map","height":640,"width":1100}}
)

x_mean = float(edited["Offering_Nature"].mean())
y_mean = float(edited["Value_Proposition"].mean())
st.caption(f"Mean reference (for clustering): Offering_Nature **{x_mean:.2f}**, Value_Proposition **{y_mean:.2f}**")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- WHITE-SPACE & STRATEGY (card) ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">4) White-Space Analysis & Strategy Recommendations</div>', unsafe_allow_html=True)

edited["White_Space_Score"] = (edited["Offering_Nature"] + edited["Value_Proposition"]) / 2 - (10 - edited["SME_Focus"]) * 0.1

rows = len(edited)
tbl_height = min(700, 100 + 38 * rows)  # avoid inner scroll bars
st.markdown("**White-Space Scores (higher = more opportunity)**")
st.dataframe(
    edited[["Firm","Offering_Nature","Value_Proposition","SME_Focus","AI_Explanation","White_Space_Score"]]
    .sort_values("White_Space_Score", ascending=False),
    use_container_width=True,
    height=tbl_height
)

sme_mean = edited["SME_Focus"].mean()
diffs = []
if (edited["Value_Proposition"] > y_mean).sum() >= len(edited)//2 and (edited["SME_Focus"] < sme_mean).sum() >= len(edited)//3:
    diffs.append("Outcome-linked pricing for SMEs (fees tied to measured savings/throughput gains).")
else:
    diffs.append("AI-enabled SME Strategy Studio (diagnostics dashboard + scenario simulations).")
if (edited["Offering_Nature"] < x_mean).sum() >= len(edited)//3:
    diffs.append("Holistic transformation packages for Tier-2/Tier-3 SMEs (strategy + process + analytics).")
else:
    diffs.append("Sector playbooks with KPI blueprints for rapid rollout.")

st.markdown("**Strategy Recommendations**")
st.success("\n".join([f"• {d}" for d in diffs]))
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- EXPORT (card) ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">5) Export for Annexure</div>', unsafe_allow_html=True)
csv_data = edited.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download Current Data (CSV)", data=csv_data, file_name="firms_clean.csv", mime="text/csv")
st.markdown('<span class="subtle">Tip: use the chart’s camera icon to download PNG.</span>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
