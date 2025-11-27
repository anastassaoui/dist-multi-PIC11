"""
Dash callbacks for application logic - DYNAMIC VERSION
"""

import numpy as np
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, no_update, html, dcc, ALL, MATCH
from distillation import Compound, ThermodynamicPackage, ShortcutDistillation, MESHSolver, ParametricStudy
from .layout import design_page, parametric_page, COMMON_COMPOUNDS
from .figures import (
    create_material_balance_figure,
    create_composition_figure,
    create_temperature_figure,
    create_gilliland_figure,
    create_summary_table,
    create_flow_rates_figure,
    create_vapor_composition_figure,
    create_heat_duties_card
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
    elif pathname == '/parametric':
        return parametric_page()
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
     State({'type': 'composition', 'index': ALL}, 'value'),
     State('simulation-method', 'value')],
    prevent_initial_call=True
)
def calculate_design(n_clicks, F, P_kPa, q, rec_lk, rec_hk, r_factor, eff_pct,
                     n_components, compound_names, compositions, sim_method):
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

        if sim_method == 'shortcut':
            # Run shortcut design
            shortcut = ShortcutDistillation(thermo, F, z_F, P)
            results = shortcut.complete_shortcut_design(
                recovery_LK_D=recovery_LK_D,
                recovery_HK_B=recovery_HK_B,
                R_factor=r_factor,
                q=q,
                efficiency=efficiency
            )

            # Calculate approximate linear profiles for shortcut
            N_real = results['N_real']
            stages = np.arange(1, N_real + 1).tolist()
            x_profiles = np.zeros((N_real, n_components))
            y_profiles = np.zeros((N_real, n_components))
            temperatures = np.zeros(N_real)
            L_flows = np.zeros(N_real)
            V_flows = np.zeros(N_real)

            for j, stage in enumerate(stages):
                if stage <= results['feed_stage']:
                    ratio = (stage - 1) / results['feed_stage'] if results['feed_stage'] > 0 else 0
                    x_stage = results['x_D'] + ratio * (z_F - results['x_D'])
                else:
                    ratio = (stage - results['feed_stage']) / (N_real - results['feed_stage'])
                    x_stage = z_F + ratio * (results['x_B'] - z_F)

                x_stage = x_stage / np.sum(x_stage)
                x_profiles[j, :] = x_stage
                y_profiles[j, :] = x_stage  # Approximate for shortcut

                try:
                    T_bubble, _ = thermo.bubble_temperature(P, x_stage)
                    temperatures[j] = T_bubble
                except:
                    temperatures[j] = compounds[0].Tb + (compounds[-1].Tb - compounds[0].Tb) * (j / N_real)

            # Approximate flow rates (CMO assumption)
            D_flow = results.get('D', F * 0.5)
            R_actual = results['R_min'] * r_factor
            for j in range(N_real):
                if j < results['feed_stage']:
                    L_flows[j] = R_actual * D_flow
                    V_flows[j] = (R_actual + 1) * D_flow
                else:
                    L_flows[j] = L_flows[results['feed_stage']-1] + F
                    V_flows[j] = V_flows[results['feed_stage']-1]

            results['QC'] = 0.0  # Placeholder
            results['QR'] = 0.0
            results['y_profiles'] = y_profiles.tolist()
            results['L_flows'] = L_flows.tolist()
            results['V_flows'] = V_flows.tolist()
            results['method'] = 'shortcut'

        else:  # rigorous MESH
            # Run shortcut first to get initial estimates
            shortcut = ShortcutDistillation(thermo, F, z_F, P)
            initial_results = shortcut.complete_shortcut_design(
                recovery_LK_D=recovery_LK_D,
                recovery_HK_B=recovery_HK_B,
                R_factor=r_factor,
                q=q,
                efficiency=efficiency
            )

            # Run MESH solver with shortcut results as initial guess
            N_theoretical = int(initial_results['N_theoretical'])
            feed_stage_mesh = int(initial_results['feed_stage'])
            R_actual = initial_results['R_min'] * r_factor

            mesh_solver = MESHSolver(
                thermo_package=thermo,
                F=F,
                z_F=z_F,
                P=P,
                N=N_theoretical,
                feed_stage=feed_stage_mesh,
                R=R_actual
            )

            mesh_results = mesh_solver.solve(max_iter=100, tol_T=0.1, tol_x=1e-6)

            # Package results
            stages = list(range(1, N_theoretical + 1))
            x_profiles = mesh_results['x_profiles']
            y_profiles = mesh_results['y_profiles']
            temperatures = mesh_results['temperatures']
            L_flows = mesh_results['L_flows']
            V_flows = mesh_results['V_flows']

            results = {
                'N_min': initial_results['N_min'],
                'R_min': initial_results['R_min'],
                'N_theoretical': N_theoretical,
                'N_real': int(N_theoretical / efficiency),
                'feed_stage': feed_stage_mesh,
                'R_operating': R_actual,
                'D': mesh_results['D'],
                'B': mesh_results['B'],
                'x_D': mesh_results['x_D'].tolist(),
                'x_B': mesh_results['x_B'].tolist(),
                'QC': mesh_results['QC'],
                'QR': mesh_results['QR'],
                'converged': mesh_results['converged'],
                'iterations': mesh_results['iterations'],
                'y_profiles': y_profiles.tolist(),
                'L_flows': L_flows.tolist(),
                'V_flows': V_flows.tolist(),
                'method': 'rigorous'
            }

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

        # Additional plots for rigorous simulation
        show_rigorous = results.get('method') == 'rigorous'
        if show_rigorous or 'y_profiles' in results:
            y_profiles = np.array(results.get('y_profiles', x_profiles))
            L_flows = np.array(results.get('L_flows', []))
            V_flows = np.array(results.get('V_flows', []))
            QC = results.get('QC', 0.0)
            QR = results.get('QR', 0.0)

            vapor_fig = create_vapor_composition_figure(stages, y_profiles, results['feed_stage'], compound_names)
            if len(L_flows) > 0 and len(V_flows) > 0:
                flow_fig = create_flow_rates_figure(stages, L_flows, V_flows, results['feed_stage'])
                duties_card = create_heat_duties_card(QC, QR)
            else:
                flow_fig = {}
                duties_card = html.Div()
        else:
            vapor_fig = {}
            flow_fig = {}
            duties_card = html.Div()

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
        ], className="mb-4"),

        # Rigorous simulation additional results
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6("VAPOR COMPOSITION PROFILES",
                           style={'fontWeight': '700', 'letterSpacing': '1px',
                                 'padding': '1rem', 'margin': '0',
                                 'backgroundColor': COLORS['card_bg'],
                                 'borderBottom': f'2px solid {COLORS["border"]}'}),
                    dcc.Graph(figure=vapor_fig, config={'displayModeBar': False},
                             style={'backgroundColor': 'white'})
                ], style={'border': f'2px solid {COLORS["border"]}',
                         'backgroundColor': 'white'})
            ], md=6),

            dbc.Col([
                html.Div([
                    html.H6("INTERNAL FLOW RATES",
                           style={'fontWeight': '700', 'letterSpacing': '1px',
                                 'padding': '1rem', 'margin': '0',
                                 'backgroundColor': COLORS['card_bg'],
                                 'borderBottom': f'2px solid {COLORS["border"]}'}),
                    dcc.Graph(figure=flow_fig, config={'displayModeBar': False},
                             style={'backgroundColor': 'white'})
                ], style={'border': f'2px solid {COLORS["border"]}',
                         'backgroundColor': 'white'})
            ], md=6),
        ], className="mb-4") if vapor_fig else html.Div(),

        # Heat duties card
        dbc.Row([
            dbc.Col([
                duties_card
            ], md=12)
        ]) if duties_card and not isinstance(duties_card, type(html.Div())) else html.Div(),

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


@callback(
    [Output('study-status', 'children'),
     Output('parametric-results', 'children')],
    Input('run-study-btn', 'n_clicks'),
    [State('study-type', 'value'),
     State('calculation-store', 'data')],
    prevent_initial_call=True
)
def run_parametric_study(n_clicks, study_type, calc_data):
    """Run parametric study based on selected type"""
    import plotly.graph_objects as go

    try:
        if not calc_data:
            status = html.Div("ERROR: Run a design calculation first",
                            style={'padding': '1rem', 'backgroundColor': '#ffebee',
                                  'border': '2px solid #c62828', 'fontWeight': '600',
                                  'color': '#c62828'})
            return [status, no_update]

        # Extract base case data
        compound_names = calc_data['compound_names']
        z_F = np.array(calc_data['z_F'])
        F = calc_data['F']
        results = calc_data['results']
        P_base = results.get('P', 101325)

        # Create compounds and thermo package
        compounds = [Compound(name) for name in compound_names]
        thermo = ThermodynamicPackage(compounds)

        # Initialize parametric study
        parametric = ParametricStudy(thermo, F, z_F, P_base)

        if study_type == 'reflux':
            # Reflux ratio study
            study_results = parametric.reflux_study()

            # Create plots
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=study_results['R_values'],
                y=study_results['N_theoretical'],
                mode='lines+markers',
                name='Theoretical Stages',
                line=dict(color='#000000', width=2),
                marker=dict(size=6)
            ))
            fig1.add_trace(go.Scatter(
                x=study_results['R_values'],
                y=study_results['N_real'],
                mode='lines+markers',
                name='Real Stages',
                line=dict(color='#666666', width=2, dash='dash'),
                marker=dict(size=6)
            ))
            fig1.add_vline(x=study_results['R_min'], line_dash="dash",
                          line_color='#d32f2f', line_width=2,
                          annotation_text=f"R_min = {study_results['R_min']:.2f}")
            fig1.update_layout(
                title='Number of Stages vs Reflux Ratio',
                xaxis_title='Reflux Ratio (R)',
                yaxis_title='Number of Stages',
                plot_bgcolor='white',
                height=400,
                hovermode='closest',
                showlegend=True
            )

            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=study_results['R_values'],
                y=[abs(q) for q in study_results['total_energy']],
                mode='lines+markers',
                line=dict(color='#d32f2f', width=2),
                marker=dict(size=6),
                fill='tozeroy',
                fillcolor='rgba(211, 47, 47, 0.1)'
            ))
            fig2.update_layout(
                title='Total Energy vs Reflux Ratio',
                xaxis_title='Reflux Ratio (R)',
                yaxis_title='Total Energy (kW)',
                plot_bgcolor='white',
                height=400,
                hovermode='closest'
            )

            results_div = html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H6("NUMBER OF STAGES VS REFLUX",
                                   style={'fontWeight': '700', 'padding': '1rem',
                                         'borderBottom': f'2px solid {COLORS["border"]}'}),
                            dcc.Graph(figure=fig1, config={'displayModeBar': False})
                        ], style={'border': f'2px solid {COLORS["border"]}', 'backgroundColor': 'white'})
                    ], md=6),
                    dbc.Col([
                        html.Div([
                            html.H6("ENERGY CONSUMPTION VS REFLUX",
                                   style={'fontWeight': '700', 'padding': '1rem',
                                         'borderBottom': f'2px solid {COLORS["border"]}'}),
                            dcc.Graph(figure=fig2, config={'displayModeBar': False})
                        ], style={'border': f'2px solid {COLORS["border"]}', 'backgroundColor': 'white'})
                    ], md=6)
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H6("KEY FINDINGS", style={'fontWeight': '700', 'marginBottom': '1rem'}),
                            html.P(f"Minimum Reflux: {study_results['R_min']:.3f}"),
                            html.P(f"Recommended Range: {1.2*study_results['R_min']:.2f} - {1.5*study_results['R_min']:.2f}"),
                            html.P("Higher reflux = fewer stages but more energy consumption")
                        ], style={'backgroundColor': '#f5f5f5', 'padding': '1.5rem',
                                'border': f'1px solid {COLORS["input_border"]}', 'marginTop': '1rem'})
                    ], md=12)
                ])
            ])

        elif study_type == 'pressure':
            # Pressure study
            study_results = parametric.pressure_study()

            # Create plots
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=study_results['P_values'],
                y=study_results['alpha_avg'],
                mode='lines+markers',
                line=dict(color='#000000', width=2),
                marker=dict(size=6)
            ))
            fig1.update_layout(
                title='Average Relative Volatility vs Pressure',
                xaxis_title='Pressure (atm)',
                yaxis_title='Average Relative Volatility',
                plot_bgcolor='white',
                height=400
            )

            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=study_results['P_values'],
                y=study_results['N_theoretical'],
                mode='lines+markers',
                line=dict(color='#666666', width=2),
                marker=dict(size=6)
            ))
            fig2.update_layout(
                title='Number of Stages vs Pressure',
                xaxis_title='Pressure (atm)',
                yaxis_title='Theoretical Stages',
                plot_bgcolor='white',
                height=400
            )

            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=study_results['P_values'],
                y=study_results['T_top'],
                mode='lines+markers',
                name='Top Temperature',
                line=dict(color='#1976d2', width=2),
                marker=dict(size=6)
            ))
            fig3.add_trace(go.Scatter(
                x=study_results['P_values'],
                y=study_results['T_bottom'],
                mode='lines+markers',
                name='Bottom Temperature',
                line=dict(color='#d32f2f', width=2),
                marker=dict(size=6)
            ))
            fig3.update_layout(
                title='Operating Temperatures vs Pressure',
                xaxis_title='Pressure (atm)',
                yaxis_title='Temperature (°C)',
                plot_bgcolor='white',
                height=400,
                showlegend=True
            )

            results_div = html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H6("VOLATILITY VS PRESSURE",
                                   style={'fontWeight': '700', 'padding': '1rem',
                                         'borderBottom': f'2px solid {COLORS["border"]}'}),
                            dcc.Graph(figure=fig1, config={'displayModeBar': False})
                        ], style={'border': f'2px solid {COLORS["border"]}', 'backgroundColor': 'white'})
                    ], md=6),
                    dbc.Col([
                        html.Div([
                            html.H6("STAGES VS PRESSURE",
                                   style={'fontWeight': '700', 'padding': '1rem',
                                         'borderBottom': f'2px solid {COLORS["border"]}'}),
                            dcc.Graph(figure=fig2, config={'displayModeBar': False})
                        ], style={'border': f'2px solid {COLORS["border"]}', 'backgroundColor': 'white'})
                    ], md=6)
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H6("TEMPERATURES VS PRESSURE",
                                   style={'fontWeight': '700', 'padding': '1rem',
                                         'borderBottom': f'2px solid {COLORS["border"]}'}),
                            dcc.Graph(figure=fig3, config={'displayModeBar': False})
                        ], style={'border': f'2px solid {COLORS["border"]}', 'backgroundColor': 'white'})
                    ], md=12)
                ], className="mt-3")
            ])

        else:  # optimization
            # TAC optimization
            opt_results = parametric.optimize_reflux()

            # Create plot
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=opt_results['R_values'],
                y=opt_results['TAC_values'],
                mode='lines+markers',
                name='Total Annualized Cost',
                line=dict(color='#000000', width=2),
                marker=dict(size=6)
            ))
            fig.add_trace(go.Scatter(
                x=opt_results['R_values'],
                y=opt_results['capital_costs'],
                mode='lines',
                name='Capital Cost',
                line=dict(color='#1976d2', width=2, dash='dash')
            ))
            fig.add_trace(go.Scatter(
                x=opt_results['R_values'],
                y=opt_results['operating_costs'],
                mode='lines',
                name='Operating Cost',
                line=dict(color='#d32f2f', width=2, dash='dash')
            ))
            fig.add_vline(x=opt_results['R_optimal'], line_dash="dot",
                         line_color='#2e7d32', line_width=3,
                         annotation_text=f"Optimal R = {opt_results['R_optimal']:.2f}")
            fig.update_layout(
                title='Total Annualized Cost Optimization',
                xaxis_title='Reflux Ratio (R)',
                yaxis_title='Cost ($/year)',
                plot_bgcolor='white',
                height=500,
                showlegend=True,
                hovermode='closest'
            )

            results_div = html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H6("COST OPTIMIZATION",
                                   style={'fontWeight': '700', 'padding': '1rem',
                                         'borderBottom': f'2px solid {COLORS["border"]}'}),
                            dcc.Graph(figure=fig, config={'displayModeBar': False})
                        ], style={'border': f'2px solid {COLORS["border"]}', 'backgroundColor': 'white'})
                    ], md=12)
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H6("OPTIMAL DESIGN", style={'fontWeight': '700', 'marginBottom': '1rem'}),
                            html.H4(f"R = {opt_results['R_optimal']:.2f}", style={'color': '#2e7d32', 'fontWeight': '800'}),
                            html.P(f"Number of Stages: {opt_results['N_optimal']}"),
                            html.P(f"TAC: ${opt_results['TAC_optimal']:,.0f}/year"),
                            html.P(f"Reflux Factor: {opt_results['R_factor_optimal']:.2f} x R_min")
                        ], style={'backgroundColor': '#e8f5e9', 'padding': '1.5rem',
                                'border': f'2px solid #2e7d32', 'marginTop': '1rem', 'textAlign': 'center'})
                    ], md=12)
                ])
            ])

        status = html.Div("STUDY COMPLETE",
                         style={'padding': '1rem', 'backgroundColor': '#e8f5e9',
                               'border': '2px solid #2e7d32', 'fontWeight': '600',
                               'color': '#2e7d32', 'textAlign': 'center'})

        return [status, results_div]

    except Exception as e:
        status = html.Div(f"ERROR: {str(e)}",
                         style={'padding': '1rem', 'backgroundColor': '#ffebee',
                               'border': '2px solid #c62828', 'fontWeight': '600',
                               'color': '#c62828'})
        return [status, no_update]
