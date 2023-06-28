import numpy as np
import random
import matplotlib.pyplot as plt

from oct2py import Oct2Py
from multiprocessing.pool import ThreadPool

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

MAX_ITERATION = 128 # number of iterations

NUM_PARALLEL = 4    # number of evaluations done in parallel

NUM_BATCHS_SAVE = 1 # save every (NUM_BATCHS_SAVE * NUM_PARALLEL) iterations
# this will give aprox 32 saves, close to the number of iterations of others algorithms


save_file = False

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

from multiprocessing import Process, Pool

def run(z):
    global Z
    Z = z
    # create the csv file with the headers
    if save_file:
        global filename
        filename = create_file(str(Z))
    # create history list
    history = np.zeros(MAX_ITERATION // NUM_ITER_SAVE)
    # start best value
    best_fitness = float('-inf')
    best_x       = [-1, -1, -1]

    # execute for MAX_ITERATION in batches of NUM_PARALLEL
    for i in range(MAX_ITERATION // NUM_PARALLEL):
        fitness_list = np.zeros(NUM_PARALLEL)
        # create a list of params for evaluation
        x_list       = [[] for _ in range(NUM_PARALLEL)]
        for k in range(NUM_PARALLEL):
            # generate random values for params
            x =  [
                    random.uniform(range_D[0],     range_D[1]),
                    random.uniform(range_AEdAO[0], range_AEdAO[1]),
                    random.uniform(range_PdD[0],   range_PdD[1])
                  ]
            x_list[k] = x
        # evaluate the list of params in parralel
        with ThreadPool() as pool:
            id_x = [(k, x_list[k]) for k in range(NUM_PARALLEL)]
            fitness_wrapper = (lambda k, x: [k, fit_func(x)] )
            for result in pool.starmap(fitness_wrapper, id_x):
                k, fitness = result
                fitness_list[k] = fitness
        # go through the results and update the best result
        for k in range(NUM_PARALLEL):
            x = x_list[k]
            fitness = fitness_list[k]
            # if not failed, update best
            #  fitness is negative, so the best is the max
            if (fitness != 0) and fitness > best_fitness:
                best_fitness = fitness
                best_x       = x
        # end of batch
        if (i % NUM_BATCHS_SAVE) == 0:
            print('iteration:', i, 'best fitness:', best_fitness)
            counter = i // NUM_BATCHS_SAVE
            history[counter] = best_fitness
            if save_file:
                append_to_file_order(filename, "fitness at iteration", i, fitness=best_fitness)
    # return
    return [Z, best_x, best_fitness, history]

# results[0] = [Z, (D, AEdAO, PdD), fitness, history]
def get_best_result(results):
    # get result with best fitness
    best_result = max(results, key=(lambda x: x[2]))

    Z             =  best_result[0]
    D, AEdAO, PdD =  best_result[1]
    P_B           = -best_result[2]
    print("D:",D,"Z:",Z,"AEdAO:",AEdAO,"PdD:",PdD)
    print("P_B:",P_B)

    return best_result

def save_best_result(result, solver_name, seed=None):
    # create the csv file with the headers
    global filename
    if seed != None:
        filename = create_file('best_results_' + str(seed) + '_' + solver_name)
    else:
        filename = create_file('best_results_' + solver_name)
    #
    Z             = result[0]
    D, AEdAO, PdD = result[1]
    fitness       = result[2]
    append_to_file_order(filename, D=D, AEdAO=AEdAO, PdD=PdD, Z=Z, fitness=fitness)
    # if there is history to save
    if (len(result) > 2):
        history   = result[3]
        append_to_file(filename, ['history'])
        append_to_file(filename, history)

# ========= RUN THE SEEDs ============
global dir_name
dir_name = create_dir('random')

for seed in range(10):
    results = []
    with Pool() as pool:
        for result in pool.map(run, range(range_Z[0],range_Z[1]+1)):
            results.append(result)

    # sort by Z
    results.sort(key=(lambda r: r[0]))

    print("Best result random")
    best_result = get_best_result(results)

    # ======== SAVE ============
    save_best_result(best_result, 'random', seed)
