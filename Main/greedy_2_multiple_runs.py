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

NUM_SEGMENTS = 2
# NUM_ITERATIONS = 150 // (NUM_SEGMENTS**3)
NUM_ITERATIONS = 10

save_file = False
save_in_same_dir = False


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
    if save_in_same_dir:
        dir_name = './' + main_dir_name + '/' + text
    else:
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

# ========= run ===========
def run(z):
    global Z
    Z = z

    history = np.zeros(NUM_ITERATIONS+1)

    # find starting valid value
    counter = 0
    best_fitness = float('-inf')
    while (best_fitness <= -999):
        best_solution = [
                        random.uniform(range_D[0],     range_D[1]),
                        random.uniform(range_AEdAO[0], range_AEdAO[1]),
                        random.uniform(range_PdD[0],   range_PdD[1])
                        ]
        best_fitness = fit_func(best_solution)
        counter += 1
    print('after:', counter, 'found fitness of ', best_fitness)

    history[0] = best_fitness
    #
    sigma = 0.1
    for iteration in range(NUM_ITERATIONS):
        D, AEdAO, PdD = best_solution
        # create values around the best solution
        Ds     = [D     - sigma, D     + sigma]
        AEdAOs = [AEdAO - sigma, AEdAO + sigma]
        PdDs   = [PdD   - sigma, PdD   + sigma]
        # clip values to be inside the range
        Ds     = np.clip(Ds,     range_D[0],     range_D[1])
        AEdAOs = np.clip(AEdAOs, range_AEdAO[0], range_AEdAO[1])
        PdDs   = np.clip(PdDs,   range_PdD[0],   range_PdD[1])
        # generate all permutations
        solutions = []
        for d in Ds:
            for a in AEdAOs:
                for p in PdDs:
                    solutions.append( (d,a,p) )
        # parallel run of fitness evaluation
        fitness_list = np.zeros(len(solutions))
        with ThreadPool() as pool:
            id_solutions = [(i, solutions[i]) for i in range(len(solutions))]
            fit_wrapper = (lambda i, x: [i, fit_func(x)])
            for result in pool.starmap(fit_wrapper, id_solutions):
                i, fitness = result
                fitness_list[i] = fitness
        # get best solution
        new_best_fitness = max(fitness_list)
        # if new best fitness is better than the previous one, change to new best fitness
        if new_best_fitness > best_fitness:
            best_fitness = new_best_fitness
            # update best solution
            best_solution_index = np.where(fitness_list == best_fitness)[0][0]
            best_solution = solutions[best_solution_index]
        # save best fitness in history
        history[iteration+1] = best_fitness
        # update sigma for the next iteration
        print('Z:',Z ,"iteration:", iteration+1, ' best finess', best_fitness)
        if save_file:
            append_to_file(filename, ["fitness at iteration", iteration+1,'','','','', best_fitness])
        sigma = sigma / 2
    print('Z:',Z, 'best', best_solution, 'with fit:', best_fitness)
    return [Z, best_solution, best_fitness, history]


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

def save_best_result(result, solver_name, seed=0):
    # create the csv file with the headers
    global filename
    filename = create_file('best_results_' + str(seed) + '_' + solver_name)
    Z             = result[0]
    D, AEdAO, PdD = result[1]
    fitness       = result[2]
    history       = result[3] if len(result) > 2 else []
    append_to_file_order(filename, D=D, AEdAO=AEdAO, PdD=PdD, Z=Z, fitness=fitness)
    append_to_file(filename, ['history'])
    append_to_file(filename,history)

# ========= RUN THE SEEDs ============
global dir_name
dir_name = create_dir('greedy_2')

for seed in range(10):
    results = []
    with Pool() as pool:
        for result in pool.map(run, range(range_Z[0],range_Z[1]+1)):
            results.append(result)

    # sort by Z
    results.sort(key=(lambda r: r[0]))

    print("Best result greedy_2")
    best_result = get_best_result(results)

    # ======== SAVE ============
    save_best_result(best_result, 'greedy_2', seed)
