# NIIMBL Bioreactor Digital Twin — GUI

A Streamlit-based GUI for the NIIMBL bioreactor compartment model.  
Covers hydrodynamics, cell kinetics, glycosylation, and zone analysis.

---

## 🚀 Quick Deploy on Streamlit Cloud

1. Push this folder to a **public GitHub repo**
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo → select `app.py` → Deploy

That's it. No extra configuration needed.

---

## 🖥️ Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 📁 Project Structure

```
niimbl_gui/
├── app.py              # Main Streamlit app (all UI + backend calls)
├── report.py           # PDF report generator (reportlab)
├── requirements.txt
├── .streamlit/
│   └── config.toml     # Theme & server settings
└── README.md
```

---

## 🔌 Replacing Placeholders with Real Data

All placeholder functions are clearly marked with `⚠️ PLACEHOLDER` banners in the UI
and `# PLACEHOLDER` comments in the code. Here's where to swap in real data:

### 1. Hydrodynamics / CFD data
**Function:** `simulate_velocity_field()` in `app.py`  
**Replace with:** Load from your CFD `.xlsx` database file.  
**File naming convention:** `{reactor_geometry}_{working_volume_m3}_{agitation_rpm}_{sparging_vvm}.xlsx`  
**What it should return:** A velocity matrix (rows = radial, cols = axial compartments) in SI units.

```python
# Example replacement
def simulate_velocity_field(n_compartments, cfd_filepath):
    df = pd.read_excel(cfd_filepath)          # load your COMSOL output
    U = df.pivot(...)                          # reshape to matrix
    V = ...
    speed = np.sqrt(U**2 + V**2)
    return Z, R, U, V, speed
```

### 2. Cell kinetics
**Function:** `simulate_time_profiles()` in `app.py`  
**Replace with:** Your compartment model ODE solver output.  
**Expected output columns:** `time_hr, cell_density_e6_cells_mL, viability_pct, glucose_mM, lactate_mM, DO_pct, pH, titer_mg_L`

### 3. Glycosylation
**Function:** `simulate_glycosylation()` in `app.py`  
**Replace with:** Your glycosylation kinetics module output.  
**Expected output columns:** `time_hr, G0F_pct, G1F_pct, G2F_pct, Man5_pct, Other_pct`

### 4. Zone classification
**Function:** `classify_zones()` in `app.py`  
**Replace with:** RTD (residence time distribution) analysis from the compartment model.  
**Expected output columns:** `compartment, zone_type, local_power_W_m3, local_DO_pct, residence_time_hr`

### 5. Derived KPIs
**Function:** `compute_derived_params()` in `app.py`  
The power, kLa, mixing time, and Kolmogorov scale calculations use standard correlations
(Nienow, van't Riet) — these are reasonable approximations. Update the correlation
constants when you have experimental validation data.

---

## 📊 CFD Database Integration

Per the URS, the database approach works as follows:

1. Pre-solve CFD for discrete operating conditions (reactor geometry × rpm × vvm grid)
2. Save each run as `{geometry}_{volume}_{rpm}_{vvm}.xlsx` (SI units throughout)
3. At runtime, the GUI looks up the nearest pre-solved file and interpolates
4. For conditions outside the database, "advanced interpolation" is applied

The file upload widget in the sidebar (Simulation Settings → "Upload CFD output") is wired up
and ready — just replace the `simulate_velocity_field()` call to use `cfd_file` from
`st.session_state`.

---

## 📄 PDF Export

PDF generation uses `reportlab`. The report includes:
- Full run parameters
- Derived KPIs
- Cell kinetics summary table
- Glycosylation profile at final time
- Zone analysis summary

To embed actual charts as images in the PDF, install `kaleido`:
```bash
pip install kaleido
```
Then use `fig.write_image("plot.png")` and insert with `reportlab.platypus.Image`.

---

## ⚠️ Notes

- All outputs are **placeholders** until the CFD database is connected
- Keep all inputs/outputs in **SI units** (per URS specification)
- The GUI supports sensitivity analysis sweeps — extend `param_ranges` dict as needed
- Feeding strategies (Sheet 1 of URS) can be added as a new sidebar expander
