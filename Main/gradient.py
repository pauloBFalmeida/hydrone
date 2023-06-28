import numpy as np
import random
import matplotlib.pyplot as plt

from oct2py import Oct2Py
from multiprocessing.pool import ThreadPool
from multiprocessing import Pool

import csv
from datetime import datetime
from os import mkdir

# -------- range of the variables ----------
V_S = 7.0                   # service speed [kn]
range_D     = [0.5, 0.8]
range_AEdAO = [0.3, 1.05]
range_PdD   = [0.5, 1.4]
range_Z     = [2, 7]

# Define the lower and upper bounds for each variable
lower_bounds = [range_D[0], range_AEdAO[0], range_PdD[0]]
upper_bounds = [range_D[1], range_AEdAO[1], range_PdD[1]]

NUM_PARALLEL = 4    # number of evaluations done in parallel

STEP_SIZE = {'D':     0.2,   # size of step from each variable
             'AEdAO': 0.2,
             'PdD':   0.2}

save_file = True

# ----- save to file functions -------
global dir_name

def append_to_file(filename, row):
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)

def append_to_file_order(filename, D='', AEdAO='', PdD='', Z='', P_B='', n='', fitness='', i=''):
    row = [D, AEdAO, PdD, Z, P_B, n, fitness, i]
    append_to_file(filename, row)

def create_file(text):
    filename = dir_name+'/' + text +'.csv'
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        header = ["D = propeller diameter [m]",
                  "AEdAO = expanded area ratio",
                  "PdD = pitch ratio",
                  "Z = propeller's number of blades",
                  "P_B = power brake",
                  "n = Propeller angular speed [rpm]",
                  "fitness",
                  "i = thread pool id"]
        writer.writerow(header)
    return filename

def create_dir(text):
    now = datetime.now()
    dir_name = './' + text +'_'+ now.strftime("%Y_%m_%d_%H_%M")
    try:
        mkdir(dir_name)
    except: pass
    return dir_name


# ---- fitness function --------
def run_octave_evaluation(V_S,D,Z,AEdAO,PdD):
    P_B, n = [0, 0]
    with Oct2Py() as octave:
        octave.warning ("off", "Octave:data-file-in-path");
        octave.addpath('./allCodesOctave');
        # P_B, n = octave.F_LabH2(V_S,D,Z,AEdAO,PdD, nout=2)
        # P_B, n = octave.F_LabH2_no_cav_lim(V_S,D,Z,AEdAO,PdD, nout=2)
#         P_B, n = octave.F_LabH2_aprox_no_cav_lim(V_S,D,Z,AEdAO,PdD, nout=2)
        P_B, n = octave.F_LabH2_aprox(V_S,D,Z,AEdAO,PdD, nout=2)
#         if not (P_B == 0 or n == 0):
#             P_B, n = octave.F_LabH2(V_S,D,Z,AEdAO,PdD, nout=2)
    return [P_B, n]

def evaluate_solution(x, i=None):
    D     = x[0]
    AEdAO = x[1]
    PdD   = x[2]
    # verify that the values are in range
    penalty = -1000
    if (D > range_D[1] or D < range_D[0]):
        print("out","_D_:",D,"Z:",Z,"AEdAO:",AEdAO,"PdD:",PdD)
        return penalty
    if (AEdAO > range_AEdAO[1] or AEdAO < range_AEdAO[0]):
        print("out","D:",D,"Z:",Z,"_AEdAO_:",AEdAO,"PdD:",PdD)
        return penalty
    if (PdD > range_PdD[1] or PdD < range_PdD[0]):
        print("out","D:",D,"Z:",Z,"AEdAO:",AEdAO,"_PdD_:",PdD)
        return penalty

    P_B, n = run_octave_evaluation(V_S,D,Z,AEdAO,PdD)
    # to get the minimal P_B
    # the solvers use the max value as best fitness
    fit_value = 0
    if (P_B == 0 or n == 0):
        fit_value = penalty
    else:
        fit_value = -P_B

#     print("D:",D,"Z:",Z,"AEdAO:",AEdAO,"PdD:",PdD, "fitness:",fit_value)
    if save_file:
        append_to_file(filename, [D, AEdAO, PdD, Z, P_B, n, fit_value, i])

    return fit_value

# use evaluate_solution as the fitness function
fit_func = evaluate_solution

# ========= run ===========
def run_list_parallel(x_list):
    fitness_list = np.zeros(NUM_PARALLEL)
    # run fit_func in parallel
    with ThreadPool() as pool:
        id_x = [(k, x_list[k]) for k in range(NUM_PARALLEL)]
        fitness_wrapper = (lambda k, x: [k, fit_func(x)] )
        for result in pool.starmap(fitness_wrapper, id_x):
            # ajust the results to be in the same order as the x_list
            k, fitness = result
            fitness_list[k] = fitness
    # return fitness_list


def add_to_compute_list(x, x_list):
    print(x_list, '+', x)
    x_list.append(x)

    if len(x_list) == NUM_PARALLEL:
        run_list_parallel(x_list)
        x_list = []
        print(x_list, 'clear')

    # return x_list

def run(z):
    global Z
    Z = z
    # create the csv file with the headers
    if save_file:
        global filename
        filename = create_file(str(Z))

    # list to append values and compute them in parallel
    x_list = []


    list_D = np.linspace(range_D[0], range_D[1], 5)

    D = range_D[0]
    while D <= range_D[1]:
        AEdAO = range_AEdAO[0]
        while AEdAO <= range_AEdAO[1]:
            PdD = range_PdD[0]
            while PdD <= range_PdD[1]:
                add_to_compute_list((D, AEdAO, PdD), x_list)
                print(x_list)
                PdD += STEP_SIZE['PdD']
            AEdAO += STEP_SIZE['AEdAO']
        D += STEP_SIZE['D']

# ========= RUN THE SEEDs ============
global dir_name
dir_name = create_dir('gradient')

if __name__ == '__main__':
    with Pool() as pool:
        for _ in pool.map(run, range(range_Z[0],range_Z[1]+1)):
            pass
