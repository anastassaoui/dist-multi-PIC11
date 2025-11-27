# Implementation Plan - Missing Features from PDF

## Current State
- Shortcut methods only (Fenske, Underwood, Gilliland, Kirkbride)
- Simple linear composition/temperature profiles
- Basic material balance calculations
- No rigorous simulation capability

## Missing Features (PDF Sections 4-11)

### PRIORITY 1: MESH Rigorous Simulation (Section 4)

Backend - distillation/mesh.py:
- MESHSolver class with Wang-Henke algorithm
- Stage-by-stage material balances (M)
- VLE equilibrium calculations (E) at each stage
- Normalization constraints (S)
- Heat balance equations (H) - calculate QC, QR
- Iterative convergence (tolerance: T < 0.1K, x < 1e-6)
- Return: stage temperatures, liquid/vapor compositions, L/V flow rates, duties

Frontend - New RESULTS tab sections:
- Stage-by-stage temperature profile (accurate, not linear)
- Stage-by-stage composition profiles (accurate liquid + vapor)
- Internal flow rates plot (L and V vs stage number)
- Heat duties display (QC condenser, QR reboiler in kW)
- Convergence metrics table

### PRIORITY 2: Parametric Studies (Section 9)

Backend - distillation/parametric.py:
- reflux_study(R_range, compound_system) -> N vs R, Q vs R
- pressure_study(P_range, compound_system) -> alpha vs P, N vs P, T vs P

Frontend - New PARAMETRIC tab:
- Reflux ratio slider (1.1*Rmin to 5.0*Rmin)
- Live plot: N_theoretical vs R
- Live plot: Energy (QC+QR) vs R
- Pressure study controls
- Live plots: Effect on separation, temperatures, energy

### PRIORITY 3: Economic Optimization (Section 10.3)

Backend - distillation/economics.py:
- Column cost model (diameter, height, material)
- Tray cost model (number, type)
- Heat exchanger costs (condenser, reboiler)
- Operating costs (energy, cooling water)
- TAC calculation (capital + operating)
- optimize_reflux() -> optimal R for minimum TAC

Frontend - New ECONOMICS tab:
- Cost breakdown table (capital vs operating)
- TAC vs reflux ratio plot
- Optimal design point indicator
- Sensitivity analysis controls

### PRIORITY 4: Non-Ideal Mixtures (Section 10.1)

Backend - distillation/activity.py:
- Activity coefficient models (NRTL, UNIQUAC, Wilson)
- Modified K-value: K = gamma * Psat / P
- Binary interaction parameters database
- Integration with MESH solver

Frontend - DESIGN page addition:
- Thermodynamic model selector dropdown
- Activity model parameter inputs (if non-ideal selected)
- Warning if non-ideal system detected

## Implementation Order

Phase 1 (Core):
1. distillation/mesh.py - MESH solver with Wang-Henke
2. Update app/figures.py - accurate profile plots
3. Update RESULTS tab - show rigorous results

Phase 2 (Studies):
1. distillation/parametric.py - reflux and pressure studies
2. New PARAMETRIC tab in app/layout.py
3. New callbacks for parametric controls

Phase 3 (Economics):
1. distillation/economics.py - cost models and optimization
2. New ECONOMICS tab in app/layout.py
3. New callbacks for economic analysis

Phase 4 (Advanced):
1. distillation/activity.py - non-ideal thermodynamics
2. Update DESIGN page with model selector
3. Integrate with MESH solver

## Files to Create
- distillation/mesh.py
- distillation/parametric.py
- distillation/economics.py
- distillation/activity.py

## Files to Modify
- app/layout.py - add new tabs
- app/callbacks.py - add new page routes and callbacks
- app/figures.py - add new plot functions
- distillation/__init__.py - export new classes
