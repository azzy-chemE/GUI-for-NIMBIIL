## niimbl bioreactor digital twin // gui

by azzy xiang & ashley torralba | ohio state university | william g. lowrie department of chemical and biomolecular engineering

streamlit-based GUI for the NIIMBL bioreactor compartment model.  

covers
- hydrodynamics
- cell kinetics
- glycosylation
- zone analysis.

## run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## project structure

```
├── app.py              # main streamlit app (all UI + backend calls)
├── report.py           # pdf report generator (reportlab)
├── requirements.txt
├── .streamlit/
│   └── config.toml     # theme & server settings
└── README.md
```

---

## replacing placeholders with real data

all placeholder functions are clearly marked with `⚠️ PLACEHOLDER` banners in the UI
and `# PLACEHOLDER` comments in the code. here's where to swap in real data !!

### 1. hydrodynamics / CFD data
**function:** `simulate_velocity_field()` in `app.py`  
**replace with:** Load from your CFD `.xlsx` database file.  
**file naming convention:** `{reactor_geometry}_{working_volume_m3}_{agitation_rpm}_{sparging_vvm}.xlsx`  
**what it should return:** A velocity matrix (rows = radial, cols = axial compartments) in SI units.

```python
# example replacement
def simulate_velocity_field(n_compartments, cfd_filepath):
    df = pd.read_excel(cfd_filepath)          # load your COMSOL output
    U = df.pivot(...)                          # reshape to matrix
    V = ...
    speed = np.sqrt(U**2 + V**2)
    return Z, R, U, V, speed
```

### 2. cell kinetics
**function:** `simulate_time_profiles()` in `app.py`  
**replace with:** Your compartment model ODE solver output.  
**expected output columns:** `time_hr, cell_density_e6_cells_mL, viability_pct, glucose_mM, lactate_mM, DO_pct, pH, titer_mg_L`

### 3. glycosylation
**function:** `simulate_glycosylation()` in `app.py`  
**replace with:** Your glycosylation kinetics module output.  
**expected output columns:** `time_hr, G0F_pct, G1F_pct, G2F_pct, Man5_pct, Other_pct`

### 4. zone classification
**function:** `classify_zones()` in `app.py`  
**replace with:** RTD (residence time distribution) analysis from the compartment model.  
**expected output columns:** `compartment, zone_type, local_power_W_m3, local_DO_pct, residence_time_hr`

### 5. derived KPIs
**function:** `compute_derived_params()` in `app.py`  
the power, kLa, mixing time, and Kolmogorov scale calculations use standard correlations
(Nienow, van't Riet) — these are reasonable approximations. Update the correlation
constants when you have experimental validation data.

---

### CFD database integration

per the URS, the database approach works as follows:

1. pre-solve CFD for discrete operating conditions (reactor geometry × rpm × vvm grid)
2. save each run as `{geometry}_{volume}_{rpm}_{vvm}.xlsx` (SI units throughout)
3. at runtime, the GUI looks up the nearest pre-solved file and interpolates
4. for conditions outside the database, "advanced interpolation" is applied

the file upload widget in the sidebar (simulation settings → "upload CFD output") is wired up
and ready — just replace the `simulate_velocity_field()` call to use `cfd_file` from
`st.session_state`.

---

## pdf export

PDF generation uses `reportlab`. The report includes:
- full run parameters
- derived KPIs
- cell kinetics summary table
- glycosylation profile at final time
- zone analysis summary

to embed actual charts as images in the PDF, install `kaleido`:
```bash
pip install kaleido
```
then use `fig.write_image("plot.png")` and insert with `reportlab.platypus.Image`.

---

## notes

- all outputs are **placeholders** until the CFD database is connected
- keep all inputs/outputs in **SI units** (per URS specification)
- the GUI supports sensitivity analysis sweeps — extend `param_ranges` dict as needed
- feeding strategies (Sheet 1 of URS) can be added as a new sidebar expander
