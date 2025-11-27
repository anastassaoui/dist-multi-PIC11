"""
Plotly figure generation for distillation visualizations
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
from dash import html


def create_material_balance_figure(results, z_F, compound_names, F):
    """Create material balance bar charts"""
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
    """Create composition profiles chart"""
    fig = go.Figure()

    # Dynamic colors based on number of components
    n_comp = len(compound_names)
    if n_comp == 2:
        colors = ['#000000', '#666666']
    elif n_comp == 3:
        colors = ['#000000', '#333333', '#666666']
    elif n_comp == 4:
        colors = ['#000000', '#222222', '#444444', '#666666']
    else:
        colors = ['#000000', '#1a1a1a', '#333333', '#4d4d4d', '#666666']

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
    """Create temperature profile chart"""
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
    """Create Gilliland correlation chart"""
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
    """Create design summary table"""
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
