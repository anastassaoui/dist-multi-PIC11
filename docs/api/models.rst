Chemical Compound Models
========================

The ``models`` module defines the ``Compound`` class for representing chemical species
with their thermodynamic properties.

Module Overview
---------------

.. automodule:: distillation.models
   :members:
   :undoc-members:
   :show-inheritance:

Compound Class
--------------

.. autoclass:: distillation.models.Compound
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__, __repr__

Example Usage
-------------

Creating a Compound
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from distillation import Compound

   # Create benzene compound
   benzene = Compound('benzene')

   print(benzene)
   # Output: Compound(name='benzene', Tb=80.1°C, MW=78.11)

   # Access properties
   print(f"Critical temperature: {benzene.Tc:.2f} K")
   print(f"Critical pressure: {benzene.Pc/1e5:.2f} bar")
   print(f"Acentric factor: {benzene.omega:.4f}")

Vapor Pressure Calculation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   T = 353.15  # K (80°C)
   P_sat = benzene.vapor_pressure(T)
   print(f"Vapor pressure at {T-273.15}°C: {P_sat/1000:.2f} kPa")

K-Value Calculation
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   T = 353.15  # K
   P = 101325  # Pa
   K = benzene.K_value(T, P)
   print(f"K-value: {K:.4f}")

Enthalpy Calculations
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   T = 353.15  # K

   # Liquid enthalpy
   H_L = benzene.enthalpy_liquid(T)
   print(f"Liquid enthalpy: {H_L:.2f} J/mol")

   # Vapor enthalpy
   H_V = benzene.enthalpy_vapor(T)
   print(f"Vapor enthalpy: {H_V:.2f} J/mol")

   # Heat of vaporization
   H_vap = H_V - H_L
   print(f"Heat of vaporization: {H_vap/1000:.2f} kJ/mol")

Notes
-----

- The ``Compound`` class uses the ``thermo`` library for property retrieval
- All temperatures are in Kelvin
- All pressures are in Pascals
- All enthalpies are in J/mol
