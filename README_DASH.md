# 🏭 Multi-Component Distillation Designer - Dash App

Interactive web application for designing multi-component distillation columns using shortcut methods.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Open in Browser
Navigate to: **http://127.0.0.1:8050**

## ✨ Features

### 🎨 Industrial Theme
- Dark, professional industrial design
- High-contrast color scheme optimized for process engineering
- Responsive layout that works on desktop and mobile

### 📊 Interactive Visualizations
- **Material Balance**: Flow rates and compositions
- **Composition Profiles**: Liquid phase distribution across stages
- **Temperature Profile**: Column temperature gradient
- **Gilliland Correlation**: Operating point visualization
- **Design Summary Table**: Complete parameter overview

### ⚙️ Adjustable Parameters
- Feed flow rate and composition
- Operating pressure
- Component recoveries
- Reflux ratio factor
- Feed quality (q)
- Tray efficiency

### 🎯 Real-time Calculations
- Fenske equation (minimum stages)
- Underwood method (minimum reflux)
- Gilliland correlation (actual stages)
- Kirkbride equation (feed stage location)
- Material and energy balances

## 🎮 How to Use

1. **Adjust Input Parameters** in the top panel
2. **Click "Calculate Design"** button
3. **View Results** in the summary cards
4. **Explore Interactive Charts** below
5. **Hover over plots** for detailed data points
6. **Experiment** with different parameters in real-time

## 📦 Technology Stack

- **Dash** - Web application framework
- **Plotly** - Interactive visualizations
- **Bootstrap** - UI components
- **NumPy/SciPy** - Scientific computing
- **Thermo** - Thermodynamic properties

## 🎓 Academic Context

**Course**: Modélisation et Simulation des Procédés - PIC
**Professor**: BAKHER Zine Elabidine
**University**: UM6P / Uh1

## 📝 Notes

- Default case: BTX (Benzene-Toluene-Xylene) separation
- Compositions must sum to 100%
- All calculations use Raoult's law for VLE
- Shortcut methods provide preliminary design estimates
