import numpy as np
from math import ceil
# Run the fitness
from oct2py import Oct2Py
from multiprocessing.pool import ThreadPool
# Run multiple Zs as different processes
from multiprocessing import Pool
# to save the progress of the algorithms
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

# size of step from each variable
LIST_SIZE = {'D':     int((range_D[1]-range_D[0])        / 0.05),
             'AEdAO': int((range_AEdAO[1]-range_AEdAO[0])/ 0.1),
             'PdD':   int((range_PdD[1]-range_PdD[0])    / 0.1)}


t = [LIST_SIZE[v] for v in LIST_SIZE]
all_iter = t[0]*t[1]*t[2]

# number of octave evaluations to run in parallel in each process
NUM_PARALLEL = 3

NUM_BATCHES = ceil(LIST_SIZE['PdD'] / NUM_PARALLEL)

# save the results, otherwise there is no output
save_file = True

print_octave_result = False

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

# ========= Logic ===========
def run_octave_evaluation(V_S,D,Z,AEdAO,PdD):
    P_B, n = [0, 0]
    with Oct2Py() as octave:
        octave.warning ("off", "Octave:data-file-in-path");
        octave.addpath('./allCodesOctave');
        P_B, n = octave.F_LabH2_aprox(V_S,D,Z,AEdAO,PdD, nout=2)
    return [P_B, n]

    def wrapper(k, x):
    D, AEdAO, PdD = x
    P_B, n = run_octave_evaluation(V_S,D,Z,AEdAO,PdD)
    return [k, P_B]

def run_list_parallel(x_list):
    fitness_list = np.zeros(len(x_list))
    # run eval in parallel
    with ThreadPool(len(x_list)) as pool:
        id_x = [(k, x_list[k]) for k in range(len(x_list))]
        for result in pool.starmap(wrapper, id_x):
            k, fitness = result
            fitness_list[k] = fitness
    # go through the results and save
    for k in range(len(x_list)):
        P_B = fitness_list[k]
        D, AEdAO, PdD = x_list[k]
        #
        if print_octave_result:
            print("D:",D,"Z:",Z,"AEdAO:",AEdAO,"PdD:",PdD, "P_B:",P_B)
        if save_file:
            append_to_file(filename, [D, AEdAO, PdD, Z, P_B])

list_D     = np.linspace(range_D[0],     range_D[1],     LIST_SIZE['D'])
list_AEdAO = np.linspace(range_AEdAO[0], range_AEdAO[1], LIST_SIZE['AEdAO'])
list_PdD   = np.linspace(range_PdD[0],   range_PdD[1],   LIST_SIZE['PdD'])

def run(z):
    global Z
    Z = z
    # create the csv file with the headers
    if save_file:
        global filename
        filename = create_file(str(Z))

    counter = 0
    for D in list_D:
        for AEdAO in list_AEdAO:
            # divide PdD in batches of size NUM_PARALLEL
            for b in range(NUM_BATCHES):
                start = b * NUM_PARALLEL
                end   = (b+1) * NUM_PARALLEL
                list_x = [(D,AEdAO,PdD) for PdD in list_PdD[start:end]]
                # run list in parallel
                run_list_parallel(list_x)
                # keep count of the progress
                counter += len(list_x)
                print('Z:',Z, counter,'/',all_iter)

    return Z

# ========= RUN in parallel ============
global dir_name
dir_name = create_dir('gradient')

if __name__ == '__main__':
    with Pool() as pool:
        for result_z in pool.map(run, range(range_Z[0],range_Z[1]+1)):
            print('end of ', result_z)
