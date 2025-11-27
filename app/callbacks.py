"""
Dash callbacks for application logic - DYNAMIC VERSION
"""

import numpy as np
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, no_update, html, dcc, ALL, MATCH
from distillation import Compound, ThermodynamicPackage, ShortcutDistillation
from .layout import design_page, COMMON_COMPOUNDS
from .figures import (
    create_material_balance_figure,
    create_composition_figure,
    create_temperature_figure,
    create_gilliland_figure,
    create_summary_table
)
from . import COLORS


@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('calculation-store', 'data')
)
def display_page(pathname, store_data):
    """Route pages based on URL"""
    if pathname == '/results':
        return create_results_page(store_data)
    elif pathname == '/report':
        return create_report_page(store_data)
    else:
        return design_page()


@callback(
    [Output('compound-inputs-container', 'children'),
     Output('composition-inputs-container', 'children')],
    Input('n-components', 'value')
)
def update_compound_and_composition_inputs(n_components):
    """Generate compound selection dropdowns AND composition inputs together"""
    if not n_components:
        return [], []

    # Default compound names
    default_compounds = ['benzene', 'toluene', 'o-xylene', 'p-xylene', 'm-xylene']

    # Equal distribution
    equal_comp = 100.0 / n_components

    # Create compound selection dropdowns
    compound_inputs = []
    for i in range(n_components):
        default_value = default_compounds[i] if i < len(default_compounds) else 'benzene'

        compound_inputs.append(
            dbc.Row([
                dbc.Col([
                    html.Label(f"Component {i+1}",
                              style={'fontWeight': '600', 'fontSize': '0.75rem',
                                    'textTransform': 'uppercase', 'letterSpacing': '0.5px',
                                    'color': COLORS['text_secondary'], 'marginBottom': '0.5rem'}),
                    dcc.Dropdown(
                        id={'type': 'compound-select', 'index': i},
                        options=[{'label': c.capitalize(), 'value': c} for c in COMMON_COMPOUNDS],
                        value=default_value,
                        placeholder=f"Select or type compound {i+1}...",
                        searchable=True,
                        clearable=False,
                        style={'marginBottom': '1rem'}
                    )
                ], md=12)
            ])
        )

    # Create composition inputs
    comp_inputs = []
    cols_per_row = min(n_components, 4)

    for i in range(n_components):
        comp_name = default_compounds[i] if i < len(default_compounds) else f"Component {i+1}"

        comp_inputs.append(
            dbc.Col([
                html.Label(comp_name.capitalize(),
                          style={'fontWeight': '600', 'fontSize': '0.75rem',
                                'textTransform': 'uppercase', 'letterSpacing': '0.5px',
                                'color': COLORS['text_secondary'], 'marginBottom': '0.5rem',
                                'display': 'block'}),
                html.Div([
                    dbc.Input(
                        id={'type': 'composition', 'index': i},
                        type='number',
                        value=round(equal_comp, 1),
                        min=0,
                        max=100,
                        step=0.1,
                        style={
                            'border': f'2px solid {COLORS["input_border"]}',
                            'borderRadius': '0',
                            'padding': '0.75rem',
                            'fontSize': '1.1rem',
                            'fontWeight': '600',
                            'color': COLORS['text'],
                            'backgroundColor': 'white'
                        }
                    ),
                    html.Span("mol%",
                             style={
                                 'position': 'absolute',
                                 'right': '1rem',
                                 'top': '50%',
                                 'transform': 'translateY(-50%)',
                                 'fontWeight': '600',
                                 'color': COLORS['text_secondary'],
                                 'fontSize': '0.9rem'
                             })
                ], style={'position': 'relative', 'marginBottom': '1.5rem'})
            ], md=12//cols_per_row)
        )

    return compound_inputs, dbc.Row(comp_inputs)


@callback(
    [Output('calculation-status', 'children'),
     Output('calculation-store', 'data')],
    Input('calculate-btn', 'n_clicks'),
    [State('feed-flow', 'value'),
     State('pressure', 'value'),
     State('feed-quality', 'value'),
     State('recovery-lk', 'value'),
     State('recovery-hk', 'value'),
     State('reflux-factor', 'value'),
     State('efficiency', 'value'),
     State('n-components', 'value'),
     State({'type': 'compound-select', 'index': ALL}, 'value'),
     State({'type': 'composition', 'index': ALL}, 'value')],
    prevent_initial_call=True
)
def calculate_design(n_clicks, F, P_kPa, q, rec_lk, rec_hk, r_factor, eff_pct,
                     n_components, compound_names, compositions):
    """Main calculation callback - DYNAMIC!"""
    try:
        # Validate inputs
        if not compound_names or not compositions:
            raise ValueError("Please select compounds and enter compositions")

        if len(compound_names) != n_components or len(compositions) != n_components:
            raise ValueError("Component count mismatch")

        # Validate compositions sum to 100
        total_comp = sum(compositions)
        if abs(total_comp - 100) > 0.1:
            status = html.Div(f"ERROR: Compositions must sum to 100% (currently {total_comp:.1f}%)",
                            style={'padding': '1rem', 'backgroundColor': '#ffebee',
                                  'border': '2px solid #c62828', 'fontWeight': '600',
                                  'color': '#c62828'})
            return [status, no_update]

        # Convert inputs
        P = P_kPa * 1000
        z_F = np.array([c/100 for c in compositions])
        recovery_LK_D = rec_lk / 100
        recovery_HK_B = rec_hk / 100
        efficiency = eff_pct / 100

        # Create compounds from user selection
        try:
            compounds = [Compound(name) for name in compound_names]
        except Exception as e:
            status = html.Div(f"ERROR: Invalid compound name - {str(e)}",
                            style={'padding': '1rem', 'backgroundColor': '#ffebee',
                                  'border': '2px solid #c62828', 'fontWeight': '600',
                                  'color': '#c62828'})
            return [status, no_update]

        thermo = ThermodynamicPackage(compounds)

        # Run shortcut design
        shortcut = ShortcutDistillation(thermo, F, z_F, P)
        results = shortcut.complete_shortcut_design(
            recovery_LK_D=recovery_LK_D,
            recovery_HK_B=recovery_HK_B,
            R_factor=r_factor,
            q=q,
            efficiency=efficiency
        )

        # Calculate profiles
        N_real = results['N_real']
        stages = np.arange(1, N_real + 1).tolist()
        x_profiles = np.zeros((N_real, n_components))
        temperatures = np.zeros(N_real)

        for j, stage in enumerate(stages):
            if stage <= results['feed_stage']:
                ratio = (stage - 1) / results['feed_stage'] if results['feed_stage'] > 0 else 0
                x_stage = results['x_D'] + ratio * (z_F - results['x_D'])
            else:
                ratio = (stage - results['feed_stage']) / (N_real - results['feed_stage'])
                x_stage = z_F + ratio * (results['x_B'] - z_F)

            x_stage = x_stage / np.sum(x_stage)
            x_profiles[j, :] = x_stage

            try:
                T_bubble, _ = thermo.bubble_temperature(P, x_stage)
                temperatures[j] = T_bubble
            except:
                temperatures[j] = compounds[0].Tb + (compounds[-1].Tb - compounds[0].Tb) * (j / N_real)

        store_data = {
            'results': {k: float(v) if isinstance(v, (np.integer, np.floating)) else
                       v.tolist() if isinstance(v, np.ndarray) else v
                       for k, v in results.items()},
            'compound_names': compound_names,
            'stages': stages,
            'x_profiles': x_profiles.tolist(),
            'temperatures': temperatures.tolist(),
            'z_F': z_F.tolist(),
            'F': F
        }

        status = html.Div("CALCULATION COMPLETE - Navigate to RESULTS or REPORT",
                         style={'padding': '1rem', 'backgroundColor': '#e8f5e9',
                               'border': '2px solid #2e7d32', 'fontWeight': '600',
                               'color': '#2e7d32', 'textAlign': 'center'})

        return [status, store_data]

    except Exception as e:
        status = html.Div(f"ERROR: {str(e)}",
                         style={'padding': '1rem', 'backgroundColor': '#ffebee',
                               'border': '2px solid #c62828', 'fontWeight': '600',
                               'color': '#c62828'})
        return [status, no_update]


def create_results_page(store_data):
    """Create results visualization page"""
    if not store_data:
        n_min, r_min, n_real, feed_stage = '--', '--', '--', '--'
        mat_fig = {}
        comp_fig = {}
        temp_fig = {}
        gill_fig = {}
    else:
        results = store_data['results']
        n_min = f"{results['N_min']:.2f}"
        r_min = f"{results['R_min']:.3f}"
        n_real = f"{results['N_real']}"
        feed_stage = f"{results['feed_stage']}"

        compound_names = store_data['compound_names']
        stages = np.array(store_data['stages'])
        x_profiles = np.array(store_data['x_profiles'])
        temperatures = np.array(store_data['temperatures'])
        z_F = np.array(store_data['z_F'])
        F = store_data['F']

        mat_fig = create_material_balance_figure(results, z_F, compound_names, F)
        comp_fig = create_composition_figure(stages, x_profiles, results['feed_stage'], compound_names)
        temp_fig = create_temperature_figure(stages, temperatures, results['feed_stage'])
        gill_fig = create_gilliland_figure(results)

    return dbc.Container([
        html.H4("DESIGN RESULTS",
               style={
                   'fontWeight': '800',
                   'letterSpacing': '1.5px',
                   'color': COLORS['primary'],
                   'marginBottom': '2rem',
                   'fontSize': '1.5rem',
                   'borderBottom': f'3px solid {COLORS["border"]}',
                   'paddingBottom': '1rem'
               }),

        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div("MINIMUM STAGES",
                            style={'fontSize': '0.7rem', 'fontWeight': '700',
                                  'letterSpacing': '1px', 'color': COLORS['text_secondary'],
                                  'marginBottom': '0.5rem'}),
                    html.Div(n_min,
                            style={'fontSize': '2.5rem', 'fontWeight': '800',
                                  'color': COLORS['primary']})
                ], style={
                    'backgroundColor': COLORS['card_bg'],
                    'padding': '2rem',
                    'border': f'2px solid {COLORS["border"]}',
                    'textAlign': 'center'
                })
            ], md=3),

            dbc.Col([
                html.Div([
                    html.Div("MINIMUM REFLUX",
                            style={'fontSize': '0.7rem', 'fontWeight': '700',
                                  'letterSpacing': '1px', 'color': COLORS['text_secondary'],
                                  'marginBottom': '0.5rem'}),
                    html.Div(r_min,
                            style={'fontSize': '2.5rem', 'fontWeight': '800',
                                  'color': COLORS['primary']})
                ], style={
                    'backgroundColor': COLORS['card_bg'],
                    'padding': '2rem',
                    'border': f'2px solid {COLORS["border"]}',
                    'textAlign': 'center'
                })
            ], md=3),

            dbc.Col([
                html.Div([
                    html.Div("ACTUAL STAGES",
                            style={'fontSize': '0.7rem', 'fontWeight': '700',
                                  'letterSpacing': '1px', 'color': COLORS['text_secondary'],
                                  'marginBottom': '0.5rem'}),
                    html.Div(n_real,
                            style={'fontSize': '2.5rem', 'fontWeight': '800',
                                  'color': COLORS['primary']})
                ], style={
                    'backgroundColor': COLORS['card_bg'],
                    'padding': '2rem',
                    'border': f'2px solid {COLORS["border"]}',
                    'textAlign': 'center'
                })
            ], md=3),

            dbc.Col([
                html.Div([
                    html.Div("FEED STAGE",
                            style={'fontSize': '0.7rem', 'fontWeight': '700',
                                  'letterSpacing': '1px', 'color': COLORS['text_secondary'],
                                  'marginBottom': '0.5rem'}),
                    html.Div(feed_stage,
                            style={'fontSize': '2.5rem', 'fontWeight': '800',
                                  'color': COLORS['primary']})
                ], style={
                    'backgroundColor': COLORS['card_bg'],
                    'padding': '2rem',
                    'border': f'2px solid {COLORS["border"]}',
                    'textAlign': 'center'
                })
            ], md=3),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6("MATERIAL BALANCE",
                           style={'fontWeight': '700', 'letterSpacing': '1px',
                                 'padding': '1rem', 'margin': '0',
                                 'backgroundColor': COLORS['card_bg'],
                                 'borderBottom': f'2px solid {COLORS["border"]}'}),
                    dcc.Graph(figure=mat_fig, config={'displayModeBar': False},
                             style={'backgroundColor': 'white'})
                ], style={'border': f'2px solid {COLORS["border"]}',
                         'backgroundColor': 'white'})
            ], md=6),

            dbc.Col([
                html.Div([
                    html.H6("COMPOSITION PROFILES",
                           style={'fontWeight': '700', 'letterSpacing': '1px',
                                 'padding': '1rem', 'margin': '0',
                                 'backgroundColor': COLORS['card_bg'],
                                 'borderBottom': f'2px solid {COLORS["border"]}'}),
                    dcc.Graph(figure=comp_fig, config={'displayModeBar': False},
                             style={'backgroundColor': 'white'})
                ], style={'border': f'2px solid {COLORS["border"]}',
                         'backgroundColor': 'white'})
            ], md=6),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6("TEMPERATURE PROFILE",
                           style={'fontWeight': '700', 'letterSpacing': '1px',
                                 'padding': '1rem', 'margin': '0',
                                 'backgroundColor': COLORS['card_bg'],
                                 'borderBottom': f'2px solid {COLORS["border"]}'}),
                    dcc.Graph(figure=temp_fig, config={'displayModeBar': False},
                             style={'backgroundColor': 'white'})
                ], style={'border': f'2px solid {COLORS["border"]}',
                         'backgroundColor': 'white'})
            ], md=6),

            dbc.Col([
                html.Div([
                    html.H6("GILLILAND CORRELATION",
                           style={'fontWeight': '700', 'letterSpacing': '1px',
                                 'padding': '1rem', 'margin': '0',
                                 'backgroundColor': COLORS['card_bg'],
                                 'borderBottom': f'2px solid {COLORS["border"]}'}),
                    dcc.Graph(figure=gill_fig, config={'displayModeBar': False},
                             style={'backgroundColor': 'white'})
                ], style={'border': f'2px solid {COLORS["border"]}',
                         'backgroundColor': 'white'})
            ], md=6),
        ]),

    ], fluid=True, style={'padding': '3rem 2rem'})


def create_report_page(store_data):
    """Create summary report page"""
    if not store_data:
        table_content = html.P("No calculation data available. Run calculation on Design page.",
                              style={'textAlign': 'center', 'padding': '3rem',
                                    'color': COLORS['text_secondary']})
    else:
        results = store_data['results']
        compound_names = store_data['compound_names']
        table_content = create_summary_table(results, compound_names)

    return dbc.Container([
        html.H4("DESIGN REPORT",
               style={
                   'fontWeight': '800',
                   'letterSpacing': '1.5px',
                   'color': COLORS['primary'],
                   'marginBottom': '2rem',
                   'fontSize': '1.5rem',
                   'borderBottom': f'3px solid {COLORS["border"]}',
                   'paddingBottom': '1rem'
               }),

        html.Div([
            table_content
        ], style={
            'backgroundColor': COLORS['card_bg'],
            'border': f'2px solid {COLORS["border"]}',
            'padding': '2rem'
        }),

    ], fluid=True, style={'padding': '3rem 2rem', 'maxWidth': '1400px'})
