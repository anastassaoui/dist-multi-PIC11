"""
Multi-Component Distillation Column Designer
============================================
Interactive web application for distillation column design

Auteur: Prof. BAKHER Zine Elabidine
Cours: Modélisation et Simulation des Procédés - PIC
Université uh1
"""

from app import app

server = app.server  # For deployment

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
