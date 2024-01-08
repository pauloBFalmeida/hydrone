import numpy as np
from math import pi, log10

def F_ProPer_return_constraints(R, Vs, t, w, etaR, zP, Z, D, PdD, AEdAO, hk, Ta):
    # Water input data
    rho = 999  # [kg/m^3] water density
    nu = 1.1390e-6  # [m^2/s] kinematic viscosity
    g = 9.80665  # [m/s^2] gravity acceleration
    patm = 101325  # [Pa] atmospheric pressure
    pv = 1704  # [Pa] vapour pressure of seawater (15 °C)

    # Unit conversion
    R = R * 1000 / zP  # [N]
    Vs = Vs * 1852 / 3600  # [m/s]

    # Preliminary calculations
    T = R / (1 - t)  # [N] thrust
    Va = Vs * (1 - w)  # [m/s] velocity of advance
    C075R = 2.073 * AEdAO * D / Z  # Propeller chord length at 0.75 of radius [m]

    # Constants for calculation of thrust coefficient polynomial KtM = [Ct s t u v]
    KtM = np.array([
        [0.00880496, 0, 0, 0, 0],
        [-0.204554, 1, 0, 0, 0],
        [0.166351, 0, 1, 0, 0],
        [0.158114, 0, 2, 0, 0],
        [-0.147581, 2, 0, 1, 0],
        [-0.481497, 1, 1, 1, 0],
        [0.415437, 0, 2, 1, 0],
        [0.0144043, 0, 0, 0, 1],
        [-0.0530054, 2, 0, 0, 1],
        [0.0143481, 0, 1, 0, 1],
        [0.0606826, 1, 1, 0, 1],
        [-0.0125894, 0, 0, 1, 1],
        [0.0109689, 1, 0, 1, 1],
        [-0.133698, 0, 3, 0, 0],
        [0.00638407, 0, 6, 0, 0],
        [-0.00132718, 2, 6, 0, 0],
        [0.168496, 3, 0, 1, 0],
        [-0.0507214, 0, 0, 2, 0],
        [0.0854559, 2, 0, 2, 0],
        [-0.0504475, 3, 0, 2, 0],
        [0.010465, 1, 6, 2, 0],
        [-0.00648272, 2, 6, 2, 0],
        [-0.00841728, 0, 3, 0, 1],
        [0.0168424, 1, 3, 0, 1],
        [-0.00102296, 3, 3, 0, 1],
        [-0.0317791, 0, 3, 1, 1],
        [0.018604, 1, 0, 2, 1],
        [-0.00410798, 0, 2, 2, 1],
        [-0.000606848, 0, 0, 0, 2],
        [-0.0049819, 1, 0, 0, 2],
        [0.0025983, 2, 0, 0, 2],
        [-0.000560528, 3, 0, 0, 2],
        [-0.00163652, 1, 2, 0, 2],
        [-0.000328787, 1, 6, 0, 2],
        [0.000116502, 2, 6, 0, 2],
        [0.000690904, 0, 0, 1, 2],
        [0.00421749, 0, 3, 1, 2],
        [0.0000565229, 3, 6, 1, 2],
        [-0.00146564, 0, 3, 2, 2]
    ])

    # Finding J in order to have Kt (thrust coef.) = Kts (ship thrust coef.)
    J = 0
    Kt = 1
    Kts = 0
    Kq = 0

    while Kt > Kts:
        J += 0.1
        Kt = 0

        # for i in range(39):  # 39 is the number of rows in KtM
        for i in range(len(KtM)):  # 39 is the number of rows in KtM
            Kt += KtM[i, 0] * J**KtM[i, 1] * PdD**KtM[i, 2] * AEdAO**KtM[i, 3] * Z**KtM[i, 4]

        Kts = J**2 * T / (rho * Va**2 * D**2)

    while Kts > Kt:
        J -= 0.00001
        Kt = 0

        for i in range(39):  # 39 is the number of rows in KtM
            Kt += KtM[i, 0] * J**KtM[i, 1] * PdD**KtM[i, 2] * AEdAO**KtM[i, 3] * Z**KtM[i, 4]

        Kts = J**2 * T / (rho * Va**2 * D**2)

    # eKt = (Kts - Kt) / Kt  # calculation of the residual error

    # Propeller speed calculation
    n = Va / (J * D)

    # Reynolds number
    Rn = (Va**2 + (0.75 * pi * D * n)**2)**0.5 * C075R / nu  # Reynolds number

    # Correction of Kt and Kq for Rn > 2e06
    if Rn > 2e6:
        eRn = 1
        while eRn > 0.0001:
            deltaKt = 0.000353485 \
                      - 0.00333758 * AEdAO * J**2 \
                      - 0.00478125 * AEdAO * PdD * J \
                      + 0.000257792 * (log10(Rn) - 0.301)**2 * AEdAO * J**2 \
                      + 0.0000643192 * (log10(Rn) - 0.301) * PdD**6 * J**2 \
                      - 0.0000110636 * (log10(Rn) - 0.301)**2 * PdD**6 * J**2 \
                      - 0.0000276305 * (log10(Rn) - 0.301)**2 * Z * AEdAO * J**2 \
                      + 0.0000954 * (log10(Rn) - 0.301) * Z * AEdAO * PdD * J \
                      + 0.0000032049 * (log10(Rn) - 0.301) * Z**2 * AEdAO * PdD**3 * J

            deltaKq = -0.000591412 \
                      + 0.00696898 * PdD \
                      - 0.0000666654 * Z * PdD**6 \
                      + 0.0160818 * AEdAO**2 \
                      - 0.000938091 * (log10(Rn) - 0.301) * PdD \
                      - 0.00059593 * (log10(Rn) - 0.301) * PdD**2 \
                      + 0.0000782099 * (log10(Rn) - 0.301)**2 * PdD**2 \
                      + 0.0000052199 * (log10(Rn) - 0.301) * Z * AEdAO * J**2 \
                      - 0.00000088528 * (log10(Rn) - 0.301)**2 * Z * AEdAO * PdD * J \
                      + 0.0000230171 * (log10(Rn) - 0.301) * Z * PdD**6 \
                      - 0.00000184341 * (log10(Rn) - 0.301)**2 * Z * PdD**6 \
                      - 0.00400252 * (log10(Rn) - 0.301) * AEdAO**2 \
                      + 0.000220915 * (log10(Rn) - 0.301)**2 * AEdAO**2

            # Finding J in order to have Kt (thrust coef.) = Kts (ship thrust coef.)
            J = 0
            Kt = 1
            Kts = 0
            Kq = deltaKq

            while Kt > Kts:
                J += 0.1
                Kt = deltaKt
                for i in range(39):  # 39 is the number of rows in KtM
                    Kt += KtM[i, 0] * J**KtM[i, 1] * PdD**KtM[i, 2] * AEdAO**KtM[i, 3] * Z**KtM[i, 4]

                Kts = J**2 * T / (rho * Va**2 * D**2)

            while Kts > Kt:
                J -= 0.00001
                Kt = deltaKt
                for i in range(39):  # 39 is the number of rows in KtM
                    Kt += KtM[i, 0] * J**KtM[i, 1] * PdD**KtM[i, 2] * AEdAO**KtM[i, 3] * Z**KtM[i, 4]

                Kts = J**2 * T / (rho * Va**2 * D**2)

            # Propeller speed calculation
            n = Va / (J * D)

            # New Reynolds number
            RnN = ((Va ** 2) + (0.75 * pi * D * n) ** 2) ** 0.5 * C075R / nu
            eRn = abs(Rn - RnN) / Rn
            Rn = RnN

    # Constants for calculation of torque coef. polynomial
    KqM = [
        [0.00379368, 0, 0, 0, 0], [0.00886523, 2, 0, 0, 0], [-0.032241, 1, 1, 0, 0],
        [0.00344778, 0, 2, 0, 0], [-0.0408811, 0, 1, 1, 0], [-0.108009, 1, 1, 1, 0],
        [-0.0885381, 2, 1, 1, 0], [0.188561, 0, 2, 1, 0], [-0.00370871, 1, 0, 0, 1],
        [0.00513696, 0, 1, 0, 1], [0.0209449, 1, 1, 0, 1], [0.00474319, 2, 1, 0, 1],
        [-0.00723408, 2, 0, 1, 1], [0.00438388, 1, 1, 1, 1], [-0.0269403, 0, 2, 1, 1],
        [0.0558082, 3, 0, 1, 0], [0.0161886, 0, 3, 1, 0], [0.00318086, 1, 3, 1, 0],
        [0.015896, 0, 0, 2, 0], [0.0471729, 1, 0, 2, 0], [0.0196283, 3, 0, 2, 0],
        [-0.0502782, 0, 1, 2, 0], [-0.030055, 3, 1, 2, 0], [0.0417122, 2, 2, 2, 0],
        [-0.0397722, 0, 3, 2, 0], [-0.00350024, 0, 6, 2, 0], [-0.0106854, 3, 0, 0, 1],
        [0.00110903, 3, 3, 0, 1], [-0.000313912, 0, 6, 0, 1], [0.0035985, 3, 0, 1, 1],
        [-0.00142121, 0, 6, 1, 1], [-0.00383637, 1, 0, 2, 1], [0.0126803, 0, 2, 2, 1],
        [-0.00318278, 2, 3, 2, 1], [0.00334268, 0, 6, 2, 1], [-0.00183491, 1, 1, 0, 2],
        [0.000112451, 3, 2, 0, 2], [-0.0000297228, 3, 6, 0, 2], [0.000269551, 1, 0, 1, 2],
        [0.00083265, 2, 0, 1, 2], [0.00155334, 0, 2, 1, 2], [0.000302683, 0, 6, 1, 2],
        [-0.0001843, 0, 0, 2, 2], [-0.000425399, 0, 3, 2, 2], [0.0000869243, 3, 3, 2, 2],
        [-0.0004659, 0, 6, 2, 2], [0.0000554194, 1, 6, 2, 2]
    ]

    # Calculation of torque coefficient Kq
    for i in range(47):  # 47 is the number of rows in KqM
        Kq += KqM[i][0] * J**KqM[i][1] * PdD**KqM[i][2] * AEdAO**KqM[i][3] * Z**KqM[i][4]

    # Propeller torque
    Q = Kq * rho * n**2 * D**5  # [N*m]

    # Open water efficiency
    etaO = J * Kt / (2 * pi * Kq)

    # Open water power
    PO = 2 * pi * Q * n / 1000  # [kW]

    # Propeller angular speed
    n = n * 60  # [rpm]

    # # Shaft speed constraint
    # if n > 900 or n < 855:
    #    # print([D Z AEdAO PdD zP tmin075dD t075dD]);
    #     with open('constraints.txt', 'a') as fID:
    #         fID.write(f'{Vs * 3600 / 1852:.8f} {D} {Z} {AEdAO} {PdD} {zP} ShaftSpeed\n')
    #     raise ValueError('Shaft speed constraint has been reached!')


    # Strength constraint
    Dft = D * 3.280839895013123  # [ft] diameter
    PpHPdZ = PO / etaR * 1.341022 / Z  # [hp/blade] propeller power per blade
    Sc_psi = 19557  # [psi] maximum allowable stress

    # Dft = 20; PpHPdZ = 3312.5; Sc_psi = 6000; PdD = 1.166; n = 97.2; Z = 4;

    tmin075dD = (0.0028 + 0.21 * ((2375 - 1125 * PdD) * PpHPdZ / (4.123 * n * Dft**3 * (Sc_psi + Dft**2 * n**2 / 12788)))**(1 / 3))

    t075dD = 0.0185 - 0.00125 * Z

    # if t075dD < tmin075dD:
    # #     print([D Z AEdAO PdD zP tmin075dD t075dD]);
    #     print('Strength constraint reached')


    # Cavitation Constraint
    h = Ta - hk  # [m] distance from the centre of the propeller to water surface
    p0 = patm + rho * g * h  # [Pa] static pressure at the centre of the propeller

    sig07R = (p0 - pv) / (0.5 * rho * (Va**2 + (pi * 0.7 * n / 60 * D)**2))  # [] mean cavitation number at 0.7R

    AO = pi * D**2 / 4  # [m] disc area

    AE = AO * AEdAO  # [m] expanded area

    Ap = (1.067 - 0.229 * PdD) * AE  # [m] projected area for the propeller

    tal07R = T / (0.5 * rho * Ap * (Va**2 + (pi * 0.7 * n / 60 * D)**2))  # [] thrust loading coefficient

    sigma = [0.096863, 0.10587, 0.106216, 0.109273, 0.119423, 0.123934, 0.128191, 0.130071, 0.133415, 0.134549, 0.145498, 0.14605, 0.151302, 0.151667, 0.151994, 0.155477, 0.160436, 0.163178, 0.172615, 0.173714, 0.18035, 0.180859, 0.181607, 0.192745, 0.194136, 0.194654, 0.196008, 0.199468, 0.202909, 0.213076, 0.225825, 0.229187, 0.230794, 0.230837, 0.238109, 0.25256, 0.257919, 0.259041, 0.273601, 0.279877, 0.282535, 0.284076, 0.300368, 0.313148, 0.317236, 0.323255, 0.327327, 0.335113, 0.338342, 0.338949, 0.354907, 0.370035, 0.378004, 0.388534, 0.405782, 0.406381, 0.425536, 0.42557, 0.426293, 0.451867, 0.469118, 0.477511, 0.50036, 0.501098, 0.539314, 0.540411, 0.56212, 0.569024, 0.575477, 0.612999, 0.621964, 0.665128, 0.684072, 0.707334, 0.730429, 0.738818, 0.797749, 0.844171, 0.873004, 0.929222, 0.949152, 0.977354, 1.01081, 1.05577, 1.178, 1.20247, 1.20367, 1.20939, 1.26433, 1.40722, 1.48156, 1.49136, 1.55428, 1.67965]
    tal5  = [0.040322, 0.044961, 0.045142, 0.046738, 0.052109, 0.05453, 0.056833, 0.057855, 0.059682, 0.060304, 0.066368, 0.066677, 0.069625, 0.069831, 0.070015, 0.071985, 0.074807, 0.076376, 0.08182, 0.082459, 0.086099, 0.086379, 0.086791, 0.092953, 0.093727, 0.094016, 0.094769, 0.096329, 0.097878, 0.102446, 0.108153, 0.109654, 0.110371, 0.110389, 0.113491, 0.119626, 0.121891, 0.122365, 0.128492, 0.131122, 0.132056, 0.132597, 0.138267, 0.142662, 0.144058, 0.146106, 0.147486, 0.150113, 0.151198, 0.151384, 0.156246, 0.160792, 0.163163, 0.166273, 0.17131, 0.171483, 0.176296, 0.176304, 0.176484, 0.182772, 0.186934, 0.188936, 0.194318, 0.19449, 0.203, 0.20324, 0.207958, 0.209442, 0.210823, 0.218726, 0.220584, 0.228402, 0.231757, 0.235815, 0.239781, 0.241206, 0.251009, 0.258532, 0.263106, 0.27182, 0.274848, 0.279082, 0.283619, 0.289594, 0.305198, 0.308388, 0.308544, 0.309284, 0.316312, 0.333913, 0.342721, 0.343865, 0.351128, 0.365177]

    sigma_values = sigma
    tal5_values = tal5

    cavLim = np.interp(sig07R, sigma_values, tal5_values, left=np.nan, right=np.nan)

    # if tal07R > cavLim:
    #     print('Cavitation constraint reached')

    # Peripherical velocity constraint

    Vtip = pi*D*n/60
    Vtipmax = 39

    # if Vtip > Vtipmax:
    #     print('Peripherical velocity constraint reached')

    return [n, PO, etaO, t075dD, tmin075dD, tal07R, cavLim, Vtip, Vtipmax]
