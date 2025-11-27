# 🏭 Multi-Component Distillation Designer

**Modular web application for designing multi-component distillation columns using shortcut methods.**

**Course**: Modélisation et Simulation des Procédés - PIC
**Professor**: BAKHER Zine Elabidine
**University**: UM6P / Uh1

---

## 📁 Project Structure

```
dist-multi-PIC11/
├── distillation/              # Backend package
│   ├── __init__.py           # Package exports
│   ├── models.py             # Compound class
│   ├── thermodynamics.py     # ThermodynamicPackage class
│   ├── shortcut.py           # ShortcutDistillation methods
│   └── utils.py              # Utility functions
│
├── app/                       # Dash frontend
│   ├── __init__.py           # App initialization
│   ├── layout.py             # UI components & layouts
│   ├── callbacks.py          # Dash callbacks
│   └── figures.py            # Plotly visualizations
│
├── app.py                     # Main entry point
├── requirements.txt           # Dependencies
├── exemple_btx.py            # CLI example (BTX system)
└── README.md
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Web Application
```bash
python app.py
```

### 3. Open in Browser
Navigate to: **http://localhost:8050** or **http://127.0.0.1:8050**

### 4. Build Documentation (Optional)
```bash
pip install -r requirements-doc.txt
cd docs
make html  # Windows: make.bat html
```
Open `docs/_build/html/index.html` in browser

---

## 🎯 Features

### Backend Package (`distillation/`)
- **Modular architecture** - Clean separation of concerns
- **Thermodynamic calculations** - VLE, bubble/dew point
- **Shortcut methods** - Fenske, Underwood, Gilliland, Kirkbride
- **Component library** - Access to 20,000+ chemicals via `thermo`

### Dash Web App (`app/`)
- **Interactive UI** - Real-time parameter adjustment
- **Multi-page layout** - Design, Results, Report pages
- **Professional styling** - Industrial design theme
- **Plotly charts** - Interactive visualizations

### Calculations
- ✅ Material balance
- ✅ Minimum stages (Fenske)
- ✅ Minimum reflux (Underwood)
- ✅ Actual stages (Gilliland)
- ✅ Feed stage location (Kirkbride)
- ✅ Temperature profiles
- ✅ Composition profiles

---

## 📦 Usage Examples

### Web Interface
1. Enter feed conditions (flow, pressure, composition)
2. Set separation targets (recoveries, efficiency)
3. Click **CALCULATE DESIGN**
4. View results in **RESULTS** page
5. Export summary in **REPORT** page

### Python API
```python
from distillation import Compound, ThermodynamicPackage, ShortcutDistillation
import numpy as np

# Define system
compounds = [Compound('benzene'), Compound('toluene'), Compound('o-xylene')]
thermo = ThermodynamicPackage(compounds)

# Create design problem
F = 100.0  # kmol/h
z_F = np.array([0.333, 0.333, 0.334])
P = 101325  # Pa

shortcut = ShortcutDistillation(thermo, F, z_F, P)

# Run design
results = shortcut.complete_shortcut_design(
    recovery_LK_D=0.95,
    recovery_HK_B=0.95,
    R_factor=1.3,
    q=1.0,
    efficiency=0.70
)

print(f"Minimum stages: {results['N_min']:.2f}")
print(f"Minimum reflux: {results['R_min']:.3f}")
print(f"Actual stages: {results['N_real']}")
```

### CLI Example
```bash
python exemple_btx.py
```

---

## 🧪 Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | `numpy`, `scipy`, `thermo` |
| Frontend | `dash`, `plotly`, `dash-bootstrap-components` |
| Thermodynamics | `thermo`, `chemicals`, `CoolProp` |
| Data | `pandas` |

---

## 📊 Calculation Methods

### Fenske Equation
Calculates minimum number of theoretical stages at total reflux:
```
N_min = log[(x_LK/x_HK)_D / (x_LK/x_HK)_B] / log(α_avg)
```

### Underwood Method
Determines minimum reflux ratio for separation.

### Gilliland Correlation
Relates actual stages to minimum stages and reflux ratios.

### Kirkbride Equation
Optimizes feed stage location in the column.

---

## 🔧 Development

### Project Organization
- **Backend (`distillation/`)** - Pure calculation engine, framework-agnostic
- **Frontend (`app/`)** - Dash-specific UI and callbacks
- **Clean separation** - Easy to extend or replace components

### Adding New Features

**New shortcut method:**
```python
# In distillation/shortcut.py
class ShortcutDistillation:
    def new_method(self, params):
        # Your implementation
        pass
```

**New visualization:**
```python
# In app/figures.py
def create_new_figure(data):
    fig = go.Figure()
    # Create plot
    return fig
```

**New page:**
```python
# In app/layout.py
def new_page():
    return html.Div([...])

# In app/callbacks.py
@callback(...)
def display_new_page():
    return new_page()
```

---

## 📚 Documentation

Full API documentation is available in Sphinx format:

```bash
# Install doc requirements
pip install -r requirements-doc.txt

# Build HTML documentation
cd docs
make html  # Windows: make.bat html

# Open in browser
# File: docs/_build/html/index.html
```

**Documentation includes:**
- Complete API reference for all modules
- Mathematical formulations (Fenske, Underwood, Gilliland, Kirkbride)
- Usage examples and code snippets
- Design guidelines and limitations
- VLE calculation details

---

## 📝 Notes

- **Default case**: BTX (Benzene-Toluene-Xylene) separation
- **Compositions**: Must sum to 100%
- **VLE model**: Raoult's law (ideal mixtures)
- **Accuracy**: Shortcut methods provide preliminary estimates
- **Validation**: Compare with rigorous simulators (Aspen Plus, HYSYS)

---

## 🎓 Academic Context

This application is designed as an educational tool for chemical engineering students learning distillation design. The shortcut methods implemented are industry-standard preliminary design techniques.

**Learning Objectives:**
- Understand multicomponent distillation fundamentals
- Apply shortcut design methods
- Interpret composition and temperature profiles
- Optimize reflux ratio selection

---

## 📄 License

Educational project - Université uh1 / UM6P

---

## 🤝 Credits

**Developed by**: Prof. BAKHER Zine Elabidine
**Course**: Modélisation et Simulation des Procédés (PIC)
**Institution**: UM6P / Uh1
