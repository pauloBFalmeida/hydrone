import numpy as np
import random
import csv

from F_LabH2 import F_LabH2_return_constraints

def F_DifEvo_LH2_return_constraints(V_S, csv_filename):
    return DifEvo_LH2(V_S, csv_filename, original_fitness=True)

def F_DifEvo_LH2_return_constraints_fitness(V_S, csv_filename):
    return DifEvo_LH2(V_S, csv_filename, original_fitness=False)

# Implementation
def DifEvo_LH2(V_S, csv_filename, original_fitness=True):
    # seed for numpy
    seed = int(random.random() * 1000)
    np.random.seed( seed )
    print('seed', seed )

    # Creating output files
    # with open('constraints.txt', 'w') as fID:
    #     fID.write(f'{str.ljust("Vs[kts]", 10)} {str.ljust("D[m]", 10)} {str.ljust("Z[-]", 10)} '
    #               f'{str.ljust("AE/AO[-]", 10)} {str.ljust("P/D[-]", 10)} {str.ljust("zP[-]", 10)} '
    #               f'{str.ljust("Constraint", 10)}\n')

    # File to save all the runs
    with open(csv_filename, 'w') as fID:
        fID.write('D, Z, AEdAO, PdD, P_B, n, etaO, etaR, t075dD, tmin075dD, tal07R, cavLim, Vtip, '
                  'Vtipmax, fitness, iteration, population i\n')

    # Characteristics of the problem
    nv = 4  # number of variables

    # Upper and lower limits D,Z,AEdAO,PdD
    LimU = np.array([0.8, 7, 1.05, 1.4])
    LimL = np.array([0.5, 2, 0.30, 0.5])

    # Method Differential Evolution
    # V_S = 7.0

    pop_size = 30  # population size
    kmax = 30  # Number of iterations (generations)
    CR = 0.5  # factor that defines the crossover (0.5 < CR < 1)
    F = 0.8  # weight function that defines the mutation (0.5 < F < 1).

    xpo = np.zeros((pop_size, nv))
    VFi = np.zeros((pop_size, 4))
    VFpo = np.zeros((pop_size, 4))

    VFi2 = np.zeros((pop_size, 6))
    VFpo2 = np.zeros((pop_size, 6))

    # Initial population
    Xi = np.zeros((pop_size, nv))
    of = 0
    ofp = 0

    for i in range(pop_size):
        # removed infinite generation
        for j in range(nv):
            # create random Z
            if j == 1:
                Xi[i, j] = np.random.randint(LimL[j], LimU[j] + 1)
                # random.randint(LimL[j], LimU[j])
                # print('r', np.random.randint(LimL[j], LimU[j] + 1), random.randint(LimL[j], LimU[j]))
            else:
                Xi[i, j] = np.random.uniform(LimL[j], LimU[j])
                # print('r', np.random.uniform(LimL[j], LimU[j]), random.uniform(LimL[j], LimU[j]))
                # Xi[i, j] = random.uniform(LimL[j], LimU[j])
                # Xi[i, j] = LimL[j]



        ofp = ofp + 1

        # [P_B, n, etaO, etaR, t075dD, tmin075dD, tal07R, cavLim, Vtip, Vtipmax]
        VFi[i, 0], VFi[i, 1], VFi[i, 2], VFi[i, 3], VFi2[i, 0], VFi2[i, 1], VFi2[i, 2], VFi2[i, 3], VFi2[i, 4], VFi2[i, 5] = F_LabH2_return_constraints(V_S, Xi[i, 0], Xi[i, 1], Xi[i, 2], Xi[i, 3])

        # save
        with open(csv_filename, 'a') as fID:
            # D, Z, AEdAO, PdD,
            fID.write(f'{Xi[i, 0]},{Xi[i, 1]},{Xi[i, 2]},{Xi[i, 3]},')
            # P_B, n, etaO, etaR,
            fID.write(f'{VFi[i, 0]},{VFi[i, 1]},{VFi[i, 2]},{VFi[i, 3]},')
            # t075dD, tmin075dD, tal07R, cavLim, Vtip, Vtipmax,
            fID.write(f'{VFi2[i, 0]},{VFi2[i, 1]},{VFi2[i, 2]},{VFi2[i, 3]},{VFi2[i, 4]},{VFi2[i, 5]},')
            # fitness (P_B)
            fID.write(f'{VFpo[i, 0]},')
            # iteration, population i
            fID.write(f'0,{i}\n')

    #
    VFk = np.zeros((pop_size, 4, kmax))
    Xk = np.zeros((pop_size, nv, kmax))
    X = Xi.copy()
    VF = VFi.copy()
    VFk[:, :, 0] = VFi[:, :]
    Xk[:, :, 0] = Xi[:, :]

    for k in range(1, kmax + 1):
        print('iteration', k)
        for i in range(pop_size):
            alfa = np.random.randint(pop_size)
            beta = np.random.randint(pop_size)
            gama = np.random.randint(pop_size)

            while i == alfa or i == beta or i == gama or alfa == beta or beta == gama or gama == alfa:
                alfa = np.random.randint(pop_size)
                beta = np.random.randint(pop_size)
                gama = np.random.randint(pop_size)

            for j in range(nv):
                R = np.random.rand()
                # R = random.random()

                if R <= CR:
                    delta1, delta2 = 0, 1
                else:
                    delta1, delta2 = 1, 0

                xpo[i, j] = delta1 * X[i, j] + delta2 * (X[alfa, j] + F * (X[beta, j] - X[gama, j]))

                if xpo[i, j] > LimU[j]:
                    xpo[i, j] = LimU[j]
                elif xpo[i, j] < LimL[j]:
                    xpo[i, j] = LimL[j]

            xpo[i, 1] = round(xpo[i, 1])  # Variável discreta

            # Calculando o valor da função objetivo para xpo
            VFpo[i, 0], VFpo[i, 1], VFpo[i, 2], VFpo[i, 3], VFpo2[i, 0], VFpo2[i, 1], VFpo2[i, 2], VFpo2[i, 3], VFpo2[i, 4], VFpo2[i, 5] = F_LabH2_return_constraints(V_S, xpo[i, 0], xpo[i, 1], xpo[i, 2], xpo[i, 3])
            of += 1
            # print('offspring', of)


#           --- Calculating fitness ---
#           P_B,n,etaO,etaR
#           [VFpo(i,0),VFpo(i,1),VFpo(i,2),VFpo(i,3)]

#           strength,strengthMin, cavitation,cavitationMax, velocity,velocityMax
#           VFpo2(i,0),VFpo2(i,1),VFpo2(i,2),VFpo2(i,3),VFpo2(i,4),VFpo2(i,5)]

            if original_fitness:
                # cavitation > cavitationMax
                if VFpo2[i, 2] > VFpo2[i, 3]:
                    VFpo[i, 0] = 0

                # velocity > velocityMax
                if VFpo2[i, 4] > VFpo2[i, 5]:
                    VFpo[i, 0] = 0

                # strength < strengthMin
                if VFpo2[i, 0] < VFpo2[i, 1]:
                    VFpo[i, 0] = 0

                # Salvando
                with open(csv_filename, 'a') as fID:
                    # D, Z, AEdAO, PdD,
                    fID.write(f'{xpo[i, 0]},{xpo[i, 1]},{xpo[i, 2]},{xpo[i, 3]},')
                    # P_B, n, etaO, etaR,
                    fID.write(f'{VFpo[i, 0]},{VFpo[i, 1]},{VFpo[i, 2]},{VFpo[i, 3]},')
                    # t075dD, tmin075dD, tal07R, cavLim, Vtip, Vtipmax,
                    fID.write(f'{VFpo2[i, 0]},{VFpo2[i, 1]},{VFpo2[i, 2]},{VFpo2[i, 3]},{VFpo2[i, 4]},{VFpo2[i, 5]},')
                    # fitness
                    fID.write(f'{VFpo[i, 0]},')
                    # iteration, population i
                    fID.write(f'{k},{i}\n')

                # Verificando o valor da função
                if VFpo[i, 0] < VF[i, 0] and VFpo[i, 0] > 0:
                    X[i, :] = xpo[i, :]
                    VF[i, :] = VFpo[i, :]

            else:
                # max((cavitation - cavitationMax) / cavitation), 0)
                curr_fit = max((VFpo2[i, 2] - VFpo2[i, 3]) / VFpo2[i, 3], 0)  # max((cavitation - cavitationMax) / cavitation), 0)
                # max((velocity - velocityMax) / velocityMax), 0)
                curr_fit += max((VFpo2[i, 4] - VFpo2[i, 5]) / VFpo2[i, 5], 0)  # max((velocity - velocityMax) / velocityMax), 0)
                # max((strengthMin - strength) / strengthMin), 0)
                curr_fit += max((VFpo2[i, 1] - VFpo2[i, 0]) / VFpo2[i, 1], 0)  # max((strengthMin - strength) / strengthMin), 0)
                # (1 + curr_fit) * P_B
                curr_fit = (1 + curr_fit) * VFpo[i, 0]  # (1 + curr_fit) * P_B

                # Salvando
                with open(csv_filename, 'a') as fID:
                    # D, Z, AEdAO, PdD,
                    fID.write(f'{xpo[i, 0]},{xpo[i, 1]},{xpo[i, 2]},{xpo[i, 3]},')
                    # P_B, n, etaO, etaR,
                    fID.write(f'{VFpo[i, 0]},{VFpo[i, 1]},{VFpo[i, 2]},{VFpo[i, 3]},')
                    # t075dD, tmin075dD, tal07R, cavLim, Vtip, Vtipmax,
                    fID.write(f'{VFpo2[i, 0]},{VFpo2[i, 1]},{VFpo2[i, 2]},{VFpo2[i, 3]},{VFpo2[i, 4]},{VFpo2[i, 5]},')
                    # fitness
                    fID.write(f'{curr_fit},')
                    # iteration, population i
                    fID.write(f'{k},{i}\n')

                # Verificando o valor da função
                # P_B > 0
                if VFpo[i, 0] > 0:
                    # minimal P_B
                    if curr_fit < VF[i, 0]:
                        X[i, :] = xpo[i, :]
                        VF[i, :] = VFpo[i, :]
                        VF[i, 0] = curr_fit

        VFk[:, :, k - 1] = VF[:, :]
        Xk[:, :, k - 1]  = X[:, :]

        # Salvando
        with open(csv_filename, 'a') as fID:
            fID.write(f'best fit at iteration {k},{VF[i, 0]}\n')

    # Obtenha o melhor resultado
    print('best', X, VF)

    best_params = np.zeros(nv)
    best_fitness = 999

    for i in range(pop_size):
        if VF[i, 0] < best_fitness and VF[i, 0] > 0:
            best_params = X[i, :]
            best_fitness = VF[i, 0]

    D = best_params[0]
    Z = best_params[1]
    AEdAO = best_params[2]
    PdD = best_params[3]
    P_B = best_fitness

    print(best_params)
    print(best_fitness)

    return [D, Z, AEdAO, PdD, P_B]
