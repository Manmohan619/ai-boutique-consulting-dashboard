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

# ==================== 1) ABOUT ====================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="h3">1) About this Dashboard</div>', unsafe_allow_html=True)
with st.expander("📘 What this dashboard does & how to read the scores"):
    st.markdown("""
This tool benchmarks consulting firms along:
- **Value Proposition** (Cost → Innovation)
- **Nature of Offering** (Functional → Holistic)
- **SME Focus**

Use it to:
- Upload/add firms
- Score them 1–10
- Visualize strategic positions
- Identify SME white-space opportunities

| Scale (1–10) | Meaning |
|---|---|
| **1–3** | Low maturity / narrow scope |
| **4–6** | Mid / balanced |
| **7–10** | High maturity / deep focus |

Bubble size & color = **SME Focus**
""")
st.markdown('</div>', unsafe_allow_html=True)

# ========== HELPERS ==========
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
    if score >= 7.5: return "Very high opportunity"
    elif score >= 6.0: return "High opportunity"
    elif score >= 4.5: return "Moderate"
    else: return "Low"

# ==================== 2) IMPORT DATA ====================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="h3">2) Import Data</div>', unsafe_allow_html=True)

default = pd.read_csv("firms.csv")
uploaded = st.file_uploader("Upload firms.csv (optional)", type=["csv"])
base_df = pd.read_csv(uploaded) if uploaded else default.copy()
for c in ["Firm","Offering_Nature","Value_Proposition","SME_Focus"]:
    if c not in base_df.columns:
        base_df[c] = 5 if c!="Firm" else ""

if "df" not in st.session_state:
    st.session_state.df = base_df.copy()

if st.button("Reset to Imported Data"):
    st.session_state.df = base_df.copy()
    st.success("Reset complete")
st.markdown('</div>', unsafe_allow_html=True)

# ==================== 3) MANAGE FIRMS ====================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="h3">3) Manage Firms</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns([0.32,0.18,0.18,0.18,0.14])
name = c1.text_input("Firm name")
on = c2.slider("Offering_Nature",1,10,6)
vp = c3.slider("Value_Proposition",1,10,6)
sme = c4.slider("SME_Focus",1,10,6)

if c5.button("Add firm"):
    if name:
        st.session_state.df = pd.concat(
            [st.session_state.df, pd.DataFrame([{"Firm":name,"Offering_Nature":on,"Value_Proposition":vp,"SME_Focus":sme}])],
            ignore_index=True
        )
        st.success(f"Added: {name}")
    else: st.error("Enter firm name")

del_sel = st.multiselect("Delete firms", st.session_state.df["Firm"])
if st.button("Delete selected"):
    st.session_state.df = st.session_state.df[~st.session_state.df["Firm"].isin(del_sel)]
    st.success("Deleted")
st.markdown('</div>', unsafe_allow_html=True)

# ==================== 4) EDIT SCORES ====================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="h3">4) Edit Scores</div>', unsafe_allow_html=True)

if "uid" not in st.session_state.df.columns:
    st.session_state.df["uid"] = [
        f'{i}_{str(r["Firm"]).strip().lower().replace(" ", "_") or "blank"}'
        for i, r in st.session_state.df.reset_index().iterrows()
    ]

for i,row in st.session_state.df.iterrows():
    st.write(f"**{row['Firm']}**")
    uid=row['uid']
    c1,c2,c3,_=st.columns([0.34,0.22,0.22,0.22])
    nm=c1.text_input("Firm",row["Firm"],key=f"n{uid}")
    onv=c2.slider("Offering_Nature",1,10,int(row["Offering_Nature"]),key=f"o{uid}")
    vpv=c3.slider("Value_Proposition",1,10,int(row["Value_Proposition"]),key=f"v{uid}")
    smev=_ .slider("SME_Focus",1,10,int(row["SME_Focus"]),key=f"s{uid}")
    st.session_state.df.loc[i]=[nm,onv,vpv,smev,uid]

edited=st.session_state.df.copy()
edited["AI_Explanation"]=[explain_row(r["Offering_Nature"],r["Value_Proposition"],r["SME_Focus"]) for _,r in edited.iterrows()]
st.markdown('</div>', unsafe_allow_html=True)

# ==================== 5) COMPETITOR MAP ====================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="h3">5) Competitor Map</div>', unsafe_allow_html=True)
show_lbl=st.checkbox("Show firm labels",True)

fig=px.scatter(
    edited,x="Offering_Nature",y="Value_Proposition",
    size="SME_Focus",color="SME_Focus",text="Firm" if show_lbl else None,
    template="plotly_white",color_continuous_scale=px.colors.sequential.Viridis,
    hover_data=["AI_Explanation"]
)

fig.layout.plot_bgcolor="#fff"
tick_vals=list(range(1,11))

fig.update_xaxes(
    title="Nature of Offering (Functional → Holistic)",title_font=dict(color="white",size=14),
    tickvals=tick_vals,ticklabelposition="inside",ticks="inside",tickcolor="#000",tickfont=dict(color="#000"),
    showgrid=True,gridcolor="#e6e9ef",showline=True,linecolor="#000",mirror=True,range=[0.5,10.5],title_standoff=22
)

fig.update_yaxes(
    title="Value Proposition (Cost → Innovation)",title_font=dict(color="white",size=14),
    tickvals=tick_vals,ticklabelposition="inside",ticks="inside",tickcolor="#000",tickfont=dict(color="#000"),
    showgrid=True,gridcolor="#e6e9ef",showline=True,linecolor="#000",mirror=True,range=[0.5,10.5],title_standoff=22
)

fig.update_traces(textposition="top center" if show_lbl else None,marker=dict(line=dict(width=2,color="#111")))

fig.update_layout(
    height=560,margin=dict(l=110,r=140,t=50,b=110),
    coloraxis_colorbar=dict(title="SME_Focus",bgcolor="white",outlinecolor="#ddd")
)

st.markdown('<div class="plot-card">', unsafe_allow_html=True)
st.plotly_chart(fig,use_container_width=True,theme=None)
st.markdown('</div>', unsafe_allow_html=True)

# ==================== 6) WHITE-SPACE ====================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="h3">6) White-Space Analysis & Strategy</div>', unsafe_allow_html=True)

edited["White_Space_Score"]=(edited["Offering_Nature"]+edited["Value_Proposition"])/2-(10-edited["SME_Focus"])*0.1
edited["WS_Interpretation"]=edited["White_Space_Score"].apply(ws_interpretation)

st.dataframe(edited.sort_values("White_Space_Score",ascending=False),use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==================== 7) EXPORT DATA ====================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="h3">7) Export Data</div>', unsafe_allow_html=True)

csv=edited.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download CSV",csv,file_name="firms_clean.csv")
st.markdown('</div>', unsafe_allow_html=True)
