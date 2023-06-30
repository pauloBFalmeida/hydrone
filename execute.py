import numpy as np
import random
import matplotlib.pyplot as plt

import csv
from datetime import datetime
from os import mkdir, chdir

from multiprocessing import Process, Pool

from oct2py import Oct2Py

V_S = 7.0    # service speed [kn]

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

def append_to_file_order(filename, D='', AEdAO='', PdD='', Z='', P_B='', n='', fitness='', i=''):
    row = [D, AEdAO, PdD, Z, P_B, n, fitness, i]
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)

def save_best_result(D, Z, AEdAO, PdD, fitness, seed, solver_name):
    # create the csv file with the headers
    fitness = -fitness
    Z = int(Z)
    filename = create_file('best_results_' + str(seed) + '_' + solver_name)
    append_to_file_order(filename, D=D, AEdAO=AEdAO, PdD=PdD, Z=Z, fitness=fitness)
    # append_to_file(filename, ['history'])
    # append_to_file(filename,history)

# ------- run the algorithm ---------
def run_original(seed):
    chdir('./allCodesOctave'+'_'+str(seed))

    P_B = 0
    with Oct2Py() as octave:
        octave.warning ("off", "Octave:data-file-in-path");
        octave.eval('pkg load statistics')
        D, Z, AEdAO, PdD, P_B = octave.F_DifEvo_LH2(V_S, nout=5)
        # D, Z, AEdAO, PdD = (.7, 5, .7, .7)
        # P_B = octave.F_LabH2(V_S, D, Z, AEdAO, PdD, nout=1)

    print("D, Z, AEdAO, PdD")
    print(D, Z, AEdAO, PdD)
    print("P_B:")
    print(P_B)

    return [D, Z, AEdAO, PdD, P_B, seed]

if __name__ == '__main__':
    global dir_name
    now = datetime.now()
    dir_name = './' +'original_best_results_'+ now.strftime("%Y_%m_%d_%H_%M")
    try:
        mkdir(dir_name)
    except: pass

    # run 10 runs
    results = []
    with Pool(10) as pool:
        seeds = [seed for seed in range(10)]
        for result in pool.map(run_original, seeds):
            results.append(result)

    print()
    print('--- end ---')
    best = results[0]
    for r in results:
        D, Z, AEdAO, PdD, fitness, seed = r
        save_best_result(D, Z, AEdAO, PdD, fitness, seed, 'original')
        # find the best result
        if fitness < best[4]:
            best = r

    print('best result:')
    print('P_B:',  best[4])
    print('seed:', best[5])
