import csv
from datetime import datetime
from os import mkdir


# ---------- csv files and dir operations ---------------
def append_to_file(filename, row):
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)

def append_to_file_order(filename, D='', AEdAO='', PdD='', Z='', P_B='', n='', fitness=''):
    row = [D, AEdAO, PdD, Z, P_B, n, fitness]
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)

def create_file(dir_solver, text):
    filename = dir_solver+'/' + text +'.csv'
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        header = ["D = propeller diameter [m]",
                  "AEdAO = expanded area ratio",
                  "PdD = pitch ratio",
                  "Z = propeller's number of blades",
                  "P_B = power brake",
                  "n = Propeller angular speed [rpm]",
                  "fitness",
                  "t075dD",
                  "tmin075dD",
                  "tal07R",
                  "cavLim",
                  "Vtip",
                  "Vtipmax",
                  "penalty",
                  "valid"
                 ]
        writer.writerow(header)
    return filename

def create_dir(text):
    now = datetime.now()
    dir_name = './' + text +'_'+ now.strftime("%Y_%m_%d_%H_%M")
    try:
        mkdir(dir_name)
    except: pass
    return dir_name

def create_config_file_DifEvo(dir_solver, SOLVER_NAME, V_S, NPOPULATION, MAX_ITERATION, SEED, new_fitness):
    # save the configs in a file
    filename = dir_solver+'/' + 'configs.csv'
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow( ["V_S",            V_S] )
        writer.writerow( ["NPOPULATION",    NPOPULATION] )
        writer.writerow( ["MAX_ITERATION",  MAX_ITERATION] )
        writer.writerow( ["SEED",           SEED] )
        writer.writerow( ["Solver Name",    SOLVER_NAME] )
        writer.writerow( ["New Fitness",    new_fitness] )

def create_config_file_ES(dir_solver, SOLVER_NAME, V_S, NPOPULATION, MAX_ITERATION, SEED, x0, SIGMA_INIT):
    # save the configs in a file
    filename = dir_solver+'/' + 'configs.csv'
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow( ["V_S",            V_S] )
        writer.writerow( ["NPOPULATION",    NPOPULATION] )
        writer.writerow( ["MAX_ITERATION",  MAX_ITERATION] )
        writer.writerow( ["SEED",           SEED] )
        writer.writerow( ["Solver Name",    SOLVER_NAME] )
        writer.writerow( ["x0 D",           x0[0]] )
        writer.writerow( ["x0 AEdAO",       x0[1]] )
        writer.writerow( ["x0 PdD",         x0[2]] )
        writer.writerow( ["SIGMA_INIT",    SIGMA_INIT] )


def save_best_result(dir_seed, solver_name, V_S, Npop, Mit, seed, D, Z, AEdAO, PdD, fitness, P_B='', n='', history=''):
    # create the csv file with the headers
    fitness = -fitness
    Z = int(Z)
    filename = create_file(dir_seed, 'best_results_' + str(seed) +'_'+ solver_name)
    append_to_file_order(filename, D=D, AEdAO=AEdAO, PdD=PdD, Z=Z, P_B=P_B, n=P_B, fitness=fitness)
    # history
    append_to_file(filename, ['history'])
    append_to_file(filename, history)
    # config
    append_to_file(filename, ['solver Name', 'V_S', 'NPOPULATION', 'MAX_ITERATION', 'SEED'])
    append_to_file(filename, [ solver_name,   V_S,   Npop,          Mit,             seed])

    print('saved', filename)


# each element of the list results is [Z, (D, AEdAO, PdD), fitness, history]
def get_best_result(results):
    # get result with best fitness
    best_result = max(results, key=(lambda x: x[2]))
    # print the values
    Z             =  best_result[0]
    D, AEdAO, PdD =  best_result[1]
    fitness       = -best_result[2]
    print("D:",D,"Z:",Z,"AEdAO:",AEdAO,"PdD:",PdD)
    print("fitness:",fitness)
    return best_result
