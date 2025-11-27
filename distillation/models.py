"""
Chemical compound models with thermodynamic properties
"""

from thermo.chemical import Chemical


class Compound:
    """
    Représente un composé chimique avec ses propriétés thermodynamiques
    """

    def __init__(self, name):
        """
        Initialise le composé depuis la base de données thermo

        Parameters:
        -----------
        name : str
            Nom du composé (ex: 'benzene', 'toluene', 'xylene')
        """
        self.name = name
        try:
            self.chem = Chemical(name)

            # Propriétés critiques
            self.Tc = self.chem.Tc  # Température critique (K)
            self.Pc = self.chem.Pc  # Pression critique (Pa)
            self.omega = self.chem.omega  # Facteur acentrique

            # Propriétés normales
            self.Tb = self.chem.Tb  # Température d'ébullition normale (K)
            self.MW = self.chem.MW  # Masse molaire (g/mol)

            # Pour l'enthalpie
            self.Hfus = self.chem.Hfusm if self.chem.Hfusm else 0  # Enthalpie de fusion

        except Exception as e:
            raise ValueError(f"Impossible de charger le composé '{name}': {e}")

    def vapor_pressure(self, T):
        """
        Calcule la pression de vapeur saturante à la température T

        Parameters:
        -----------
        T : float
            Température (K)

        Returns:
        --------
        Psat : float
            Pression de vapeur saturante (Pa)
        """
        self.chem.T = T
        Psat = self.chem.Psat
        return Psat if Psat else 1e-10  # Éviter division par zéro

    def K_value(self, T, P):
        """
        Calcule le coefficient de partage K = y/x

        Pour un mélange idéal: K = Psat(T) / P

        Parameters:
        -----------
        T : float
            Température (K)
        P : float
            Pression (Pa)

        Returns:
        --------
        K : float
            Coefficient de partage
        """
        Psat = self.vapor_pressure(T)
        return Psat / P

    def enthalpy_liquid(self, T, T_ref=298.15):
        """
        Calcule l'enthalpie du liquide à T par rapport à T_ref

        Parameters:
        -----------
        T : float
            Température (K)
        T_ref : float
            Température de référence (K)

        Returns:
        --------
        H_L : float
            Enthalpie molaire liquide (J/mol)
        """
        self.chem.T = T
        try:
            # Utiliser la capacité calorifique pour l'intégration
            Cp_liquid = self.chem.Cplm  # J/(mol·K)
            H_L = Cp_liquid * (T - T_ref)
            return H_L
        except:
            # Approximation simple si Cp n'est pas disponible
            return 4.18 * self.MW * (T - T_ref)  # Approximation eau

    def enthalpy_vapor(self, T, T_ref=298.15):
        """
        Calcule l'enthalpie de la vapeur à T par rapport à T_ref

        Parameters:
        -----------
        T : float
            Température (K)
        T_ref : float
            Température de référence (K)

        Returns:
        --------
        H_V : float
            Enthalpie molaire vapeur (J/mol)
        """
        H_L = self.enthalpy_liquid(T, T_ref)
        self.chem.T = T
        Hvap = self.chem.Hvap if self.chem.Hvap else 40000  # J/mol (valeur typique)
        return H_L + Hvap

    def __repr__(self):
        return f"Compound(name='{self.name}', Tb={self.Tb-273.15:.1f}°C, MW={self.MW:.2f})"
