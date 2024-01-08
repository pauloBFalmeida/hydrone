import numpy as np

def F_ProFac(L, B, C_B, C_P, C_M, T_F, T_A, LCB, S_APP, S, apk1, apk2, C_F, C_A, Cstern, D, AEdAO, PdD, zP):
# F_ProFac - Computation of the propulsion factors
    T_M = (T_A + T_F) / 2

    apk = apk1 + (apk2 - apk1) * S_APP / S

    C_V = apk * C_F + C_A  # Viscous resistance coefficient

    if zP == 1:
        # Wake Fraction
        BdT_A = B / T_A
        if BdT_A < 5:
            c8 = B * S / (L * D * T_A)
        else:
            c8 = S * (7 * B / T_A - 25) / (L * D * (B / T_A - 3))

        if c8 < 28:
            c9 = c8
        else:
            c9 = 32 - 16 / (c8 - 24)

        T_AdD = T_A / D
        if T_AdD < 2:
            c11 = T_AdD
        else:
            c11 = 0.0833333 * T_AdD**3 + 1.33333

        if C_P < 0.7:
            c19 = 0.12997 / (0.95 - C_B) - 0.11056 / (0.95 - C_P)
        else:
            c19 = 0.18567 / (1.3571 - C_M) - 0.71276 + 0.38648 * C_P

        c20 = 1 + 0.015 * Cstern

        C_P1 = 1.45 * C_P - 0.315 - 0.0225 * LCB

        w = c9 * c20 * C_V * L / T_A * (0.050776 + 0.93405 * c11 * C_V / (1 - C_P1)) + 0.27915 * c20 * \
            (B / (L * (1 - C_P1)))**0.5 + c19 * c20

        # Thrust Deduction Factor
        t = 0.25014 * (B / L)**0.28956 * ((B * T_M)**0.5 / D)**0.2624 / (1 - C_P + 0.0225 * LCB)**\
            0.01762 + 0.0015 * Cstern

        # Relative-Rotative Efficiency
        etaR = 0.9922 - 0.05908 * AEdAO + 0.07424 * (C_P - 0.0225 * LCB)
    elif zP == 2:
        w = 0.3095 * C_B + 10 * C_V * C_B - 0.23 * D / (B * T_M)**0.5
        t = 0.325 * C_B - 0.1885 * D / (B * T_M)**0.5
        etaR = 0.9737 + 0.111 * (C_P - 0.0225 * LCB) - 0.06325 * PdD
    else:
        raise ValueError('The number of propellers must be equal to 1 or 2 only!')

    return t, w, etaR
