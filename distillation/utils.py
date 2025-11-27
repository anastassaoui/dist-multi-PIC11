"""
Utility functions and helpers for distillation package
"""

import sys
import warnings

warnings.filterwarnings('ignore')


class SuppressOutput:
    """Suppress stdout/stderr output"""
    def write(self, x):
        pass
    def flush(self):
        pass


def suppress_output():
    """Suppress stdout and stderr"""
    sys.stdout = SuppressOutput()
    sys.stderr = SuppressOutput()


# Call on import
suppress_output()
