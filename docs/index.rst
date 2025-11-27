Distillation Multicomposants Documentation
==========================================

**Modular backend for multi-component distillation column design**

.. image:: https://img.shields.io/badge/Python-3.8%2B-blue
   :alt: Python Version

.. image:: https://img.shields.io/badge/License-Educational-green
   :alt: License

Course: Modélisation et Simulation des Procédés - PIC

Professor: BAKHER Zine Elabidine

University: UM6P / Uh1

----

Overview
--------

The ``distillation`` package provides a comprehensive Python implementation of
multi-component distillation design using industry-standard shortcut methods:

- **Fenske Equation** - Minimum theoretical stages at total reflux
- **Underwood Method** - Minimum reflux ratio calculation
- **Gilliland Correlation** - Actual stages from operating reflux
- **Kirkbride Equation** - Optimal feed stage location

Features
--------

✅ **Thermodynamic Calculations**
   - Vapor-liquid equilibrium (VLE)
   - Bubble and dew point calculations
   - K-values and relative volatilities
   - Mixture enthalpy calculations

✅ **Shortcut Design Methods**
   - Complete column design workflow
   - Material balance calculations
   - Internal flow rate determination
   - Stage-by-stage profile estimation

✅ **Component Database**
   - Access to 20,000+ chemicals via ``thermo`` library
   - Automatic property retrieval (Tb, Tc, Pc, MW, etc.)
   - Vapor pressure correlations
   - Enthalpy calculations

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install -r requirements.txt

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from distillation import Compound, ThermodynamicPackage, ShortcutDistillation
   import numpy as np

   # Define system components
   compounds = [
       Compound('benzene'),
       Compound('toluene'),
       Compound('o-xylene')
   ]

   # Create thermodynamic package
   thermo = ThermodynamicPackage(compounds)

   # Setup design problem
   F = 100.0  # kmol/h
   z_F = np.array([0.333, 0.333, 0.334])
   P = 101325  # Pa

   # Initialize shortcut design
   shortcut = ShortcutDistillation(thermo, F, z_F, P)

   # Run complete design
   results = shortcut.complete_shortcut_design(
       recovery_LK_D=0.95,
       recovery_HK_B=0.95,
       R_factor=1.3,
       q=1.0,
       efficiency=0.70
   )

   # Access results
   print(f"Minimum stages: {results['N_min']:.2f}")
   print(f"Minimum reflux: {results['R_min']:.3f}")
   print(f"Actual stages: {results['N_real']}")
   print(f"Feed stage: {results['feed_stage']}")

API Documentation
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api/models
   api/thermodynamics
   api/shortcut
   api/utils

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
