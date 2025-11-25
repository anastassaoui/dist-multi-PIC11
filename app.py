"""
Dash Application for Multi-Component Distillation Design
=========================================================
Professional industrial dashboard for BTX distillation column design

Author: Prof. BAKHER Zine Elabidine
Course: Modélisation et Simulation des Procédés - PIC
"""

import dash
from dash import dcc, html, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

from distillation_multicomposants import (
    Compound, ThermodynamicPackage, ShortcutDistillation
)

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

app.title = "Distillation Column Designer"

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


def navbar():
    return html.Div([
        dbc.Navbar(
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H3("DISTILLATION COLUMN DESIGNER",
                                   style={
                                       'margin': '0',
                                       'fontWeight': '800',
                                       'letterSpacing': '2px',
                                       'color': COLORS['primary'],
                                       'fontSize': '1.8rem'
                                   })
                        ])
                    ], width="auto"),
                ], align="center", className="w-100"),
            ], fluid=True, style={'padding': '1.5rem 2rem'}),
            color='white',
            style={
                'borderBottom': f'4px solid {COLORS["border"]}',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            },
            className="mb-0"
        ),
        dbc.Nav([
            dbc.NavItem(dbc.NavLink("DESIGN", href="/", active="exact",
                                   style={
                                       'color': COLORS['text'],
                                       'fontWeight': '700',
                                       'fontSize': '0.9rem',
                                       'letterSpacing': '1px',
                                       'padding': '1rem 2rem',
                                       'borderRight': f'1px solid {COLORS["input_border"]}'
                                   })),
            dbc.NavItem(dbc.NavLink("RESULTS", href="/results", active="exact",
                                   style={
                                       'color': COLORS['text'],
                                       'fontWeight': '700',
                                       'fontSize': '0.9rem',
                                       'letterSpacing': '1px',
                                       'padding': '1rem 2rem',
                                       'borderRight': f'1px solid {COLORS["input_border"]}'
                                   })),
            dbc.NavItem(dbc.NavLink("REPORT", href="/report", active="exact",
                                   style={
                                       'color': COLORS['text'],
                                       'fontWeight': '700',
                                       'fontSize': '0.9rem',
                                       'letterSpacing': '1px',
                                       'padding': '1rem 2rem'
                                   })),
        ], pills=False, style={
            'backgroundColor': 'white',
            'borderBottom': f'2px solid {COLORS["border"]}'
        })
    ])


def create_input_group(label, input_id, value, unit, min_val, max_val, step):
    return html.Div([
        html.Label(label,
                  style={
                      'fontWeight': '600',
                      'fontSize': '0.75rem',
                      'textTransform': 'uppercase',
                      'letterSpacing': '0.5px',
                      'color': COLORS['text_secondary'],
                      'marginBottom': '0.5rem',
                      'display': 'block'
                  }),
        html.Div([
            dbc.Input(
                id=input_id,
                type='number',
                value=value,
                min=min_val,
                max=max_val,
                step=step,
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
            html.Span(unit,
                     style={
                         'position': 'absolute',
                         'right': '1rem',
                         'top': '50%',
                         'transform': 'translateY(-50%)',
                         'fontWeight': '600',
                         'color': COLORS['text_secondary'],
                         'fontSize': '0.9rem'
                     })
        ], style={'position': 'relative'})
    ], style={'marginBottom': '1.5rem'})


def design_page():
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("PROCESS CONFIGURATION",
                               style={
                                   'fontWeight': '800',
                                   'letterSpacing': '1.5px',
                                   'color': COLORS['primary'],
                                   'marginBottom': '2rem',
                                   'fontSize': '1.5rem',
                                   'borderBottom': f'3px solid {COLORS["border"]}',
                                   'paddingBottom': '1rem'
                               })
                    ]),

                    html.Div([
                        html.Div([
                            html.H6("FEED STREAM",
                                   style={
                                       'fontWeight': '700',
                                       'letterSpacing': '1px',
                                       'marginBottom': '1.5rem',
                                       'fontSize': '0.9rem',
                                       'color': COLORS['primary']
                                   }),
                            dbc.Row([
                                dbc.Col([
                                    create_input_group("Flow Rate", "feed-flow", 100, "kmol/h", 10, 1000, 10)
                                ], md=4),
                                dbc.Col([
                                    create_input_group("Pressure", "pressure", 101.325, "kPa", 50, 500, 10)
                                ], md=4),
                                dbc.Col([
                                    create_input_group("Feed Quality", "feed-quality", 1.0, "q", 0, 1.5, 0.1)
                                ], md=4),
                            ])
                        ], style={
                            'backgroundColor': COLORS['card_bg'],
                            'padding': '2rem',
                            'border': f'1px solid {COLORS["input_border"]}',
                            'marginBottom': '2rem'
                        }),

                        html.Div([
                            html.H6("COMPOSITION",
                                   style={
                                       'fontWeight': '700',
                                       'letterSpacing': '1px',
                                       'marginBottom': '1.5rem',
                                       'fontSize': '0.9rem',
                                       'color': COLORS['primary']
                                   }),
                            dbc.Row([
                                dbc.Col([
                                    create_input_group("Benzene", "comp-benzene", 33.3, "mol%", 0, 100, 0.1)
                                ], md=4),
                                dbc.Col([
                                    create_input_group("Toluene", "comp-toluene", 33.3, "mol%", 0, 100, 0.1)
                                ], md=4),
                                dbc.Col([
                                    create_input_group("Xylene", "comp-xylene", 33.4, "mol%", 0, 100, 0.1)
                                ], md=4),
                            ])
                        ], style={
                            'backgroundColor': COLORS['card_bg'],
                            'padding': '2rem',
                            'border': f'1px solid {COLORS["input_border"]}',
                            'marginBottom': '2rem'
                        }),

                        html.Div([
                            html.H6("SEPARATION TARGETS",
                                   style={
                                       'fontWeight': '700',
                                       'letterSpacing': '1px',
                                       'marginBottom': '1.5rem',
                                       'fontSize': '0.9rem',
                                       'color': COLORS['primary']
                                   }),
                            dbc.Row([
                                dbc.Col([
                                    create_input_group("Light Key Recovery", "recovery-lk", 95, "%", 50, 99.9, 1)
                                ], md=4),
                                dbc.Col([
                                    create_input_group("Heavy Key Recovery", "recovery-hk", 95, "%", 50, 99.9, 1)
                                ], md=4),
                                dbc.Col([
                                    create_input_group("Tray Efficiency", "efficiency", 70, "%", 30, 100, 5)
                                ], md=4),
                            ])
                        ], style={
                            'backgroundColor': COLORS['card_bg'],
                            'padding': '2rem',
                            'border': f'1px solid {COLORS["input_border"]}',
                            'marginBottom': '2rem'
                        }),

                        html.Div([
                            html.H6("OPERATING CONDITIONS",
                                   style={
                                       'fontWeight': '700',
                                       'letterSpacing': '1px',
                                       'marginBottom': '1.5rem',
                                       'fontSize': '0.9rem',
                                       'color': COLORS['primary']
                                   }),
                            dbc.Row([
                                dbc.Col([
                                    create_input_group("Reflux Ratio Factor", "reflux-factor", 1.3, "x R_min", 1.1, 5.0, 0.1)
                                ], md=4),
                            ])
                        ], style={
                            'backgroundColor': COLORS['card_bg'],
                            'padding': '2rem',
                            'border': f'1px solid {COLORS["input_border"]}',
                            'marginBottom': '2rem'
                        }),

                        html.Div([
                            dbc.Button("CALCULATE DESIGN",
                                      id='calculate-btn',
                                      size='lg',
                                      style={
                                          'width': '100%',
                                          'backgroundColor': COLORS['primary'],
                                          'border': 'none',
                                          'borderRadius': '0',
                                          'padding': '1.25rem',
                                          'fontWeight': '800',
                                          'letterSpacing': '2px',
                                          'fontSize': '1rem'
                                      }),
                            html.Div(id='calculation-status', style={'marginTop': '1.5rem'})
                        ])
                    ])
                ], lg=10)
            ], justify="center")
        ], fluid=True, style={
            'padding': '3rem 2rem',
            'backgroundColor': COLORS['background']
        })
    ])


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='calculation-store'),
    navbar(),
    html.Div(id='page-content', style={'minHeight': '80vh', 'backgroundColor': COLORS['background']})
], style={'backgroundColor': COLORS['background']})


@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('calculation-store', 'data')
)
def display_page(pathname, store_data):
    if pathname == '/results':
        return create_results_page(store_data)
    elif pathname == '/report':
        return create_report_page(store_data)
    else:
        return design_page()


def create_results_page(store_data):
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
    [Output('calculation-status', 'children'),
     Output('calculation-store', 'data')],
    Input('calculate-btn', 'n_clicks'),
    [State('feed-flow', 'value'),
     State('pressure', 'value'),
     State('comp-benzene', 'value'),
     State('comp-toluene', 'value'),
     State('comp-xylene', 'value'),
     State('recovery-lk', 'value'),
     State('recovery-hk', 'value'),
     State('reflux-factor', 'value'),
     State('feed-quality', 'value'),
     State('efficiency', 'value')],
    prevent_initial_call=True
)
def calculate_design(n_clicks, F, P_kPa, comp_benz, comp_tol, comp_xyl,
                     rec_lk, rec_hk, r_factor, q, eff_pct):

    try:
        total_comp = comp_benz + comp_tol + comp_xyl
        if abs(total_comp - 100) > 0.1:
            status = html.Div("ERROR: Compositions must sum to 100%",
                            style={'padding': '1rem', 'backgroundColor': '#ffebee',
                                  'border': '2px solid #c62828', 'fontWeight': '600',
                                  'color': '#c62828'})
            return [status, no_update]

        P = P_kPa * 1000
        z_F = np.array([comp_benz/100, comp_tol/100, comp_xyl/100])
        recovery_LK_D = rec_lk / 100
        recovery_HK_B = rec_hk / 100
        efficiency = eff_pct / 100

        compound_names = ['benzene', 'toluene', 'o-xylene']
        compounds = [Compound(name) for name in compound_names]
        thermo = ThermodynamicPackage(compounds)

        shortcut = ShortcutDistillation(thermo, F, z_F, P)
        results = shortcut.complete_shortcut_design(
            recovery_LK_D=recovery_LK_D,
            recovery_HK_B=recovery_HK_B,
            R_factor=r_factor,
            q=q,
            efficiency=efficiency
        )

        N_real = results['N_real']
        stages = np.arange(1, N_real + 1).tolist()
        x_profiles = np.zeros((N_real, 3))
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


def create_material_balance_figure(results, z_F, compound_names, F):
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Flow Rates', 'Compositions'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}]]
    )

    fig.add_trace(
        go.Bar(
            x=['Feed', 'Distillate', 'Bottoms'],
            y=[F, results['D'], results['B']],
            marker_color=['#000000', '#333333', '#666666'],
            text=[f"{F:.1f}", f"{results['D']:.1f}", f"{results['B']:.1f}"],
            textposition='outside',
            showlegend=False
        ),
        row=1, col=1
    )

    for i, (name, color) in enumerate(zip(['Feed', 'Distillate', 'Bottoms'],
                                          ['#000000', '#333333', '#666666'])):
        if i == 0:
            comp = z_F
        elif i == 1:
            comp = results['x_D']
        else:
            comp = results['x_B']

        fig.add_trace(
            go.Bar(
                x=compound_names,
                y=comp * 100,
                name=name,
                marker_color=color,
                text=[f"{c*100:.1f}%" for c in comp],
                textposition='outside'
            ),
            row=1, col=2
        )

    fig.update_xaxes(title_text="Stream", row=1, col=1)
    fig.update_xaxes(title_text="Component", row=1, col=2)
    fig.update_yaxes(title_text="Flow Rate (kmol/h)", row=1, col=1)
    fig.update_yaxes(title_text="Composition (%)", row=1, col=2)

    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#000000', family='Arial, sans-serif', size=11),
        showlegend=True,
        legend=dict(x=0.7, y=0.95),
        height=400,
        hovermode='x unified'
    )

    return fig


def create_composition_figure(stages, x_profiles, feed_stage, compound_names):
    fig = go.Figure()

    colors = ['#000000', '#333333', '#666666']

    for i, (name, color) in enumerate(zip(compound_names, colors)):
        fig.add_trace(
            go.Scatter(
                x=x_profiles[:, i] * 100,
                y=stages,
                mode='lines+markers',
                name=name.capitalize(),
                line=dict(color=color, width=2),
                marker=dict(size=4),
                hovertemplate=f'<b>{name.capitalize()}</b><br>' +
                             'Stage: %{y}<br>' +
                             'Composition: %{x:.2f}%<extra></extra>'
            )
        )

    fig.add_hline(
        y=feed_stage,
        line_dash="dash",
        line_color='#999999',
        line_width=2,
        annotation_text=f"Feed Stage: {feed_stage}",
        annotation_position="right"
    )

    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#000000', family='Arial, sans-serif', size=11),
        xaxis_title="Liquid Composition (%)",
        yaxis_title="Stage Number",
        height=500,
        hovermode='closest',
        xaxis=dict(gridcolor='#e0e0e0', showgrid=True),
        yaxis=dict(gridcolor='#e0e0e0', showgrid=True, autorange='reversed')
    )

    return fig


def create_temperature_figure(stages, temperatures, feed_stage):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=temperatures - 273.15,
            y=stages,
            mode='lines+markers',
            line=dict(color='#000000', width=2),
            marker=dict(size=4, color='#000000'),
            hovertemplate='<b>Temperature Profile</b><br>' +
                         'Stage: %{y}<br>' +
                         'Temperature: %{x:.1f} C<extra></extra>'
        )
    )

    fig.add_hline(
        y=feed_stage,
        line_dash="dash",
        line_color='#999999',
        line_width=2,
        annotation_text=f"Feed Stage",
        annotation_position="left"
    )

    T_top = temperatures[0] - 273.15
    T_bottom = temperatures[-1] - 273.15

    fig.add_annotation(
        x=T_top, y=1,
        text=f"Top: {T_top:.1f} C",
        showarrow=True,
        arrowhead=2,
        arrowcolor='#000000',
        ax=40, ay=-40
    )

    fig.add_annotation(
        x=T_bottom, y=len(stages),
        text=f"Bottom: {T_bottom:.1f} C",
        showarrow=True,
        arrowhead=2,
        arrowcolor='#000000',
        ax=-40, ay=40
    )

    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#000000', family='Arial, sans-serif', size=11),
        xaxis_title="Temperature (C)",
        yaxis_title="Stage Number",
        height=500,
        hovermode='closest',
        xaxis=dict(gridcolor='#e0e0e0', showgrid=True),
        yaxis=dict(gridcolor='#e0e0e0', showgrid=True, autorange='reversed'),
        showlegend=False
    )

    return fig


def create_gilliland_figure(results):
    fig = go.Figure()

    N_range = np.linspace(results['N_min'], results['N_min'] * 3, 100)
    R_range = []

    for N in N_range:
        Y = (N - results['N_min']) / (N + 1)
        if Y >= 0.999:
            R_range.append(results['R_min'])
        else:
            X_num = np.linspace(0.01, 0.99, 100)
            exponent = (1 + 54.4*X_num) * (X_num - 1) / ((11 + 117.2*X_num) * np.sqrt(X_num))
            Y_curve = 1 - np.exp(exponent)
            idx = np.argmin(np.abs(Y_curve - Y))
            X = X_num[idx]
            R = results['R_min'] + X * (1 + results['R_min']) / (1 - X) if X < 0.999 else results['R_min'] * 10
            R_range.append(min(R, results['R_min'] * 5))

    fig.add_trace(
        go.Scatter(
            x=R_range,
            y=N_range,
            mode='lines',
            name='Gilliland Correlation',
            line=dict(color='#000000', width=2),
            hovertemplate='<b>Gilliland Curve</b><br>' +
                         'Reflux: %{x:.3f}<br>' +
                         'Stages: %{y:.2f}<extra></extra>'
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[results['R']],
            y=[results['N_theoretical']],
            mode='markers',
            name='Operating Point',
            marker=dict(size=12, color='#666666', symbol='diamond'),
            hovertemplate='<b>Operating Point</b><br>' +
                         f"R = {results['R']:.3f}<br>" +
                         f"N = {results['N_theoretical']:.2f}<extra></extra>"
        )
    )

    fig.add_hline(
        y=results['N_min'],
        line_dash="dash",
        line_color='#999999',
        line_width=2,
        annotation_text=f"N_min = {results['N_min']:.2f}"
    )

    fig.add_vline(
        x=results['R_min'],
        line_dash="dash",
        line_color='#999999',
        line_width=2,
        annotation_text=f"R_min = {results['R_min']:.3f}"
    )

    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#000000', family='Arial, sans-serif', size=11),
        xaxis_title="Reflux Ratio (R)",
        yaxis_title="Number of Theoretical Stages (N)",
        height=500,
        hovermode='closest',
        xaxis=dict(gridcolor='#e0e0e0', showgrid=True),
        yaxis=dict(gridcolor='#e0e0e0', showgrid=True)
    )

    return fig


def create_summary_table(results, compound_names):
    table_data = [
        ['Parameter', 'Value', 'Unit', 'Method'],
        ['Minimum Stages', f"{results['N_min']:.2f}", 'stages', 'Fenske'],
        ['Minimum Reflux', f"{results['R_min']:.3f}", '-', 'Underwood'],
        ['Operating Reflux', f"{results['R']:.3f}", '-', f"{results['R']/results['R_min']:.2f} x R_min"],
        ['Theoretical Stages', f"{results['N_theoretical']:.2f}", 'stages', 'Gilliland'],
        ['Tray Efficiency', f"{results['efficiency']*100:.1f}", '%', 'Input'],
        ['Actual Stages', f"{results['N_real']}", 'stages', 'Calculated'],
        ['Feed Stage', f"{results['feed_stage']}", '-', 'Kirkbride'],
        ['Rectification Stages', f"{results['N_R']}", 'stages', 'Kirkbride'],
        ['Stripping Stages', f"{results['N_S']}", 'stages', 'Kirkbride'],
        ['Distillate Flow', f"{results['D']:.2f}", 'kmol/h', 'Material Balance'],
        ['Bottoms Flow', f"{results['B']:.2f}", 'kmol/h', 'Material Balance'],
        ['Liquid Flow (Rect.)', f"{results['L']:.2f}", 'kmol/h', 'Internal Flows'],
        ['Vapor Flow (Rect.)', f"{results['V']:.2f}", 'kmol/h', 'Internal Flows'],
    ]

    df = pd.DataFrame(table_data[1:], columns=table_data[0])

    table = dbc.Table.from_dataframe(
        df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        style={
            'color': '#000000',
            'fontSize': '0.95rem',
            'fontWeight': '500'
        }
    )

    return table


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
