"""
NIIMBL Bioreactor Digital Twin GUI
Run: streamlit run app.py
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import io
from datetime import datetime

# ── Page config (must be first) ──────────────────────────────────────────────
st.set_page_config(
    page_title="NIIMBL · Bioreactor Digital Twin",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

  :root {
    --teal:      #0A7A6E;
    --teal-lt:   #12A896;
    --navy:      #0D2137;
    --slate:     #2C4A5A;
    --cream:     #F4F7F6;
    --accent:    #E8F4F2;
    --warn:      #D4713A;
    --border:    #C8DAD7;
    --muted:     #6B8A85;
  }

  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

  /* sidebar */
  [data-testid="stSidebar"] {
    background: var(--navy) !important;
    border-right: 2px solid var(--teal);
  }
  [data-testid="stSidebar"] * { color: #DDE9E7 !important; }
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stNumberInput label,
  [data-testid="stSidebar"] .stTextInput label,
  [data-testid="stSidebar"] .stFileUploader label { color: #223C4E !important; font-size: 0.78rem !important; letter-spacing: 0.04em; text-transform: uppercase; }
  [data-testid="stSidebar"] h1 { font-family: 'DM Serif Display', serif; color: #E8F4F2 !important; font-size: 1.4rem !important; }
  [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: var(--teal-lt) !important; }
  [data-testid="stSidebar"] .stExpander { border: 1px solid #1E3A4A !important; border-radius: 6px; margin-bottom: 8px; }
  [data-testid="stSidebar"] [data-testid="stExpanderToggle"] { color: #A8C8C3 !important; }

  [data-testid="stSidebar"] [data-baseweb="select"] > div,
  [data-testid="stSidebar"] [data-baseweb="input"],
  [data-testid="stSidebar"] [data-baseweb="stNumberInput"] input { background-color: #0D2137 !important; border-color: #C8DAD7 !important; color: #0D2137 !important; }
  [data-testid="stSidebar"] [data-baseweb="select"] span,
  [data-testid="stSidebar"] [data-baseweb="select"] div[class*="ValueContainer"] {color: #0D2137 !important; }
  [data-testid="stSidebar"] input[type="number"] { background color: #DDE9E7 !important; color: #DDE9E7 !important; }
  [data-testid="stSidebar"] [data-baseweb="select"] svg { fill: #83848c !important; }
  [data-testid="stSidebar"] [data-baseweb="stNumberInput"] button { background-color: #0D2137 !important; border-color: #C8DAD7 !important; color: #0D2137 !important; }

  /* main area */
  .main { background: var(--cream); }
  .block-container { padding: 2rem 2.5rem !important; }

  /* page title */
  .page-header {
    background: linear-gradient(135deg, var(--navy) 0%, var(--slate) 100%);
    border-radius: 12px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    display: flex; align-items: center; gap: 1.5rem;
    border-left: 5px solid var(--teal-lt);
  }
  .page-header h1 { font-family: 'DM Serif Display', serif; color: #E8F4F2; font-size: 2rem; margin: 0; }
  .page-header p  { color: #8DAEB0; font-size: 0.9rem; margin: 0.3rem 0 0; }

  /* metric cards */
  .metric-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    border-top: 3px solid var(--teal);
  }
  .metric-card .label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); }
  .metric-card .value { font-family: 'JetBrains Mono', monospace; font-size: 1.7rem; color: var(--navy); font-weight: 500; }
  .metric-card .unit  { font-size: 0.78rem; color: var(--muted); }

  /* section headers */
  .section-title {
    font-family: 'DM Serif Display', serif;
    color: var(--navy);
    font-size: 1.25rem;
    border-bottom: 2px solid var(--teal);
    padding-bottom: 0.3rem;
    margin-bottom: 1rem;
  }

  /* placeholder banner */
  .placeholder-banner {
    background: #FFF8F0;
    border: 1.5px dashed var(--warn);
    border-radius: 8px;
    padding: 0.8rem 1.2rem;
    font-size: 0.82rem;
    color: var(--warn);
    margin-bottom: 1rem;
  }

  /* status badges */
  .badge { display: inline-block; border-radius: 20px; padding: 2px 10px; font-size: 0.72rem; font-weight: 600; }
  .badge-ok    { background: #E0F5F0; color: #0A7A6E; }
  .badge-warn  { background: #FFF0E0; color: #D4713A; }
  .badge-info  { background: #E0EEFF; color: #2460A7; }

  /* run button */
  .stButton > button {
    background: linear-gradient(135deg, var(--teal) 0%, var(--teal-lt) 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    padding: 0.6rem 2rem !important;
    transition: opacity 0.2s !important;
  }
  .stButton > button:hover { opacity: 0.85 !important; }

  /* tab styling */
  .stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 2px solid var(--border); }
  .stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    color: var(--slate);
    border-radius: 6px 6px 0 0;
    padding: 0.5rem 1.2rem;
  }
  .stTabs [aria-selected="true"] { background: var(--teal) !important; color: white !important; }

  /* dataframe */
  .stDataFrame { border-radius: 8px; overflow: hidden; }

  /* footer */
  .footer { text-align: center; color: var(--muted); font-size: 0.75rem; margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--border); }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  SIDEBAR  — all inputs
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🧬 NIIMBL Digital Twin")
    st.caption("Bioreactor Simulation · v1.0")
    st.divider()

    # ── 1. Reactor Mode ──────────────────────────────────
    with st.expander("① Reactor Mode", expanded=True):
        reactor_type = st.selectbox(
            "Reactor type",
            ["Stirred Tank Reactor (STR)", "Single-use STR", "Plug Flow Reactor (PFR)", "Custom"],
        )
        culture_mode = st.selectbox(
            "Culture mode",
            ["Fed-batch", "Perfusion", "Batch"],
        )
        cell_type = st.selectbox(
            "Cell type",
            ["CHO (Chinese Hamster Ovary)", "HEK 293", "NS0", "Vero", "Custom"],
        )

    # ── 2. Tank Geometry ─────────────────────────────────
    with st.expander("② Tank Geometry", expanded=False):
        tank_height = st.number_input("Tank height (m)", min_value=0.1, value=3.5, step=0.1, format="%.2f")
        tank_diameter = st.number_input("Inner diameter (m)", min_value=0.1, value=1.5, step=0.1, format="%.2f")
        n_baffles = st.number_input("No. of baffles", min_value=0, value=4, step=1)
        baffle_width = st.number_input("Baffle width (m)", min_value=0.0, value=0.15, step=0.01, format="%.3f")

    # ── 3. Impeller ───────────────────────────────────────
    with st.expander("③ Impeller", expanded=False):
        impeller_diameter = st.number_input("Impeller diameter (m)", min_value=0.05, value=0.6, step=0.05, format="%.2f")
        n_impellers = st.number_input("No. of impellers", min_value=1, value=2, step=1)
        impeller_position = st.number_input("Impeller position – z (m)", min_value=0.0, value=0.5, step=0.05, format="%.2f")
        power_number = st.number_input("Power number (Np)", min_value=0.1, value=5.0, step=0.1, format="%.1f")
        agitation_rpm = st.number_input("Agitation speed (rpm)", min_value=0.0, value=80.0, step=5.0)

    # ── 4. Sparger ────────────────────────────────────────
    with st.expander("④ Sparger", expanded=False):
        sparger_diameter = st.number_input("Sparger diameter (m)", min_value=0.01, value=0.1, step=0.01, format="%.3f")
        air_flow_vvm = st.number_input("Air flow rate (vvm)", min_value=0.0, value=0.1, step=0.01, format="%.3f")

    # ── 5. Process Conditions ─────────────────────────────
    with st.expander("⑤ Process Conditions", expanded=False):
        working_volume = st.number_input("Working volume (m³)", min_value=0.001, value=2.0, step=0.1, format="%.3f")
        total_volume = st.number_input("Total reactor volume (m³)", min_value=0.001, value=2.5, step=0.1, format="%.3f")
        DO_setpoint = st.number_input("DO setpoint (% sat)", min_value=0.0, max_value=100.0, value=40.0, step=5.0)
        pH_setpoint = st.number_input("pH setpoint", min_value=6.0, max_value=8.0, value=7.0, step=0.05, format="%.2f")
        temperature_C = st.number_input("Temperature (°C)", min_value=20.0, max_value=40.0, value=37.0, step=0.5)
        start_vol_frac = st.slider("Starting volume fraction (%)", 0, 100, 30)
        end_vol_frac = st.slider("End volume fraction (%)", 0, 100, 80)

    # ── 6. Cell & Media Specs ─────────────────────────────
    with st.expander("⑥ Cell & Media Specs", expanded=False):
        molar_volume_pg = st.number_input("Molar volume (pg/cell)", min_value=0.0, value=2.0, step=0.1)
        number_density = st.number_input("Number density (mol/m³)", min_value=0.0, value=1e6, step=1e5, format="%.0f")
        media_viscosity = st.number_input("Media viscosity (mPa·s)", min_value=0.1, value=1.0, step=0.1)
        pluronic_present = st.checkbox("Pluronic present?", value=False)
        antifoam_present = st.checkbox("Antifoam present?", value=True)
        st.caption("Upload cell-specific parameters:")
        cell_params_file = st.file_uploader("Cell params (.xlsx)", type=["xlsx"], key="cell_params")
        media_comp_file = st.file_uploader("Media composition (.xlsx)", type=["xlsx"], key="media_comp")

    # ── 7. Simulation Settings ────────────────────────────
    with st.expander("⑦ Simulation Settings", expanded=False):
        total_time_hr = st.number_input("Total simulation time (hr)", min_value=1.0, value=240.0, step=12.0)
        dt_hr = st.number_input("Time step (hr)", min_value=0.05, value=1.0, step=0.25)
        n_compartments = st.number_input("Number of compartments", min_value=1, value=50, step=5)
        hydrodynamics_src = st.selectbox(
            "Hydrodynamics data source",
            ["Upload CFD output (.xlsx)", "Use placeholder (demo)", "Connect OSU CFD outputs"],
        )
        if hydrodynamics_src == "Upload CFD output (.xlsx)":
            cfd_file = st.file_uploader("CFD data (.xlsx)", type=["xlsx"], key="cfd")
        sensitivity_analysis = st.checkbox("Enable sensitivity analysis", value=False)

    st.divider()
    run_sim = st.button("▶  Run Simulation", use_container_width=True)

# ══════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════
st.markdown("""
<div class="page-header">
  <div>
    <h1>Bioreactor Digital Twin</h1>
    <p>NIIMBL · Compartment Model · Hydrodynamics · Cell Kinetics · Glycosylation</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════
tab_overview, tab_hydro, tab_kinetics, tab_glyco, tab_zones, tab_sensitivity, tab_export = st.tabs([
    "📊 Overview",
    "🌊 Hydrodynamics",
    "🔬 Cell Kinetics",
    "🧪 Glycosylation",
    "🗺️ Zone Analysis",
    "📈 Sensitivity",
    "📄 Export",
])

# ══════════════════════════════════════════════════════════
#  BACKEND / PLACEHOLDER CALCULATIONS
#  ─────────────────────────────────────────────────────────
#  ⚠️  PLACEHOLDER ZONE — replace functions below with real
#      data lookups / your compartment model calls once the
#      CFD database is ready.
# ══════════════════════════════════════════════════════════

def compute_derived_params(agitation_rpm, impeller_diameter, power_number,
                           working_volume, temperature_C, air_flow_vvm,
                           n_compartments, total_time_hr, dt_hr):
    """
    PLACEHOLDER: returns derived hydrodynamic & process KPIs.
    Replace with actual database lookup + compartment model when CFD data is available.
    File naming convention: {reactor_geometry}_{working_volume}_{agitation_speed}_{sparging_rate}.xlsx
    """
    omega = agitation_rpm / 60  # rev/s
    rho = 1000  # kg/m³ water approximation
    mu = 1e-3   # Pa·s

    # Power input (W)
    P = power_number * rho * (omega ** 3) * (impeller_diameter ** 5)
    P_per_V = P / working_volume  # W/m³

    # Mixing time estimate (Nienow correlation placeholder)
    Re_imp = rho * omega * (impeller_diameter ** 2) / mu
    mixing_time_s = max(5.0, 5000 / Re_imp * 60)  # very rough placeholder

    # Tip speed
    tip_speed = np.pi * impeller_diameter * omega  # m/s

    # Kolmogorov length scale
    epsilon = P_per_V / rho  # m²/s³ (energy dissipation rate)
    nu = mu / rho
    eta = (nu ** 3 / max(epsilon, 1e-9)) ** 0.25 * 1e6  # μm

    # kLa estimate (van't Riet correlation placeholder)
    Vs = air_flow_vvm * working_volume / 60  # superficial gas velocity proxy
    kLa = 0.026 * (P_per_V ** 0.4) * (Vs ** 0.5)  # s⁻¹ placeholder

    return {
        "power_input_W": round(P, 1),
        "P_per_V": round(P_per_V, 1),
        "mixing_time_s": round(mixing_time_s, 1),
        "tip_speed_m_s": round(tip_speed, 3),
        "kolmogorov_um": round(eta, 2),
        "kLa_per_hr": round(kLa * 3600, 3),
        "Re_imp": round(Re_imp, 0),
    }


def simulate_time_profiles(total_time_hr, dt_hr, DO_setpoint, temperature_C, n_compartments):
    """
    PLACEHOLDER: generates synthetic time-series for all output variables.
    Replace with compartment model solver once database + kinetics equations are supplied.
    """
    t = np.arange(0, total_time_hr + dt_hr, dt_hr)
    np.random.seed(42)
    noise = lambda s: np.random.normal(0, s, len(t))

    # Cell growth (logistic)
    mu_max = 0.04  # hr⁻¹ placeholder
    K = 20e6       # max cell density cells/mL
    X0 = 0.5e6
    X = K / (1 + (K / X0 - 1) * np.exp(-mu_max * t)) + noise(0.3e5)

    # Viability (sigmoidal decline after peak)
    viab = 100 / (1 + np.exp(0.04 * (t - 0.75 * total_time_hr))) + noise(0.5)

    # Substrate (glucose, exponential depletion + feeding in fed-batch)
    glc = 25 * np.exp(-0.008 * t) + 5 * np.sin(t / 40) + noise(0.3)
    glc = np.clip(glc, 0.5, 30)

    # Lactate accumulation
    lac = 3 + 0.05 * t + noise(0.2)
    lac = np.clip(lac, 0, 8)

    # DO profile
    DO = DO_setpoint + 5 * np.sin(t / 30) + noise(2)
    DO = np.clip(DO, 0, 100)

    # pH profile
    pH = pH_setpoint + 0.05 * np.sin(t / 20) + noise(0.02)

    # Titer (product concentration)
    titer = 0.5 * (1 - np.exp(-0.015 * t)) * 5000 + noise(20)

    return pd.DataFrame({
        "time_hr": t,
        "cell_density_e6_cells_mL": X / 1e6,
        "viability_pct": viab,
        "glucose_mM": glc,
        "lactate_mM": lac,
        "DO_pct": DO,
        "pH": pH,
        "titer_mg_L": titer,
    })


def simulate_velocity_field(n_compartments):
    """
    PLACEHOLDER: synthetic velocity field for the reactor cross-section.
    Replace with CFD-derived velocity matrix (from .xlsx database file).
    """
    z = np.linspace(0, 1, n_compartments)
    r = np.linspace(0, 1, 20)
    Z, R = np.meshgrid(z, r)
    # Synthetic swirling flow
    U = np.sin(np.pi * R) * np.cos(2 * np.pi * Z) * 0.3
    V = -np.cos(np.pi * R) * np.sin(np.pi * Z) * 0.2
    speed = np.sqrt(U**2 + V**2)
    return Z, R, U, V, speed


def simulate_glycosylation(total_time_hr, dt_hr):
    """
    PLACEHOLDER: synthetic glycan profile over time.
    Replace with glycosylation kinetics module outputs.
    """
    t = np.arange(0, total_time_hr + dt_hr, dt_hr)
    np.random.seed(7)
    noise = lambda s: np.random.normal(0, s, len(t))

    # Glycan species fractions (sum to ~100%)
    G0F  = 30 + 0.05 * t + noise(1.5)
    G1F  = 25 - 0.03 * t + noise(1.2)
    G2F  = 15 + 0.02 * t + noise(0.8)
    Man5 = 10 - 0.01 * t + noise(0.5)
    other = 100 - G0F - G1F - G2F - Man5

    return pd.DataFrame({
        "time_hr": t,
        "G0F_pct": np.clip(G0F, 0, 100),
        "G1F_pct": np.clip(G1F, 0, 100),
        "G2F_pct": np.clip(G2F, 0, 100),
        "Man5_pct": np.clip(Man5, 0, 100),
        "Other_pct": np.clip(other, 0, 100),
    })


def classify_zones(n_compartments, P_per_V):
    """
    PLACEHOLDER: classifies compartments into well-mixed, transition, and stagnant zones.
    Replace with RTD (residence time distribution) analysis from compartment model.
    """
    np.random.seed(21)
    zones = []
    for i in range(n_compartments):
        pos = i / n_compartments
        local_P = P_per_V * (1 - 0.6 * abs(pos - 0.3)) + np.random.uniform(-20, 20)
        DO_local = DO_setpoint * (0.8 + 0.4 * np.random.rand())
        if local_P > P_per_V * 0.7:
            zone_type = "Well-mixed"
        elif local_P > P_per_V * 0.3:
            zone_type = "Transition"
        else:
            zone_type = "Stagnant / Anaerobic"
        rt = np.random.exponential(total_time_hr / n_compartments)
        zones.append({
            "compartment": i + 1,
            "zone_type": zone_type,
            "local_power_W_m3": round(local_P, 1),
            "local_DO_pct": round(DO_local, 1),
            "residence_time_hr": round(rt, 2),
        })
    return pd.DataFrame(zones)


# ══════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════
if "results_ready" not in st.session_state:
    st.session_state.results_ready = False

if run_sim:
    with st.spinner("Running simulation…"):
        kpis = compute_derived_params(
            agitation_rpm, impeller_diameter, power_number,
            working_volume, temperature_C, air_flow_vvm,
            n_compartments, total_time_hr, dt_hr,
        )
        df_time = simulate_time_profiles(total_time_hr, dt_hr, DO_setpoint, temperature_C, n_compartments)
        df_glyco = simulate_glycosylation(total_time_hr, dt_hr)
        df_zones = classify_zones(n_compartments, kpis["P_per_V"])
        Z, R, U, V, speed = simulate_velocity_field(n_compartments)

        st.session_state.results_ready = True
        st.session_state.kpis      = kpis
        st.session_state.df_time   = df_time
        st.session_state.df_glyco  = df_glyco
        st.session_state.df_zones  = df_zones
        st.session_state.vel       = (Z, R, U, V, speed)
        st.session_state.run_params = dict(
            reactor_type=reactor_type, culture_mode=culture_mode,
            cell_type=cell_type, agitation_rpm=agitation_rpm,
            working_volume=working_volume, DO_setpoint=DO_setpoint,
            pH_setpoint=pH_setpoint, temperature_C=temperature_C,
            total_time_hr=total_time_hr, n_compartments=n_compartments,
        )

COLORS = {
    "Well-mixed":          "#12A896",
    "Transition":          "#F0A832",
    "Stagnant / Anaerobic": "#D44B2A",
}

# ══════════════════════════════════════════════════════════
#  TAB 0 — OVERVIEW
# ══════════════════════════════════════════════════════════
with tab_overview:
    st.markdown('<p class="section-title">Simulation Overview</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="placeholder-banner">
      ⚠️  <strong>Demo Mode</strong>  — All outputs are generated from placeholder calculations.
      Once your CFD database is ready, replace the functions in <code>backend.py</code> with real lookups.
      File naming convention: <code>{reactor_geometry}_{working_volume_m3}_{agitation_rpm}_{sparging_vvm}.xlsx</code>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.results_ready:
        st.info("👈  Configure parameters in the sidebar and click **▶ Run Simulation** to begin.")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **What this GUI simulates:**
            - Hydrodynamics (velocity field, mixing zones, power input)
            - Cell kinetics (growth, viability, substrate, titer)
            - Glycosylation profiles (G0F, G1F, G2F, Man5)
            - Zone classification (well-mixed, transition, stagnant/anaerobic)
            - Residence time distributions
            """)
        with col2:
            st.markdown("""
            **Inputs accepted:**
            - Reactor geometry (tank, impeller, sparger)
            - Operating conditions (DO, pH, temperature, rpm)
            - CFD outputs from COMSOL (.xlsx upload)
            - Cell & media specifications
            """)
    else:
        kpis = st.session_state.kpis
        p = st.session_state.run_params

        # KPI row
        cols = st.columns(4)
        cards = [
            ("Power input", f"{kpis['power_input_W']:.0f}", "W"),
            ("P/V", f"{kpis['P_per_V']:.1f}", "W/m³"),
            ("Mixing time", f"{kpis['mixing_time_s']:.0f}", "s"),
            ("kLa", f"{kpis['kLa_per_hr']:.3f}", "hr⁻¹"),
        ]
        for col, (label, val, unit) in zip(cols, cards):
            with col:
                st.markdown(f"""
                <div class="metric-card">
                  <div class="label">{label}</div>
                  <div class="value">{val}</div>
                  <div class="unit">{unit}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        cols2 = st.columns(4)
        cards2 = [
            ("Tip speed", f"{kpis['tip_speed_m_s']:.3f}", "m/s"),
            ("Kolmogorov scale", f"{kpis['kolmogorov_um']:.1f}", "μm"),
            ("Impeller Re", f"{kpis['Re_imp']:,.0f}", "—"),
            ("Compartments", f"{p['n_compartments']}", "zones"),
        ]
        for col, (label, val, unit) in zip(cols2, cards2):
            with col:
                st.markdown(f"""
                <div class="metric-card">
                  <div class="label">{label}</div>
                  <div class="value">{val}</div>
                  <div class="unit">{unit}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Quick-look: final cell density & titer
        df = st.session_state.df_time
        final = df.iloc[-1]
        st.markdown('<p class="section-title">Run Summary</p>', unsafe_allow_html=True)
        sumcols = st.columns(5)
        summary_items = [
            ("Peak cell density", f"{df['cell_density_e6_cells_mL'].max():.2f}", "×10⁶ cells/mL"),
            ("Final titer", f"{final['titer_mg_L']:.0f}", "mg/L"),
            ("Final viability", f"{final['viability_pct']:.1f}", "%"),
            ("Avg DO", f"{df['DO_pct'].mean():.1f}", "%"),
            ("Avg glucose", f"{df['glucose_mM'].mean():.1f}", "mM"),
        ]
        for col, (label, val, unit) in zip(sumcols, summary_items):
            with col:
                st.markdown(f"""
                <div class="metric-card">
                  <div class="label">{label}</div>
                  <div class="value">{val}</div>
                  <div class="unit">{unit}</div>
                </div>""", unsafe_allow_html=True)

        # Zone summary pie
        st.markdown("<br>", unsafe_allow_html=True)
        df_z = st.session_state.df_zones
        zone_counts = df_z["zone_type"].value_counts().reset_index()
        zone_counts.columns = ["Zone", "Count"]
        fig_pie = px.pie(
            zone_counts, names="Zone", values="Count",
            color="Zone",
            color_discrete_map=COLORS,
            title="Zone distribution",
            hole=0.4,
        )
        fig_pie.update_layout(
            font_family="DM Sans",
            paper_bgcolor="white",
            plot_bgcolor="white",
            legend_title_text="",
            margin=dict(t=50, b=20),
        )
        st.plotly_chart(fig_pie, use_container_width=True)


# ══════════════════════════════════════════════════════════
#  TAB 1 — HYDRODYNAMICS
# ══════════════════════════════════════════════════════════
with tab_hydro:
    st.markdown('<p class="section-title">Hydrodynamics</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="placeholder-banner">
      ⚠️  Velocity field is a synthetic placeholder. Replace <code>simulate_velocity_field()</code> in
      <code>backend.py</code> with the CFD-derived matrix from your COMSOL .xlsx files.
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.results_ready:
        st.info("Run the simulation first.")
    else:
        Z, R, U, V, speed = st.session_state.vel
        n_c = st.session_state.run_params["n_compartments"]

        fig_vel = go.Figure()
        fig_vel.add_trace(go.Heatmap(
            z=speed,
            colorscale="Teal",
            colorbar=dict(title="Speed (m/s)"),
            showscale=True,
        ))
        fig_vel.add_trace(go.Cone(
            x=(Z * n_c).flatten()[::10],
            y=(R * 20).flatten()[::10],
            z=[0] * len(Z.flatten()[::10]),
            u=U.flatten()[::10],
            v=V.flatten()[::10],
            w=[0] * len(U.flatten()[::10]),
            colorscale="RdBu",
            showscale=False,
            sizemode="scaled",
            sizeref=0.5,
        ))
        fig_vel.update_layout(
            title="Velocity Field — Reactor Cross-Section (placeholder)",
            font_family="DM Sans",
            paper_bgcolor="white",
            plot_bgcolor="#F8FBFA",
            xaxis_title="Axial compartment",
            yaxis_title="Radial position",
            height=420,
        )
        st.plotly_chart(fig_vel, use_container_width=True)

        # RTD placeholder
        st.markdown('<p class="section-title">Residence Time Distribution</p>', unsafe_allow_html=True)
        df_z = st.session_state.df_zones
        fig_rtd = px.histogram(
            df_z, x="residence_time_hr", color="zone_type",
            color_discrete_map=COLORS,
            nbins=20, barmode="overlay",
            labels={"residence_time_hr": "Residence time (hr)", "zone_type": "Zone"},
            title="RTD — compartment residence times (placeholder)",
        )
        fig_rtd.update_layout(font_family="DM Sans", paper_bgcolor="white", plot_bgcolor="#F8FBFA")
        st.plotly_chart(fig_rtd, use_container_width=True)


# ══════════════════════════════════════════════════════════
#  TAB 2 — CELL KINETICS
# ══════════════════════════════════════════════════════════
with tab_kinetics:
    st.markdown('<p class="section-title">Cell Kinetics</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="placeholder-banner">
      ⚠️  Time profiles are synthetic placeholders. Replace <code>simulate_time_profiles()</code> with
      your compartment model kinetics solver.
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.results_ready:
        st.info("Run the simulation first.")
    else:
        df = st.session_state.df_time
        teal, orange, red, blue = "#12A896", "#F0A832", "#D44B2A", "#2460A7"

        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=("Cell density (×10⁶/mL)", "Viability (%)",
                            "Glucose (mM)", "Lactate (mM)",
                            "DO (% sat)", "Titer (mg/L)"),
            vertical_spacing=0.15, horizontal_spacing=0.1,
        )

        def add_line(fig, x, y, name, color, row, col):
            fig.add_trace(go.Scatter(x=x, y=y, name=name, line=dict(color=color, width=2),
                                     showlegend=False), row=row, col=col)

        t = df["time_hr"]
        add_line(fig, t, df["cell_density_e6_cells_mL"], "Cell density", teal,   1, 1)
        add_line(fig, t, df["viability_pct"],            "Viability",    orange, 1, 2)
        add_line(fig, t, df["glucose_mM"],               "Glucose",      blue,   2, 1)
        add_line(fig, t, df["lactate_mM"],               "Lactate",      red,    2, 2)
        add_line(fig, t, df["DO_pct"],                   "DO",           teal,   3, 1)
        add_line(fig, t, df["titer_mg_L"],               "Titer",        orange, 3, 2)

        fig.update_layout(
            height=700, font_family="DM Sans", 
            paper_bgcolor="white", plot_bgcolor="#F8FBFA",
            title_text="Cell Culture Kinetics — Time Profiles", margin = dict(l = 60, r = 20, t = 120, b = 60)
        )
        
        for i in fig.layout.annotations:
            i.font.family = "DM Sans"
        fig.update_xaxes(title_text="Time (hr)")
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("View raw data table"):
            st.dataframe(df.round(4), use_container_width=True)


# ══════════════════════════════════════════════════════════
#  TAB 3 — GLYCOSYLATION
# ══════════════════════════════════════════════════════════
with tab_glyco:
    st.markdown('<p class="section-title">Glycosylation Profile</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="placeholder-banner">
      ⚠️  Glycan fractions are synthetic placeholders. Replace <code>simulate_glycosylation()</code>
      with your glycosylation kinetics module.
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.results_ready:
        st.info("Run the simulation first.")
    else:
        df_g = st.session_state.df_glyco
        t = df_g["time_hr"]

        fig_g = go.Figure()
        palette = {"G0F_pct": "#12A896", "G1F_pct": "#2460A7", "G2F_pct": "#F0A832",
                   "Man5_pct": "#D44B2A", "Other_pct": "#8A6EB4"}
        labels  = {"G0F_pct": "G0F", "G1F_pct": "G1F", "G2F_pct": "G2F",
                   "Man5_pct": "Man5", "Other_pct": "Other"}

        for col, color in palette.items():
            fig_g.add_trace(go.Scatter(
                x=t, y=df_g[col], name=labels[col],
                line=dict(color=color, width=2.5),
                fill="tonexty" if col != "G0F_pct" else None,
                stackgroup="glyco",
            ))

        fig_g.update_layout(
            title="Glycan Species Fractions Over Time (placeholder)",
            xaxis_title="Time (hr)",
            yaxis_title="Fraction (%)",
            font_family="DM Sans",
            paper_bgcolor="white",
            plot_bgcolor="#F8FBFA",
            legend=dict(orientation="h", y=-0.2),
            height=430,
        )
        st.plotly_chart(fig_g, use_container_width=True)

        # bar chart at final time
        final_g = df_g.iloc[-1]
        species = list(labels.values())
        fracs   = [final_g[c] for c in labels]
        fig_bar = go.Figure(go.Bar(
            x=species, y=fracs,
            marker_color=list(palette.values()),
            text=[f"{v:.1f}%" for v in fracs],
            textposition="outside",
        ))
        fig_bar.update_layout(
            title=f"Glycan Distribution at t = {total_time_hr:.0f} hr",
            xaxis_title="Glycan species",
            yaxis_title="Fraction (%)",
            font_family="DM Sans",
            paper_bgcolor="white",
            plot_bgcolor="#F8FBFA",
            height=350,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        with st.expander("View raw data table"):
            st.dataframe(df_g.round(3), use_container_width=True)


# ══════════════════════════════════════════════════════════
#  TAB 4 — ZONE ANALYSIS
# ══════════════════════════════════════════════════════════
with tab_zones:
    st.markdown('<p class="section-title">Zone Analysis — Mixing & Anaerobic Regions</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="placeholder-banner">
      ⚠️  Zone classification is a placeholder based on power dissipation proxy.
      Replace <code>classify_zones()</code> with RTD + DO integration from compartment model.
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.results_ready:
        st.info("Run the simulation first.")
    else:
        df_z = st.session_state.df_zones

        # color bar chart of zone types along compartment axis
        fig_z = px.bar(
            df_z, x="compartment", y="local_DO_pct",
            color="zone_type", color_discrete_map=COLORS,
            labels={"local_DO_pct": "Local DO (%)", "compartment": "Compartment #"},
            title="Local DO by Compartment — Zone Classification",
        )
        fig_z.update_layout(font_family="DM Sans", paper_bgcolor="white", plot_bgcolor="#F8FBFA", height=380)
        st.plotly_chart(fig_z, use_container_width=True)

        # Power dissipation profile
        fig_p = px.line(
            df_z, x="compartment", y="local_power_W_m3",
            labels={"local_power_W_m3": "Local power (W/m³)", "compartment": "Compartment #"},
            title="Local Power Dissipation per Compartment",
            color_discrete_sequence=["#12A896"],
        )
        fig_p.update_layout(font_family="DM Sans", paper_bgcolor="white", plot_bgcolor="#F8FBFA", height=320)
        st.plotly_chart(fig_p, use_container_width=True)

        # Summary table
        st.markdown('<p class="section-title">Zone Summary Table</p>', unsafe_allow_html=True)
        zone_summary = df_z.groupby("zone_type").agg(
            n_compartments=("compartment", "count"),
            avg_DO_pct=("local_DO_pct", "mean"),
            avg_power=("local_power_W_m3", "mean"),
            avg_RT_hr=("residence_time_hr", "mean"),
        ).reset_index().round(2)
        st.dataframe(zone_summary, use_container_width=True)

        with st.expander("Full compartment data"):
            st.dataframe(df_z, use_container_width=True)


# ══════════════════════════════════════════════════════════
#  TAB 5 — SENSITIVITY ANALYSIS
# ══════════════════════════════════════════════════════════
with tab_sensitivity:
    st.markdown('<p class="section-title">Sensitivity Analysis</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="placeholder-banner">
      ⚠️  Sensitivity sweeps use placeholder calculations. Connect to your compartment model solver
      when the CFD database is available. Discrete operating-condition grid can be extended.
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.results_ready:
        st.info("Run the simulation first.")
    else:
        st.markdown("Select a parameter to sweep:")
        sweep_param = st.selectbox(
            "Sweep parameter",
            ["Agitation (rpm)", "DO setpoint (%)", "Temperature (°C)", "Sparger rate (vvm)"],
        )

        param_ranges = {
            "Agitation (rpm)":    np.linspace(40, 200, 8),
            "DO setpoint (%)":    np.linspace(20, 80, 8),
            "Temperature (°C)":   np.linspace(33, 39, 8),
            "Sparger rate (vvm)": np.linspace(0.02, 0.3, 8),
        }
        sweep_vals = param_ranges[sweep_param]

        # Placeholder: vary kpis across sweep
        kLa_vals, mix_vals, P_vals = [], [], []
        for v in sweep_vals:
            args = dict(
                agitation_rpm=agitation_rpm, impeller_diameter=impeller_diameter,
                power_number=power_number, working_volume=working_volume,
                temperature_C=temperature_C, air_flow_vvm=air_flow_vvm,
                n_compartments=n_compartments, total_time_hr=total_time_hr, dt_hr=dt_hr,
            )
            if sweep_param == "Agitation (rpm)":       args["agitation_rpm"] = v
            elif sweep_param == "DO setpoint (%)":     args["air_flow_vvm"] = max(0.01, v / 500)
            elif sweep_param == "Temperature (°C)":    args["temperature_C"] = v
            elif sweep_param == "Sparger rate (vvm)":  args["air_flow_vvm"] = v

            r = compute_derived_params(**args)
            kLa_vals.append(r["kLa_per_hr"])
            mix_vals.append(r["mixing_time_s"])
            P_vals.append(r["P_per_V"])

        fig_sens = make_subplots(
            rows=1, cols=3,
            subplot_titles=("kLa (hr⁻¹)", "Mixing time (s)", "P/V (W/m³)"),
        )
        for col_i, (vals, color, name) in enumerate([
            (kLa_vals, "#12A896", "kLa"),
            (mix_vals, "#F0A832", "Mixing"),
            (P_vals,   "#2460A7", "P/V"),
        ], 1):
            fig_sens.add_trace(
                go.Scatter(x=sweep_vals, y=vals, name=name,
                           line=dict(color=color, width=2.5), mode="lines+markers"),
                row=1, col=col_i,
            )

        fig_sens.update_layout(
            title=f"Sensitivity to {sweep_param}",
            font_family="DM Sans",
            paper_bgcolor="white",
            plot_bgcolor="#F8FBFA",
            height=380,
            showlegend=False,
        )
        fig_sens.update_xaxes(title_text=sweep_param)
        st.plotly_chart(fig_sens, use_container_width=True)


# ══════════════════════════════════════════════════════════
#  TAB 6 — EXPORT
# ══════════════════════════════════════════════════════════
with tab_export:
    st.markdown('<p class="section-title">Export Results</p>', unsafe_allow_html=True)

    if not st.session_state.results_ready:
        st.info("Run the simulation first, then export here.")
    else:
        p = st.session_state.run_params
        kpis = st.session_state.kpis

        col_l, col_r = st.columns(2)

        # ── CSV export ──────────────────────────────────────
        with col_l:
            st.markdown("**📊 Download data tables (CSV)**")

            for label, df_key in [
                ("Cell kinetics", "df_time"),
                ("Glycosylation",  "df_glyco"),
                ("Zone analysis",  "df_zones"),
            ]:
                df_exp = st.session_state[df_key]
                csv = df_exp.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label=f"⬇ {label} (.csv)",
                    data=csv,
                    file_name=f"NIIMBL_{label.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        # ── JSON config export ───────────────────────────────
        with col_r:
            st.markdown("**⚙️ Download run configuration (JSON)**")
            config = {
                "run_timestamp": datetime.now().isoformat(),
                "run_parameters": p,
                "derived_kpis": kpis,
            }
            json_bytes = json.dumps(config, indent=2).encode("utf-8")
            st.download_button(
                label="⬇ Run config (.json)",
                data=json_bytes,
                file_name=f"NIIMBL_config_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                use_container_width=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**📄 PDF Report**")
            st.info(
                "PDF export requires the `reportlab` package (included in requirements.txt). "
                "Click below to generate a summary report."
            )
            if st.button("Generate PDF Report", use_container_width=True):
                try:
                    from report import generate_pdf
                    pdf_bytes = generate_pdf(p, kpis, st.session_state.df_time,
                                             st.session_state.df_glyco, st.session_state.df_zones)
                    st.download_button(
                        label="⬇ Download PDF",
                        data=pdf_bytes,
                        file_name=f"NIIMBL_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"PDF generation failed: {e}")

        st.markdown("---")
        st.markdown("**📋 Run parameters summary**")
        summary_df = pd.DataFrame([
            {"Parameter": k.replace("_", " ").title(), "Value": str(v)}
            for k, v in {**p, **kpis}.items()
        ])
        st.dataframe(summary_df, use_container_width=True, hide_index=True)


# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  NIIMBL Bioreactor Digital Twin · Built with Streamlit ·
  <em>All outputs in demo mode are placeholders — replace backend functions with real CFD data once database is available.</em>
</div>
""", unsafe_allow_html=True)
