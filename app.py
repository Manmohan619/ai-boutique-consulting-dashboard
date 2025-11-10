import streamlit as st
import pandas as pd
import plotly.express as px

# ==================== PAGE CONFIG ====================
st.set_page_config(page_title="AI Dashboard | Boutique Consulting (India, SMEs)", layout="wide")

# ==================== GLOBAL STYLES ====================
st.markdown("""
<style>
.top-banner{
  background: linear-gradient(90deg,#0f766e 0%,#2563eb 100%);
  color:#fff; padding:18px 22px; border-radius:14px; margin-bottom:16px;
  box-shadow:0 8px 22px rgba(0,0,0,.10)
}
.top-banner .title{font-size:24px;font-weight:800;letter-spacing:.3px}
.top-banner .meta{font-size:14px;opacity:.98;margin-top:6px}

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

.stDownloadButton button,.stButton>button{
  background:#0f766e !important; color:#fff !important; border-radius:10px !important; font-weight:700 !important
}
.stDownloadButton button:hover,.stButton>button:hover{background:#115e59 !important}
.stDataFrame{border:1px solid #e5e7eb;border-radius:10px}
.block-container > div:empty{display:none}

/* Chart wrapper (white, rounded) */
.plot-card{
  border:1px solid #e5e7eb;
  border-radius:12px;
  background:#ffffff;
  padding:8px 10px 6px 10px;
  margin:0;
  overflow:visible;
}
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

with st.container():  # keeps widget layout stable; avoids orphan artifacts
    # stable uid for keys (prevents the "white ribbon" ghost slider)
    if "uid" not in st.session_state.df.columns:
        st.session_state.df["uid"] = [
            f'{i}_{str(r["Firm"]).strip().lower().replace(" ", "_") or "blank"}'
            for i, r in st.session_state.df.reset_index().iterrows()
        ]

    for i in range(len(st.session_state.df)):
        row = st.session_state.df.loc[i]
        title = row['Firm'] if row['Firm'] else f'Firm {i+1}'
        st.write(f"**{title}**")

        uid = row["uid"]
        cols = st.columns([0.34, 0.22, 0.22, 0.22])
        name = cols[0].text_input("Firm", value=str(row["Firm"]), key=f"name_{uid}")
        on   = cols[1].slider("Offering_Nature", 1, 10, int(row["Offering_Nature"]), key=f"on_{uid}")
        vp   = cols[2].slider("Value_Proposition", 1, 10, int(row["Value_Proposition"]), key=f"vp_{uid}")
        sme  = cols[3].slider("SME_Focus", 1, 10, int(row["SME_Focus"]), key=f"sme_{uid}")

        st.session_state.df.loc[i, ["Firm","Offering_Nature","Value_Proposition","SME_Focus"]] = [name, on, vp, sme]
st.markdown('</div>', unsafe_allow_html=True)

# Snapshot for plots/tables
edited = st.session_state.df.copy()
edited["AI_Explanation"] = [
    explain_row(float(r["Offering_Nature"]), float(r["Value_Proposition"]), float(r["SME_Focus"]))
    for _, r in edited.iterrows()
]

# ==================== 4) COMPETITOR MAP ====================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="h3">4) Competitor Map (Professional Plot + In-Plot Axis Titles)</div>', unsafe_allow_html=True)
show_labels = st.checkbox("Show firm labels on chart", value=True)

fig = px.scatter(
    edited,
    x="Offering_Nature", y="Value_Proposition",
    size="SME_Focus", color="SME_Focus",
    text="Firm" if show_labels else None,
    color_continuous_scale=px.colors.sequential.Viridis,
    hover_data=["AI_Explanation"],
    template="plotly_white",
)

# --- White plot area, transparent paper ---
fig.layout.plot_bgcolor = "#ffffff"
fig.layout.paper_bgcolor = "rgba(0,0,0,0)"

# --- Axes: keep numbers visible and dark ---
fig.update_xaxes(
    title_text=None,
    range=[0.5, 10.5],
    showgrid=True, gridcolor="#e6e9ef",
    zeroline=False, showline=True, linecolor="#111", linewidth=1.1,
    ticks="outside", ticklen=6, tickcolor="#111",
    tickmode="linear", tick0=1, dtick=1,
    showticklabels=True, tickfont=dict(color="#111", size=12, family="Inter, Arial, sans-serif"),
)
fig.update_yaxes(
    title_text=None,
    range=[0.5, 10.5],
    showgrid=True, gridcolor="#e6e9ef",
    zeroline=False, showline=True, linecolor="#111", linewidth=1.1,
    ticks="outside", ticklen=6, tickcolor="#111",
    tickmode="linear", tick0=1, dtick=1,
    showticklabels=True, tickfont=dict(color="#111", size=12, family="Inter, Arial, sans-serif"),
)

# --- Bubble styling ---
if show_labels:
    fig.update_traces(textposition="top center", textfont=dict(color="#111", size=12))
fig.update_traces(marker=dict(line=dict(width=2, color="#111")), cliponaxis=False)

# --- In-plot axis titles (precise anchors; won’t cover ticks) ---
fig.update_layout(
    height=560,
    margin=dict(l=80, r=140, t=50, b=80),
    font=dict(family="Inter, Arial, sans-serif"),
    coloraxis_colorbar=dict(
        title=dict(text="SME_Focus", font=dict(color="#111", size=12)),
        tickfont=dict(color="#111", size=11),
        x=1.01, xanchor="left", y=0.5, yanchor="middle",
        len=0.90, thickness=12,
        bgcolor="rgba(255,255,255,0.9)",
        outlinecolor="#d1d5db", outlinewidth=1
    ),
    annotations=[
        dict(
            text="Nature of Offering (Functional → Holistic)",
            x=0.5, y=0.06, xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=14, color="#111", family="Arial Black"),
            xanchor="center", yanchor="bottom"
        ),
        dict(
            text="Value Proposition (Cost → Innovation)",
            x=0.06, y=0.5, xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=14, color="#111", family="Arial Black"),
            xanchor="left", yanchor="middle",
            textangle=-90
        ),
    ],
)

# --- Render full-width; disable Streamlit theming so our colors win ---
st.markdown('<div class="plot-card">', unsafe_allow_html=True)
st.plotly_chart(
    fig,
    use_container_width=True,
    theme=None,  # ← important: prevents Streamlit dark theme from turning tick labels white
    config={"displaylogo": False,
            "toImageButtonOptions": {"format":"png","filename":"competitor_map","height":560,"width":1200}}
)
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
    edited[["Firm","Offering_Nature","Value_Proposition","SME_Focus","AI_Explanation","White_Space_Score","WS_Interpretation"]]
        .sort_values("White_Space_Score", ascending=False),
    use_container_width=True, height=tbl_height
)

# Simple strategy hints
x_mean = float(edited["Offering_Nature"].mean())
y_mean = float(edited["Value_Proposition"].mean())
sme_mean = float(edited["SME_Focus"].mean())

diffs = []
if (edited["Value_Proposition"] > y_mean).sum() >= len(edited)//2 and (edited["SME_Focus"] < sme_mean).sum() >= len(edited)//3:
    diffs.append("Outcome-linked pricing for SMEs (fees tied to realized improvements).")
else:
    diffs.append("AI-enabled SME Strategy Studio (diagnostics + simulation).")
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
