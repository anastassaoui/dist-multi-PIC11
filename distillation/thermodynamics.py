"""
Thermodynamic package for VLE calculations and mixture properties
"""

import numpy as np
from scipy.optimize import fsolve


class ThermodynamicPackage:
    """
    Package thermodynamique pour calculs d'équilibre et propriétés de mélanges
    """

    def __init__(self, compounds):
        """
        Parameters:
        -----------
        compounds : list of Compound objects
            Liste des composés du mélange
        """
        self.compounds = compounds
        self.n_comp = len(compounds)
        self.compound_names = [c.name for c in compounds]

    def K_values(self, T, P, x=None):
        """
        Calcule tous les coefficients K à T et P

        Parameters:
        -----------
        T : float
            Température (K)
        P : float
            Pression (Pa)
        x : array, optional
            Compositions liquides (pour modèles non-idéaux)

        Returns:
        --------
        K : ndarray
            Coefficients K pour tous les composés
        """
        K = np.array([comp.K_value(T, P) for comp in self.compounds])
        return K

    def relative_volatilities(self, T, P, ref_index=-1):
        """
        Calcule les volatilités relatives par rapport au composé de référence

        Parameters:
        -----------
        T : float
            Température (K)
        P : float
            Pression (Pa)
        ref_index : int
            Index du composé de référence (par défaut: le plus lourd)

        Returns:
        --------
        alpha : ndarray
            Volatilités relatives
        """
        K = self.K_values(T, P)
        K_ref = K[ref_index]
        alpha = K / K_ref
        return alpha

    def bubble_temperature(self, P, x, T_guess=None, tol=1e-6, max_iter=100):
        """
        Calcule la température de bulle pour une composition liquide donnée

        Résout: sum(K_i * x_i) = 1

        Parameters:
        -----------
        P : float
            Pression (Pa)
        x : array
            Composition liquide (fractions molaires)
        T_guess : float, optional
            Estimation initiale de température (K)

        Returns:
        --------
        T_bubble : float
            Température de bulle (K)
        y : array
            Composition vapeur à l'équilibre
        """
        x = np.array(x)

        if T_guess is None:
            # Estimation: moyenne pondérée des Tb
            T_guess = np.sum([x[i] * self.compounds[i].Tb for i in range(self.n_comp)])

        def equation(T):
            K = self.K_values(T, P)
            return np.sum(K * x) - 1.0

        try:
            T_bubble = fsolve(equation, T_guess, full_output=False)[0]
            K = self.K_values(T_bubble, P)
            y = K * x
            y = y / np.sum(y)  # Normalisation
            return T_bubble, y
        except:
            # Silent - no convergence warnings
            return T_guess, x.copy()

    def dew_temperature(self, P, y, T_guess=None, tol=1e-6, max_iter=100):
        """
        Calcule la température de rosée pour une composition vapeur donnée

        Résout: sum(y_i / K_i) = 1

        Parameters:
        -----------
        P : float
            Pression (Pa)
        y : array
            Composition vapeur (fractions molaires)
        T_guess : float, optional
            Estimation initiale de température (K)

        Returns:
        --------
        T_dew : float
            Température de rosée (K)
        x : array
            Composition liquide à l'équilibre
        """
        y = np.array(y)

        if T_guess is None:
            # Estimation: moyenne pondérée des Tb
            T_guess = np.sum([y[i] * self.compounds[i].Tb for i in range(self.n_comp)])

        def equation(T):
            K = self.K_values(T, P)
            return np.sum(y / K) - 1.0

        try:
            T_dew = fsolve(equation, T_guess, full_output=False)[0]
            K = self.K_values(T_dew, P)
            x = y / K
            x = x / np.sum(x)  # Normalisation
            return T_dew, x
        except:
            # Silent - no convergence warnings
            return T_guess, y.copy()

    def mixture_enthalpy_liquid(self, T, x, T_ref=298.15):
        """
        Calcule l'enthalpie du mélange liquide

        Hypothèse: mélange idéal (pas d'enthalpie de mélange)

        Parameters:
        -----------
        T : float
            Température (K)
        x : array
            Composition molaire liquide
        T_ref : float
            Température de référence (K)

        Returns:
        --------
        H_L : float
            Enthalpie molaire du mélange liquide (J/mol)
        """
        H_L = np.sum([x[i] * self.compounds[i].enthalpy_liquid(T, T_ref)
                     for i in range(self.n_comp)])
        return H_L

    def mixture_enthalpy_vapor(self, T, y, T_ref=298.15):
        """
        Calcule l'enthalpie du mélange vapeur

        Parameters:
        -----------
        T : float
            Température (K)
        y : array
            Composition molaire vapeur
        T_ref : float
            Température de référence (K)

        Returns:
        --------
        H_V : float
            Enthalpie molaire du mélange vapeur (J/mol)
        """
        H_V = np.sum([y[i] * self.compounds[i].enthalpy_vapor(T, T_ref)
                     for i in range(self.n_comp)])
        return H_V

    def print_properties(self, T, P):
        """
        Affiche les propriétés à T et P
        """
        print(f"\n{'PROPRIÉTÉS À T={T-273.15:.1f}°C, P={P/1e5:.3f} bar':-^80}")
        print(f"{'Composé':<15} {'Tb (°C)':<12} {'Psat (kPa)':<15} {'K':<12} {'α':<12}")
        print("-" * 80)

        K = self.K_values(T, P)
        alpha = self.relative_volatilities(T, P)

        for i, comp in enumerate(self.compounds):
            Psat = comp.vapor_pressure(T)
            print(f"{comp.name:<15} {comp.Tb-273.15:<12.2f} {Psat/1000:<15.2f} "
                  f"{K[i]:<12.4f} {alpha[i]:<12.4f}")
        print("-" * 80)
