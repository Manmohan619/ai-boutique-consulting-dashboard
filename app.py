
import streamlit as st
import pandas as pd
import plotly.express as px

# ==================== PAGE CONFIG ====================
st.set_page_config(page_title="AI Dashboard | Boutique Consulting (India, SMEs)", layout="wide")

# ==================== GLOBAL STYLES ====================
st.markdown("""
<style>
/* Header banner */
.top-banner{
  background: linear-gradient(90deg,#0f766e 0%,#2563eb 100%);
  color:#fff;padding:18px 22px;border-radius:14px;margin-bottom:16px;
  box-shadow:0 8px 22px rgba(0,0,0,.10)
}
.top-banner .title{font-size:24px;font-weight:800;letter-spacing:.3px}
.top-banner .meta{font-size:14px;opacity:.98;margin-top:6px}

/* Card blocks – theme aware */
.card{border-radius:14px;padding:16px 18px;margin:12px 0;border:1px solid}
@media (prefers-color-scheme: dark){
  .card{background:#0f172a;border-color:#1f2937;box-shadow:0 6px 18px rgba(0,0,0,.35)}
  .h3{color:#e5e7eb}.subtle{color:#94a3b8}
}
@media (prefers-color-scheme: light){
  .card{background:#ffffff;border-color:#e8ecf4;box-shadow:0 6px 18px rgba(17,24,39,.06)}
  .h3{color:#0f172a}.subtle{color:#475569}
}
.h3{font-weight:800;font-size:18px;margin-bottom:10px}
.subtle{font-size:13px}

/* Buttons */
.stDownloadButton button,.stButton>button{
  background:#0f766e !important;color:#fff !important;border-radius:10px !important;font-weight:700 !important
}
.stDownloadButton button:hover,.stButton>button:hover{background:#115e59 !important}

/* Soft border on tables */
.stDataFrame{border:1px solid #e5e7eb;border-radius:10px}

/* Hide truly empty blocks (prevents blank ribbons) */
.block-container > div:empty{display:none}

/* ---- Chart wrapper for rounded border ---- */
.plot-card{
  border:1.75px solid #000; border-radius:12px; overflow:hidden;
  background: transparent;
  padding:0; margin:0;
}

/* Fallback darkening for colorbar text if Plotly ignores font settings */
.plot-card .colorbar text,
.plot-card .colorbar-title{ fill:#000000 !important; }
</style>
""", unsafe_allow_html=True)

# ==================== HEADER ====================
st.markdown("""
<div class="top-banner">
  <div class="title">AI-Integrated Competitor Map • Boutique Consulting (India, SMEs)</div>
  <div class="meta"><strong>Developed by:</strong> Manmohan Mahapatra &nbsp;|&nbsp;
  <strong>For:</strong> Entrepreneurship Individual Project – IIM Ranchi &nbsp;|&nbsp;
  <strong>Roll No:</strong> M16D-25</div>
</div>
""", unsafe_allow_html=True)

# ==================== HELPERS ====================
def explain_row(on, vp, sme):
    """Short natural-language explanation for the 3 scores."""
    def bucket(x):
        if x >= 8: return "high"
        if x >= 6: return "moderate"
        if x >= 4: return "mid"
        return "low"
    on_b, vp_b, sme_b = bucket(on), bucket(vp), bucket(sme)
    a = "holistic, end-to-end advisory" if on_b=="high" else "balanced multi-functional advisory" if on_b=="moderate" else "specialist functional consulting"
    b = "innovation-led transformation" if vp_b=="high" else "balanced cost & improvement focus" if vp_b=="moderate" else "cost-efficiency oriented"
    c = "with strong SME engagement." if sme_b=="high" else "with selective SME reach." if sme_b=="moderate" else "with limited SME focus."
    return f"{a}, {b} {c}"

def ws_interpretation(score: float) -> str:
    """Human-readable inference for the white-space score."""
    if score >= 7.5:
        return "Very high opportunity (few rivals; strong SME value gap)"
    elif score >= 6.0:
        return "High opportunity (attractive niche to pursue)"
    elif score >= 4.5:
        return "Moderate (differentiation needed to win)"
    else:
        return "Low (crowded or weak value pocket)"

# ==================== 1) LOAD DATA ====================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="h3">1) Load Data</div>', unsafe_allow_html=True)

default = pd.read_csv("firms.csv")
uploaded = st.file_uploader("Upload firms.csv (optional)", type=["csv"])
base_df = pd.read_csv(uploaded) if uploaded else default.copy()
for c in ["Firm","Offering_Nature","Value_Proposition","SME_Focus"]:
    if c not in base_df.columns:
        base_df[c] = 5 if c!="Firm" else ""

if "df" not in st.session_state:
    st.session_state.df = base_df.copy()

c_reset, c_tip = st.columns([0.22, 0.78])
with c_reset:
    if st.button("Reset to Loaded Data"):
        st.session_state.df = base_df.copy()
        st.success("Data reset.")
with c_tip:
    st.markdown('<div class="subtle">Tip: Add firms below and adjust scores with sliders. Changes apply instantly.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==================== 2) MANAGE FIRMS ====================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="h3">2) Manage Firms</div>', unsafe_allow_html=True)

# Add firm
c1, c2, c3, c4, c5 = st.columns([0.32, 0.18, 0.18, 0.18, 0.14])
new_name = c1.text_input("Firm name", placeholder="Enter firm name")
new_on   = c2.slider("Offering_Nature", 1, 10, 6, key="add_on")
new_vp   = c3.slider("Value_Proposition", 1, 10, 6, key="add_vp")
new_sme  = c4.slider("SME_Focus", 1, 10, 6, key="add_sme")
if c5.button("Add firm"):
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

# Delete firms
st.markdown("**Delete firms**")
d1, d2 = st.columns([0.72, 0.28])
with d1:
    to_delete = st.multiselect("Select firm(s) to delete", options=st.session_state.df["Firm"].tolist())
with d2:
    if st.button("Delete selected"):
        st.session_state.df = st.session_state.df[~st.session_state.df["Firm"].isin(to_delete)].reset_index(drop=True)
        st.success("Selected firms deleted.")
st.markdown('</div>', unsafe_allow_html=True)

# ==================== 3) EDIT SCORES (SLIDERS) ====================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="h3">3) Edit Scores (Sliders)</div><div class="subtle">Adjust below; changes apply instantly.</div>', unsafe_allow_html=True)

for i in range(len(st.session_state.df)):
    row = st.session_state.df.loc[i]
    st.write(f"**{row['Firm'] if row['Firm'] else f'Firm {i+1}'}**")
    cols = st.columns([0.34, 0.22, 0.22, 0.22])
    name = cols[0].text_input("Firm", value=str(row["Firm"]), key=f"name_{i}")
    on   = cols[1].slider("Offering_Nature", 1, 10, int(row["Offering_Nature"]), key=f"on_{i}")
    vp   = cols[2].slider("Value_Proposition", 1, 10, int(row["Value_Proposition"]), key=f"vp_{i}")
    sme  = cols[3].slider("SME_Focus", 1, 10, int(row["SME_Focus"]), key=f"sme_{i}")
    st.session_state.df.loc[i, ["Firm","Offering_Nature","Value_Proposition","SME_Focus"]] = [name, on, vp, sme]

st.markdown('</div>', unsafe_allow_html=True)

# Snapshot + explanation
edited = st.session_state.df.copy()
edited["AI_Explanation"] = [
    explain_row(float(r["Offering_Nature"]), float(r["Value_Proposition"]), float(r["SME_Focus"]))
    for _, r in edited.iterrows()
]

# ==================== 4) COMPETITOR MAP ====================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="h3">4) Competitor Map (Light-Blue Plot + Smart Labels)</div>', unsafe_allow_html=True)

show_labels = st.checkbox("Show firm labels on chart", value=True)

def choose_positions(df, xcol="Offering_Nature", ycol="Value_Proposition"):
    positions, order = [], ["top center","top left","top right","bottom left","bottom right","middle left","middle right","bottom center"]
    for i, r in df.iterrows():
        pos = "top center"
        for j in range(0, i):
            dx = abs(r[xcol] - df.iloc[j][xcol]); dy = abs(r[ycol] - df.iloc[j][ycol])
            if dx < 0.45 and dy < 0.45:
                k = int((dx + dy) * 10) % len(order)
                pos = order[k]; break
        positions.append(pos)
    return positions

fig = px.scatter(
    edited,
    x="Offering_Nature", y="Value_Proposition",
    size="SME_Focus", color="SME_Focus",
    text="Firm" if show_labels else None,
    color_continuous_scale=px.colors.sequential.Viridis,
    hover_data=["AI_Explanation"],
    template="plotly_white",
    labels={
        "Offering_Nature":"Nature of Offering (Functional → Holistic)",
        "Value_Proposition":"Value Proposition (Cost → Innovation)",
        "SME_Focus":"SME Focus"
    }
)

# Subtle light-blue plot; transparent paper so wrapper shows rounded corners
fig.layout.plot_bgcolor = "#eefaFF"
fig.layout.paper_bgcolor = "rgba(0,0,0,0)"

# Axes: force visible ticks & labels
fig.update_xaxes(
    range=[0.5,10.5], showgrid=True, gridcolor="#cfd4da",
    zeroline=False, showline=True, linecolor="#000", linewidth=1.4, mirror=True,
    showticklabels=True, ticks='outside', ticklen=6, tickcolor="#000",
    tickmode='linear', tick0=1, dtick=1,
    title_text="Nature of Offering (Functional → Holistic)",
    title_font=dict(color="#000", size=14), tickfont=dict(color="#000", size=12)
)
fig.update_yaxes(
    range=[0.5,10.5], showgrid=True, gridcolor="#cfd4da",
    zeroline=False, showline=True, linecolor="#000", linewidth=1.4, mirror=True,
    showticklabels=True, ticks='outside', ticklen=6, tickcolor="#000",
    tickmode='linear', tick0=1, dtick=1,
    title_text="Value Proposition (Cost → Innovation)",
    title_font=dict(color="#000", size=14), tickfont=dict(color="#000", size=12)
)

# Labels dark + bubble outline
if show_labels:
    fig.update_traces(textposition=choose_positions(edited), textfont=dict(color="#000", size=12))
fig.update_traces(marker=dict(line=dict(width=2, color="#000")), cliponaxis=False)

# Colorbar INSIDE the plot with dark text (and a subtle readable backdrop)
try:
    fig.update_layout(
        coloraxis_colorbar=dict(
            title=dict(text="SME Focus", font=dict(color="#000", size=12)),
            tickfont=dict(color="#000", size=11),
            x=0.985, xanchor="right", y=0.5, yanchor="middle",
            len=0.9, thickness=12,
            bgcolor="rgba(255,255,255,0.55)",
            outlinecolor="#000", outlinewidth=1
        )
    )
except Exception:
    pass

# Slightly wider margins to guarantee tick labels show
fig.update_layout(margin=dict(l=40, r=40, t=35, b=50))

# Render inside rounded border card
st.markdown('<div class="plot-card">', unsafe_allow_html=True)
st.plotly_chart(
    fig, use_container_width=True,
    config={"displaylogo": False,
            "toImageButtonOptions": {"format":"png","filename":"competitor_map","height":640,"width":1100}}
)
st.markdown('</div>', unsafe_allow_html=True)

x_mean = float(edited["Offering_Nature"].mean())
y_mean = float(edited["Value_Proposition"].mean())
st.caption(f"Mean reference: Offering_Nature **{x_mean:.2f}**, Value_Proposition **{y_mean:.2f}**")

st.markdown('</div>', unsafe_allow_html=True)

# ==================== 5) WHITE-SPACE + STRATEGY ====================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="h3">5) White-Space Analysis & Strategy Recommendations</div>', unsafe_allow_html=True)

edited["White_Space_Score"] = (edited["Offering_Nature"] + edited["Value_Proposition"]) / 2 - (10 - edited["SME_Focus"]) * 0.1
edited["WS_Interpretation"] = edited["White_Space_Score"].apply(ws_interpretation)

rows = len(edited)
tbl_height = min(720, 120 + 38 * rows)
st.markdown("**White-Space Scores (higher = more opportunity)**")
st.dataframe(
    edited[[
        "Firm","Offering_Nature","Value_Proposition","SME_Focus",
        "AI_Explanation","White_Space_Score","WS_Interpretation"
    ]].sort_values("White_Space_Score", ascending=False),
    use_container_width=True, height=tbl_height
)

# Strategy recommendations (simple rules on distribution)
sme_mean = edited["SME_Focus"].mean()
diffs = []
if (edited["Value_Proposition"] > y_mean).sum() >= len(edited)//2 and (edited["SME_Focus"] < sme_mean).sum() >= len(edited)//3:
    diffs.append("Outcome-linked pricing for SMEs (fees tied to measured savings/throughput gains).")
else:
    diffs.append("AI-enabled SME Strategy Studio (diagnostics + scenario simulations).")
if (edited["Offering_Nature"] < x_mean).sum() >= len(edited)//3:
    diffs.append("Holistic transformation bundles for Tier-2/Tier-3 SMEs (strategy + process + analytics).")
else:
    diffs.append("Sector playbooks with KPI blueprints for rapid rollout.")

st.markdown("**Strategy Recommendations**")
st.success("\n".join([f"• {d}" for d in diffs]))
st.markdown('</div>', unsafe_allow_html=True)

# ==================== 6) EXPORT ====================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="h3">6) Export for Annexure</div>', unsafe_allow_html=True)
csv_data = edited.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download Current Data (CSV)", data=csv_data, file_name="firms_clean.csv", mime="text/csv")
st.markdown('</div>', unsafe_allow_html=True)
