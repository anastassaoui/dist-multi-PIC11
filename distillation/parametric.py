"""
Parametric Studies for Distillation Column Design
Effect of Reflux Ratio and Pressure on Column Performance
"""

import numpy as np
from .shortcut import ShortcutDistillation


class ParametricStudy:
    """
    Perform parametric studies on distillation column design
    """

    def __init__(self, thermo_package, F, z_F, P_base=101325):
        """
        Initialize parametric study

        Parameters
        ----------
        thermo_package : ThermodynamicPackage
            Thermodynamic package with compounds
        F : float
            Feed flowrate (kmol/h)
        z_F : array
            Feed composition (mole fractions)
        P_base : float
            Base operating pressure (Pa)
        """
        self.thermo = thermo_package
        self.F = F
        self.z_F = np.array(z_F)
        self.P_base = P_base

    def reflux_study(self, R_range=None, recovery_LK_D=0.95, recovery_HK_B=0.95,
                     q=1.0, efficiency=0.70):
        """
        Study effect of reflux ratio on number of stages and energy

        Parameters
        ----------
        R_range : array or None
            Reflux ratios to study (default: 1.1*Rmin to 5.0*Rmin, 20 points)
        recovery_LK_D : float
            Recovery of light key in distillat
        recovery_HK_B : float
            Recovery of heavy key in bottoms
        q : float
            Feed quality
        efficiency : float
            Stage efficiency

        Returns
        -------
        dict : Study results with R_values, N_theoretical, N_real, energy
        """
        # Get base design to find Rmin
        shortcut = ShortcutDistillation(self.thermo, self.F, self.z_F, self.P_base)
        base_results = shortcut.complete_shortcut_design(
            recovery_LK_D=recovery_LK_D,
            recovery_HK_B=recovery_HK_B,
            R_factor=1.3,
            q=q,
            efficiency=efficiency
        )

        R_min = base_results['R_min']

        # Generate reflux ratios if not provided
        if R_range is None:
            R_range = np.linspace(1.1 * R_min, 5.0 * R_min, 20)

        N_theoretical = []
        N_real = []
        R_factors = []
        QC_values = []
        QR_values = []

        for R in R_range:
            R_factor = R / R_min

            results = shortcut.complete_shortcut_design(
                recovery_LK_D=recovery_LK_D,
                recovery_HK_B=recovery_HK_B,
                R_factor=R_factor,
                q=q,
                efficiency=efficiency
            )

            N_theoretical.append(results['N_theoretical'])
            N_real.append(results['N_real'])
            R_factors.append(R_factor)

            # Estimate energy (simplified - based on reflux and distillate flow)
            D = results.get('D', self.F * 0.5)
            # Assume average latent heat of 35 kJ/mol
            Lambda_avg = 35000  # J/mol
            QC = -(R + 1) * D * Lambda_avg / 1000  # kW (negative = heat removed)
            QR = abs(QC)  # Approximate (QR slightly higher in reality)

            QC_values.append(QC)
            QR_values.append(QR)

        return {
            'R_values': R_range.tolist(),
            'R_min': R_min,
            'R_factors': R_factors,
            'N_theoretical': N_theoretical,
            'N_real': N_real,
            'QC': QC_values,
            'QR': QR_values,
            'total_energy': [abs(qc) + abs(qr) for qc, qr in zip(QC_values, QR_values)]
        }

    def pressure_study(self, P_range=None, recovery_LK_D=0.95, recovery_HK_B=0.95,
                       R_factor=1.3, q=1.0, efficiency=0.70):
        """
        Study effect of operating pressure on separation

        Parameters
        ----------
        P_range : array or None
            Pressures to study in Pa (default: 0.5 to 2.0 atm, 10 points)
        recovery_LK_D : float
            Recovery of light key in distillat
        recovery_HK_B : float
            Recovery of heavy key in bottoms
        R_factor : float
            Reflux ratio factor
        q : float
            Feed quality
        efficiency : float
            Stage efficiency

        Returns
        -------
        dict : Study results with P_values, alpha_avg, N_min, temperatures, energy
        """
        # Generate pressures if not provided (0.5 to 2.0 atm)
        if P_range is None:
            P_range = np.linspace(0.5 * 101325, 2.0 * 101325, 10)

        alpha_avg_values = []
        N_min_values = []
        N_theoretical_values = []
        N_real_values = []
        T_top_values = []
        T_bottom_values = []
        QC_values = []
        QR_values = []

        for P in P_range:
            shortcut = ShortcutDistillation(self.thermo, self.F, self.z_F, P)

            try:
                results = shortcut.complete_shortcut_design(
                    recovery_LK_D=recovery_LK_D,
                    recovery_HK_B=recovery_HK_B,
                    R_factor=R_factor,
                    q=q,
                    efficiency=efficiency
                )

                alpha_avg_values.append(results.get('alpha_avg', 1.0))
                N_min_values.append(results['N_min'])
                N_theoretical_values.append(results['N_theoretical'])
                N_real_values.append(results['N_real'])

                # Estimate temperatures
                try:
                    T_top, _ = self.thermo.bubble_temperature(P, results['x_D'])
                    T_bot, _ = self.thermo.bubble_temperature(P, results['x_B'])
                    T_top_values.append(T_top - 273.15)  # Convert to Celsius
                    T_bottom_values.append(T_bot - 273.15)
                except:
                    T_top_values.append(80.0)  # Placeholder
                    T_bottom_values.append(140.0)

                # Estimate energy
                D = results.get('D', self.F * 0.5)
                R = results['R_min'] * R_factor
                Lambda_avg = 35000  # J/mol
                QC = -(R + 1) * D * Lambda_avg / 1000
                QR = abs(QC)

                QC_values.append(QC)
                QR_values.append(QR)

            except Exception as e:
                # If calculation fails at this pressure, append None
                alpha_avg_values.append(None)
                N_min_values.append(None)
                N_theoretical_values.append(None)
                N_real_values.append(None)
                T_top_values.append(None)
                T_bottom_values.append(None)
                QC_values.append(None)
                QR_values.append(None)

        return {
            'P_values': (P_range / 101325).tolist(),  # Convert to atm
            'P_values_Pa': P_range.tolist(),
            'alpha_avg': alpha_avg_values,
            'N_min': N_min_values,
            'N_theoretical': N_theoretical_values,
            'N_real': N_real_values,
            'T_top': T_top_values,
            'T_bottom': T_bottom_values,
            'QC': QC_values,
            'QR': QR_values,
            'total_energy': [abs(qc) + abs(qr) if qc and qr else None
                           for qc, qr in zip(QC_values, QR_values)]
        }

    def optimize_reflux(self, recovery_LK_D=0.95, recovery_HK_B=0.95,
                       q=1.0, efficiency=0.70, cost_energy=0.05, cost_stage=10000):
        """
        Find optimal reflux ratio that minimizes total annualized cost (TAC)

        Parameters
        ----------
        recovery_LK_D : float
            Recovery of light key in distillat
        recovery_HK_B : float
            Recovery of heavy key in bottoms
        q : float
            Feed quality
        efficiency : float
            Stage efficiency
        cost_energy : float
            Cost of energy ($/kWh)
        cost_stage : float
            Cost per stage ($)

        Returns
        -------
        dict : Optimal R, N, and costs
        """
        # Perform reflux study
        study = self.reflux_study(
            R_range=None,
            recovery_LK_D=recovery_LK_D,
            recovery_HK_B=recovery_HK_B,
            q=q,
            efficiency=efficiency
        )

        # Calculate TAC for each reflux ratio
        TAC_values = []
        operating_hours = 8000  # hours/year
        CRF = 0.15  # Capital recovery factor (approximate)

        for i, (N, Q_total) in enumerate(zip(study['N_real'], study['total_energy'])):
            # Capital cost (stages)
            capital_cost = N * cost_stage

            # Operating cost (energy)
            operating_cost = abs(Q_total) * cost_energy * operating_hours

            # Total annualized cost
            TAC = capital_cost * CRF + operating_cost
            TAC_values.append(TAC)

        # Find minimum
        optimal_idx = np.argmin(TAC_values)

        return {
            'R_optimal': study['R_values'][optimal_idx],
            'R_factor_optimal': study['R_factors'][optimal_idx],
            'N_optimal': study['N_real'][optimal_idx],
            'TAC_optimal': TAC_values[optimal_idx],
            'R_values': study['R_values'],
            'TAC_values': TAC_values,
            'capital_costs': [N * cost_stage * CRF for N in study['N_real']],
            'operating_costs': [abs(Q) * cost_energy * operating_hours for Q in study['total_energy']]
        }
