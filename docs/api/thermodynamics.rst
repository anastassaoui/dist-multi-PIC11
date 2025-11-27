Thermodynamic Package
=====================

The ``thermodynamics`` module provides VLE calculations and mixture property estimation
for multi-component systems.

Module Overview
---------------

.. automodule:: distillation.thermodynamics
   :members:
   :undoc-members:
   :show-inheritance:

ThermodynamicPackage Class
---------------------------

.. autoclass:: distillation.thermodynamics.ThermodynamicPackage
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Example Usage
-------------

Creating a Thermodynamic Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from distillation import Compound, ThermodynamicPackage

   # Define components
   compounds = [
       Compound('benzene'),
       Compound('toluene'),
       Compound('o-xylene')
   ]

   # Create thermo package
   thermo = ThermodynamicPackage(compounds)

   print(f"Number of components: {thermo.n_comp}")
   print(f"Component names: {thermo.compound_names}")

K-Values and Relative Volatilities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import numpy as np

   T = 373.15  # K (100°C)
   P = 101325  # Pa (1 atm)

   # Calculate K-values
   K = thermo.K_values(T, P)
   print("K-values:", K)

   # Calculate relative volatilities (ref: heaviest component)
   alpha = thermo.relative_volatilities(T, P, ref_index=-1)
   print("Relative volatilities:", alpha)

Bubble Point Calculation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Liquid composition
   x = np.array([0.333, 0.333, 0.334])
   P = 101325  # Pa

   # Calculate bubble temperature
   T_bubble, y = thermo.bubble_temperature(P, x)

   print(f"Bubble temperature: {T_bubble-273.15:.2f} °C")
   print(f"Vapor composition: {y}")

Dew Point Calculation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Vapor composition
   y = np.array([0.5, 0.3, 0.2])
   P = 101325  # Pa

   # Calculate dew temperature
   T_dew, x = thermo.dew_temperature(P, y)

   print(f"Dew temperature: {T_dew-273.15:.2f} °C")
   print(f"Liquid composition: {x}")

Mixture Enthalpies
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   T = 373.15  # K
   x = np.array([0.333, 0.333, 0.334])

   # Liquid mixture enthalpy
   H_L = thermo.mixture_enthalpy_liquid(T, x)
   print(f"Liquid enthalpy: {H_L:.2f} J/mol")

   # Vapor mixture enthalpy
   H_V = thermo.mixture_enthalpy_vapor(T, x)
   print(f"Vapor enthalpy: {H_V:.2f} J/mol")

VLE Assumptions
---------------

The current implementation uses **Raoult's Law** for VLE calculations:

.. math::

   y_i = K_i \cdot x_i

   K_i = \frac{P_i^{sat}(T)}{P}

Where:
   - :math:`y_i` = vapor mole fraction of component i
   - :math:`x_i` = liquid mole fraction of component i
   - :math:`K_i` = equilibrium constant (K-value)
   - :math:`P_i^{sat}` = vapor pressure of component i
   - :math:`P` = total pressure

**Valid for:**
   - Ideal mixtures (low pressure)
   - Components with similar chemical nature
   - Preliminary design calculations

**Not recommended for:**
   - High-pressure systems
   - Highly non-ideal mixtures (azeotropes)
   - Rigorous design requiring activity coefficients
