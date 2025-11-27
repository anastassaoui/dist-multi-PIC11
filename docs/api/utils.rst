Utilities
=========

The ``utils`` module provides helper functions and utilities for the distillation package.

Module Overview
---------------

.. automodule:: distillation.utils
   :members:
   :undoc-members:
   :show-inheritance:

Output Suppression
------------------

The ``thermo`` library generates console output during property calculations. The
``SuppressOutput`` class and ``suppress_output()`` function silence this output
for cleaner execution.

.. autoclass:: distillation.utils.SuppressOutput
   :members:
   :undoc-members:

.. autofunction:: distillation.utils.suppress_output

Usage
~~~~~

Output suppression is automatically activated when importing the distillation package:

.. code-block:: python

   from distillation import Compound

   # No console output from thermo library
   benzene = Compound('benzene')

To manually control output:

.. code-block:: python

   import sys
   from distillation.utils import SuppressOutput, suppress_output

   # Suppress output
   suppress_output()

   # Or restore output
   sys.stdout = sys.__stdout__
   sys.stderr = sys.__stderr__
