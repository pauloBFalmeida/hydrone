import numpy as np
from math import ceil
# Run the evaluation function
from oct2py import Oct2Py
# Run in parallel
from multiprocessing import Pool
# to save the progress of the algorithm
import csv
from datetime import datetime
from os import mkdir

# -------- range of the variables ----------
V_S = 7.0                   # service speed [kn]
range_D     = [0.5, 0.8]
range_AEdAO = [0.3, 1.05]
range_PdD   = [0.5, 1.4]
range_Z     = [2, 7]

# size of array for each variable
LIST_SIZE = {'D':     30,
             'AEdAO': 30,
             'PdD':   30}

# chunksize = LIST_SIZE['D'] // NUM_PARALLEL
NUM_PARALLEL = 12
# save the results, otherwise there is no output
save_file = True
# print output of each evaluation
print_octave_result = False

# create lists
list_D     = np.linspace(range_D[0],     range_D[1],     LIST_SIZE['D'])
list_AEdAO = np.linspace(range_AEdAO[0], range_AEdAO[1], LIST_SIZE['AEdAO'])
list_PdD   = np.linspace(range_PdD[0],   range_PdD[1],   LIST_SIZE['PdD'])
list_Z     = range(range_Z[0], range_Z[1]+1)
# ----- save to file functions -------
global dir_name

def append_to_file_batch_z(z, rows_list):
    filename = dir_name+'/' + str(z) +'.csv'
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        for row in rows_list:
            writer.writerow(row)

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
                  "V_S = "+str(V_S)]
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
        P_B, n = octave.F_LabH2(V_S,D,Z,AEdAO,PdD, nout=2)
    return [P_B, n]

def run(D):
    print('Start D =', D)
    all_iter = len(list_Z) * len(list_AEdAO) * len(list_PdD)

    #
    counter = 0
    for Z in list_Z:
        for AEdAO in list_AEdAO:
            rows_list = []
            for PdD in list_PdD:
                P_B, n = run_octave_evaluation(V_S,D,Z,AEdAO,PdD)
                rows_list.append([D, AEdAO, PdD, Z, P_B, n])
                # keep count of the progressif print_octave_result:
                if print_octave_result:
                    print("D:",D,"Z:",Z,"AEdAO:",AEdAO,"PdD:",PdD, "P_B:",P_B)
            if save_file:
                append_to_file_batch_z(Z, rows_list)
            counter += len(list_PdD)
            print('Z:',Z, counter,'/',all_iter)


# ========= RUN in parallel ============
if __name__ == '__main__':
    global dir_name
    vs_str = str(V_S).replace('.','_')
    dir_name = create_dir(vs_str+'_gradient')
    # create files with headers
    for z in range(range_Z[0],range_Z[1]+1):
        create_file(str(z))

    print('Running for ', len(list_Z) * len(list_D) * len(list_AEdAO) * len(list_PdD))
    # chunk size
    cs = LIST_SIZE['D'] // NUM_PARALLEL

    with Pool() as pool:
        for _ in pool.map(run, list_D, chunksize=cs):
            pass

    print('Completed')
