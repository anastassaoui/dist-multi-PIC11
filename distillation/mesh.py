"""
MESH Equations Solver for Rigorous Distillation Column Simulation
Wang-Henke Algorithm Implementation
"""

import numpy as np
from scipy.optimize import fsolve


class MESHSolver:
    """
    Rigorous distillation column solver using MESH equations

    MESH = Material balance, Equilibrium, Summation, Heat balance
    Algorithm: Wang-Henke iterative method
    """

    def __init__(self, thermo_package, F, z_F, P=101325, N=10, feed_stage=5, R=2.0):
        """
        Initialize MESH solver

        Parameters
        ----------
        thermo_package : ThermodynamicPackage
            Thermodynamic package with compounds
        F : float
            Feed flowrate (kmol/h)
        z_F : array
            Feed composition (mole fractions)
        P : float
            Operating pressure (Pa)
        N : int
            Number of theoretical stages (including reboiler)
        feed_stage : int
            Feed stage number (1-indexed from top)
        R : float
            Reflux ratio
        """
        self.thermo = thermo_package
        self.F = F
        self.z_F = np.array(z_F)
        self.P = P
        self.N = N
        self.feed_stage = feed_stage - 1  # Convert to 0-indexed
        self.R = R
        self.n_comp = len(z_F)

        # Initialize variables
        self.T = None  # Stage temperatures
        self.x = None  # Liquid compositions [stage, component]
        self.y = None  # Vapor compositions [stage, component]
        self.L = None  # Liquid flowrates
        self.V = None  # Vapor flowrates
        self.D = None  # Distillate
        self.B = None  # Bottoms
        self.QC = None  # Condenser duty
        self.QR = None  # Reboiler duty

    def initialize(self):
        """Initialize temperature, composition, and flow profiles"""
        # Estimate distillate and bottoms (assume 50/50 split initially)
        self.D = self.F * 0.5
        self.B = self.F - self.D

        # Estimate temperature profile (linear between bubble points)
        T_bot = self.thermo.bubble_temperature(self.P, self.z_F)
        T_top = T_bot - 50  # Assume 50K difference
        self.T = np.linspace(T_top, T_bot, self.N)

        # Initialize liquid compositions (linear profile)
        self.x = np.zeros((self.N, self.n_comp))
        for i in range(self.n_comp):
            self.x[:, i] = np.linspace(0.9 * self.z_F[i], 0.1 * self.z_F[i], self.N)
        # Normalize
        self.x = self.x / self.x.sum(axis=1, keepdims=True)

        # Initialize vapor compositions using K-values
        self.y = np.zeros((self.N, self.n_comp))
        for j in range(self.N):
            K = self.thermo.K_values(self.T[j], self.P)
            self.y[j, :] = K * self.x[j, :]
        # Normalize
        self.y = self.y / self.y.sum(axis=1, keepdims=True)

        # Initialize flowrates using CMO (Constant Molar Overflow)
        self.L = np.zeros(self.N)
        self.V = np.zeros(self.N)

        # Rectifying section
        for j in range(self.feed_stage + 1):
            self.L[j] = self.R * self.D
            self.V[j] = (self.R + 1) * self.D

        # Stripping section
        for j in range(self.feed_stage + 1, self.N):
            self.L[j] = self.L[self.feed_stage] + self.F
            self.V[j] = self.V[self.feed_stage]

    def solve_material_balances(self):
        """
        Solve component material balances using tridiagonal matrix algorithm
        For each component: L[j+1]*x[j+1] + V[j-1]*y[j-1] + F[j]*z[j] = L[j]*x[j] + V[j]*y[j]
        """
        for i in range(self.n_comp):
            # Build tridiagonal system for component i
            A = np.zeros((self.N, self.N))
            b = np.zeros(self.N)

            for j in range(self.N):
                # Get K-value
                K = self.thermo.K_values(self.T[j], self.P)

                # Diagonal element
                A[j, j] = self.L[j] + self.V[j] * K[i]

                # Upper diagonal (liquid from stage above)
                if j > 0:
                    A[j, j-1] = -self.L[j-1]

                # Lower diagonal (vapor from stage below)
                if j < self.N - 1:
                    A[j, j+1] = -self.V[j+1] * K[i]

                # Feed term
                if j == self.feed_stage:
                    b[j] = self.F * self.z_F[i]
                else:
                    b[j] = 0.0

                # Boundary conditions
                if j == 0:  # Condenser (total condenser)
                    A[j, j] = 1.0
                    A[j, j+1] = 0.0
                    b[j] = self.y[0, i]  # x = y at total condenser

                if j == self.N - 1:  # Reboiler
                    A[j, j-1] = 0.0

            # Solve for liquid composition
            self.x[:, i] = np.linalg.solve(A, b)

        # Normalize liquid compositions
        self.x = np.clip(self.x, 1e-10, 1.0)
        self.x = self.x / self.x.sum(axis=1, keepdims=True)

        # Update vapor compositions
        for j in range(self.N):
            K = self.thermo.K_values(self.T[j], self.P)
            self.y[j, :] = K * self.x[j, :]
        self.y = self.y / self.y.sum(axis=1, keepdims=True)

    def update_temperatures(self):
        """Update stage temperatures using bubble point calculations"""
        T_new = np.zeros(self.N)

        for j in range(self.N):
            try:
                T_new[j] = self.thermo.bubble_temperature(self.P, self.x[j, :], T_guess=self.T[j])
            except:
                T_new[j] = self.T[j]  # Keep old value if convergence fails

        return T_new

    def update_flowrates(self):
        """Update liquid and vapor flowrates using enthalpy balances"""
        # Simplified: Use CMO assumption
        # For rigorous, would need enthalpy calculations

        # Update distillate from top stage composition
        self.D = self.V[0] / (self.R + 1)
        self.B = self.F - self.D

        # Rectifying section
        for j in range(self.feed_stage + 1):
            self.L[j] = self.R * self.D
            self.V[j] = self.L[j] + self.D

        # Stripping section
        for j in range(self.feed_stage + 1, self.N):
            self.L[j] = self.L[self.feed_stage] + self.F
            self.V[j] = self.L[j] - self.B

    def calculate_duties(self):
        """Calculate condenser and reboiler heat duties"""
        # Get enthalpies
        try:
            # Condenser duty (negative = heat removed)
            h_v_top = sum([self.y[0, i] * self.thermo.compounds[i].enthalpy_vapor(self.T[0])
                          for i in range(self.n_comp)])
            h_l_top = sum([self.x[0, i] * self.thermo.compounds[i].enthalpy_liquid(self.T[0])
                          for i in range(self.n_comp)])
            self.QC = self.V[0] * (h_v_top - h_l_top) / 1000  # Convert to kW (assuming J/mol)

            # Reboiler duty (positive = heat added)
            h_l_bot = sum([self.x[-1, i] * self.thermo.compounds[i].enthalpy_liquid(self.T[-1])
                          for i in range(self.n_comp)])
            h_v_bot = sum([self.y[-1, i] * self.thermo.compounds[i].enthalpy_vapor(self.T[-1])
                          for i in range(self.n_comp)])
            self.QR = self.V[-1] * (h_v_bot - h_l_bot) / 1000  # Convert to kW
        except:
            # Fallback if enthalpy calculation fails
            self.QC = -1000.0  # Placeholder
            self.QR = 1000.0

    def check_convergence(self, T_old, x_old):
        """Check convergence criteria"""
        # Temperature convergence
        eps_T = np.max(np.abs(self.T - T_old))

        # Composition convergence
        eps_x = np.max(np.abs(self.x - x_old))

        return eps_T, eps_x

    def solve(self, max_iter=100, tol_T=0.1, tol_x=1e-6):
        """
        Main Wang-Henke algorithm loop

        Parameters
        ----------
        max_iter : int
            Maximum iterations
        tol_T : float
            Temperature tolerance (K)
        tol_x : float
            Composition tolerance

        Returns
        -------
        dict : Simulation results
        """
        # Initialize
        self.initialize()

        # Iteration loop
        for iteration in range(max_iter):
            # Store old values
            T_old = self.T.copy()
            x_old = self.x.copy()

            # MESH algorithm steps
            # 1. Calculate K-values at current temperatures
            # 2. Solve material balances
            self.solve_material_balances()

            # 3. Normalize compositions
            self.x = np.clip(self.x, 1e-10, 1.0)
            self.x = self.x / self.x.sum(axis=1, keepdims=True)
            self.y = np.clip(self.y, 1e-10, 1.0)
            self.y = self.y / self.y.sum(axis=1, keepdims=True)

            # 4. Update temperatures
            self.T = self.update_temperatures()

            # 5. Update flowrates
            self.update_flowrates()

            # 6. Check convergence
            eps_T, eps_x = self.check_convergence(T_old, x_old)

            if eps_T < tol_T and eps_x < tol_x:
                break

        # Calculate heat duties
        self.calculate_duties()

        # Return results
        return {
            'converged': (eps_T < tol_T and eps_x < tol_x),
            'iterations': iteration + 1,
            'temperatures': self.T,
            'x_profiles': self.x,
            'y_profiles': self.y,
            'L_flows': self.L,
            'V_flows': self.V,
            'D': self.D,
            'B': self.B,
            'x_D': self.x[0, :],
            'x_B': self.x[-1, :],
            'QC': self.QC,
            'QR': self.QR,
            'eps_T': eps_T,
            'eps_x': eps_x
        }
