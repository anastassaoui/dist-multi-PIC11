"""
Dash web application for distillation column design
"""

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

# Create Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

app.title = "Distillation Column Designer"

# Color scheme
COLORS = {
    'background': '#f5f5f5',
    'card_bg': '#ffffff',
    'border': '#000000',
    'input_border': '#cccccc',
    'text': '#000000',
    'text_secondary': '#666666',
    'primary': '#000000',
    'accent': '#333333',
    'grid': '#e0e0e0',
    'hover': '#f0f0f0'
}

from . import layout, callbacks

__all__ = ['app', 'COLORS']
