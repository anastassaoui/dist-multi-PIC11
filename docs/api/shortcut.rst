Shortcut Design Methods
=======================

The ``shortcut`` module implements industry-standard shortcut methods for preliminary
distillation column design.

Module Overview
---------------

.. automodule:: distillation.shortcut
   :members:
   :undoc-members:
   :show-inheritance:

ShortcutDistillation Class
---------------------------

.. autoclass:: distillation.shortcut.ShortcutDistillation
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Design Methods
--------------

Fenske Equation
~~~~~~~~~~~~~~~

Calculates the **minimum number of theoretical stages** at total reflux:

.. math::

   N_{min} = \frac{\log \left[ \frac{(x_{LK}/x_{HK})_D}{(x_{LK}/x_{HK})_B} \right]}{\log(\alpha_{avg})}

Where:
   - :math:`N_{min}` = minimum theoretical stages
   - :math:`x_{LK}` = light key mole fraction
   - :math:`x_{HK}` = heavy key mole fraction
   - :math:`D` = distillate
   - :math:`B` = bottoms
   - :math:`\alpha_{avg}` = average relative volatility

Underwood Method
~~~~~~~~~~~~~~~~

Determines the **minimum reflux ratio**:

**Equation 1** (Find θ):

.. math::

   \sum_{i=1}^{n} \frac{\alpha_i \cdot z_{F,i}}{\alpha_i - \theta} = 1 - q

**Equation 2** (Calculate R_min):

.. math::

   R_{min} + 1 = \sum_{i=1}^{n} \frac{\alpha_i \cdot x_{D,i}}{\alpha_i - \theta}

Where:
   - :math:`\theta` = Underwood root (between :math:`\alpha_{HK}` and :math:`\alpha_{LK}`)
   - :math:`q` = feed quality (liquid fraction)
   - :math:`z_F` = feed composition

Gilliland Correlation
~~~~~~~~~~~~~~~~~~~~~~

Relates actual stages to operating conditions:

.. math::

   X = \frac{R - R_{min}}{R + 1}

.. math::

   Y = 1 - \exp\left[\frac{(1 + 54.4X)(X-1)}{(11 + 117.2X)\sqrt{X}}\right]

.. math::

   N = N_{min} + \frac{Y}{1-Y}

Where:
   - :math:`R` = operating reflux ratio
   - :math:`N` = theoretical stages

Kirkbride Equation
~~~~~~~~~~~~~~~~~~

Determines optimal **feed stage location**:

.. math::

   \log\left(\frac{N_R}{N_S}\right) = 0.206 \log\left[\frac{B}{D} \cdot \frac{z_{HK}}{z_{LK}} \cdot \left(\frac{x_{B,LK}}{x_{D,HK}}\right)^2\right]

Where:
   - :math:`N_R` = rectification stages
   - :math:`N_S` = stripping stages

Example Usage
-------------

Complete Design Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from distillation import Compound, ThermodynamicPackage, ShortcutDistillation
   import numpy as np

   # Setup system
   compounds = [Compound('benzene'), Compound('toluene'), Compound('o-xylene')]
   thermo = ThermodynamicPackage(compounds)

   F = 100.0  # kmol/h
   z_F = np.array([0.333, 0.333, 0.334])
   P = 101325  # Pa

   # Create shortcut design object
   shortcut = ShortcutDistillation(thermo, F, z_F, P)

   # Run complete design
   results = shortcut.complete_shortcut_design(
       recovery_LK_D=0.95,   # 95% light key in distillate
       recovery_HK_B=0.95,   # 95% heavy key in bottoms
       R_factor=1.3,         # R = 1.3 * R_min
       q=1.0,                # Saturated liquid feed
       efficiency=0.70       # 70% tray efficiency
   )

Accessing Results
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Design parameters
   print(f"Minimum stages (Fenske): {results['N_min']:.2f}")
   print(f"Minimum reflux (Underwood): {results['R_min']:.3f}")
   print(f"Operating reflux: {results['R']:.3f}")
   print(f"Theoretical stages (Gilliland): {results['N_theoretical']:.2f}")
   print(f"Actual stages: {results['N_real']}")
   print(f"Feed stage (Kirkbride): {results['feed_stage']}")

   # Stream compositions
   print(f"Distillate flow: {results['D']:.2f} kmol/h")
   print(f"Distillate composition: {results['x_D']}")
   print(f"Bottoms flow: {results['B']:.2f} kmol/h")
   print(f"Bottoms composition: {results['x_B']}")

   # Internal flows
   print(f"Liquid flow (rectification): {results['L']:.2f} kmol/h")
   print(f"Vapor flow (rectification): {results['V']:.2f} kmol/h")

Step-by-Step Design
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # 1. Material balance
   D, B, x_D, x_B = shortcut.material_balance(
       recovery_LK_D=0.95,
       recovery_HK_B=0.95
   )

   # 2. Fenske equation
   N_min, alpha_avg = shortcut.fenske_equation()

   # 3. Underwood method
   R_min, theta = shortcut.underwood_method(q=1.0)

   # 4. Gilliland correlation
   R = 1.3 * R_min
   N_theoretical = shortcut.gilliland_correlation(R)

   # 5. Real stages
   efficiency = 0.70
   N_real = int(np.ceil(N_theoretical / efficiency))

   # 6. Kirkbride equation
   N_R, N_S, feed_stage = shortcut.kirkbride_equation(N_real)

Design Considerations
---------------------

Reflux Ratio Selection
~~~~~~~~~~~~~~~~~~~~~~~

Typical operating reflux ratios:

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - R/R_min
     - Characteristics
     - Application
   * - 1.05 - 1.2
     - Very high stages, low energy
     - Difficult separations, expensive utilities
   * - 1.2 - 1.5
     - Optimal economic balance
     - **Most common choice**
   * - 1.5 - 3.0
     - Fewer stages, high energy
     - Easy separations, cheap utilities

Feed Quality (q)
~~~~~~~~~~~~~~~~

Feed thermal condition:

.. list-table::
   :header-rows: 1
   :widths: 15 30 55

   * - q value
     - Feed condition
     - Description
   * - 0
     - Saturated vapor
     - Feed enters as 100% vapor
   * - 0 < q < 1
     - Two-phase
     - Partial vaporization
   * - 1
     - Saturated liquid
     - **Most common case**
   * - q > 1
     - Subcooled liquid
     - Liquid below boiling point

Tray Efficiency
~~~~~~~~~~~~~~~

Typical Murphree tray efficiencies:

- Sieve trays: 60-80%
- Valve trays: 70-85%
- Bubble cap trays: 50-70%
- Structured packing: 90-100% (HETP basis)

**Default**: 70% for preliminary design

Limitations
-----------

Shortcut methods are suitable for:

✅ Preliminary design and cost estimation
✅ Feasibility studies
✅ Comparison of design alternatives
✅ Nearly ideal mixtures (Raoult's law)

Not suitable for:

❌ Final detailed design
❌ Non-ideal mixtures (azeotropes, activity coefficients)
❌ Multiple feeds or side draws
❌ Reactive distillation
❌ High-pressure systems

For accurate design, use rigorous simulation (MESH equations) or commercial software
(Aspen Plus, HYSYS, ChemCAD).
