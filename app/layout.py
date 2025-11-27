"""
Dash application layout and UI components - DYNAMIC VERSION
"""

from dash import dcc, html
import dash_bootstrap_components as dbc
from . import app, COLORS

# Common compounds for dropdown
COMMON_COMPOUNDS = [
    'benzene', 'toluene', 'o-xylene', 'p-xylene', 'm-xylene',
    'ethylbenzene', 'styrene', 'cumene',
    'methanol', 'ethanol', 'propanol', 'butanol',
    'acetone', 'MEK', 'MIBK',
    'hexane', 'heptane', 'octane', 'nonane', 'decane',
    'cyclohexane', 'methylcyclohexane',
    'water', 'ethylene glycol', 'propylene glycol'
]


def navbar():
    """Top navigation bar"""
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
            dbc.NavItem(dbc.NavLink("PARAMETRIC", href="/parametric", active="exact",
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
    """Create styled input group"""
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
    """Design input page - FULLY DYNAMIC"""
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

                    # COMPOUND SELECTION - NEW!
                    html.Div([
                        html.H6("COMPONENT SELECTION",
                               style={
                                   'fontWeight': '700',
                                   'letterSpacing': '1px',
                                   'marginBottom': '1.5rem',
                                   'fontSize': '0.9rem',
                                   'color': COLORS['primary']
                               }),

                        html.Div([
                            html.Label("Number of Components",
                                      style={'fontWeight': '600', 'fontSize': '0.75rem',
                                            'textTransform': 'uppercase', 'letterSpacing': '0.5px',
                                            'color': COLORS['text_secondary'], 'marginBottom': '0.5rem'}),
                            dcc.Dropdown(
                                id='n-components',
                                options=[
                                    {'label': '2 Components', 'value': 2},
                                    {'label': '3 Components', 'value': 3},
                                    {'label': '4 Components', 'value': 4},
                                    {'label': '5 Components', 'value': 5}
                                ],
                                value=3,
                                clearable=False,
                                style={'marginBottom': '1.5rem'}
                            ),
                        ]),

                        html.Div(id='compound-inputs-container')

                    ], style={
                        'backgroundColor': COLORS['card_bg'],
                        'padding': '2rem',
                        'border': f'1px solid {COLORS["input_border"]}',
                        'marginBottom': '2rem'
                    }),

                    # FEED STREAM
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

                    # COMPOSITION - DYNAMIC!
                    html.Div([
                        html.H6("COMPOSITION",
                               style={
                                   'fontWeight': '700',
                                   'letterSpacing': '1px',
                                   'marginBottom': '1.5rem',
                                   'fontSize': '0.9rem',
                                   'color': COLORS['primary']
                               }),
                        html.Div(id='composition-inputs-container')
                    ], style={
                        'backgroundColor': COLORS['card_bg'],
                        'padding': '2rem',
                        'border': f'1px solid {COLORS["input_border"]}',
                        'marginBottom': '2rem'
                    }),

                    # SEPARATION TARGETS
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

                    # OPERATING CONDITIONS
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

                    # SIMULATION METHOD
                    html.Div([
                        html.H6("SIMULATION METHOD",
                               style={
                                   'fontWeight': '700',
                                   'letterSpacing': '1px',
                                   'marginBottom': '1.5rem',
                                   'fontSize': '0.9rem',
                                   'color': COLORS['primary']
                               }),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Method",
                                          style={'fontWeight': '600', 'fontSize': '0.75rem',
                                                'textTransform': 'uppercase', 'letterSpacing': '0.5px',
                                                'color': COLORS['text_secondary'], 'marginBottom': '0.5rem',
                                                'display': 'block'}),
                                dcc.Dropdown(
                                    id='simulation-method',
                                    options=[
                                        {'label': 'Shortcut Methods (Fenske-Underwood-Gilliland)', 'value': 'shortcut'},
                                        {'label': 'Rigorous Simulation (MESH Equations)', 'value': 'rigorous'}
                                    ],
                                    value='shortcut',
                                    clearable=False,
                                    style={'marginBottom': '1rem'}
                                ),
                                html.Small("Rigorous simulation provides accurate stage-by-stage profiles but takes longer",
                                          style={'color': COLORS['text_secondary'], 'fontSize': '0.7rem'})
                            ], md=12)
                        ])
                    ], style={
                        'backgroundColor': COLORS['card_bg'],
                        'padding': '2rem',
                        'border': f'1px solid {COLORS["input_border"]}',
                        'marginBottom': '2rem'
                    }),

                    # CALCULATE BUTTON
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
                        html.Div(id='calculation-status')  # No initial content, no styling until populated
                    ])
                ], lg=10)
            ], justify="center")
        ], fluid=True, style={
            'padding': '3rem 2rem',
            'backgroundColor': COLORS['background']
        })
    ])


def parametric_page():
    """Parametric studies page"""
    return html.Div([
        dbc.Container([
            html.H4("PARAMETRIC STUDIES",
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
                    html.H6("STUDY TYPE",
                           style={'fontWeight': '700', 'letterSpacing': '1px',
                                 'marginBottom': '1.5rem', 'color': COLORS['primary']}),

                    dcc.Dropdown(
                        id='study-type',
                        options=[
                            {'label': 'Effect of Reflux Ratio', 'value': 'reflux'},
                            {'label': 'Effect of Operating Pressure', 'value': 'pressure'},
                            {'label': 'Reflux Optimization (TAC)', 'value': 'optimization'}
                        ],
                        value='reflux',
                        clearable=False,
                        style={'marginBottom': '1rem'}
                    ),

                    dbc.Button("RUN STUDY",
                              id='run-study-btn',
                              size='lg',
                              style={
                                  'width': '100%',
                                  'backgroundColor': COLORS['primary'],
                                  'border': 'none',
                                  'borderRadius': '0',
                                  'padding': '1rem',
                                  'fontWeight': '800',
                                  'letterSpacing': '2px',
                                  'fontSize': '0.9rem',
                                  'marginTop': '1rem'
                              }),

                    html.Div(id='study-status', style={'marginTop': '1rem'})

                ], md=3, style={
                    'backgroundColor': COLORS['card_bg'],
                    'padding': '2rem',
                    'border': f'1px solid {COLORS["input_border"]}'
                }),

                dbc.Col([
                    html.Div(id='parametric-results',
                            children=html.P("Select study type and run to see results",
                                          style={'textAlign': 'center', 'padding': '3rem',
                                                'color': COLORS['text_secondary']}))
                ], md=9)
            ])

        ], fluid=True, style={'padding': '3rem 2rem'})
    ])


# Main layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='calculation-store'),
    dcc.Store(id='compound-store'),  # Store selected compounds
    dcc.Store(id='parametric-store'),  # Store parametric study data
    navbar(),
    html.Div(id='page-content', style={'minHeight': '80vh', 'backgroundColor': COLORS['background']})
], style={'backgroundColor': COLORS['background']})
