import numpy as np
import random
# from es import CMAES, OpenES
#
# from multiprocessing.pool import ThreadPool
# from multiprocessing import Pool
#
import pandas as pd
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

def create_config_file_DifEvo(dir_solver, V_S, NPOPULATION, MAX_ITERATION, SEED, new_fitness):
    # save the configs in a file
    filename = dir_solver+'/' + 'configs.csv'
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow( ["V_S",            V_S] )
        writer.writerow( ["NPOPULATION",    NPOPULATION] )
        writer.writerow( ["MAX_ITERATION",  MAX_ITERATION] )
        writer.writerow( ["SEED",           SEED] )
        writer.writerow( ["New Fitness",    new_fitness] )

def create_config_file_ES(dir_solver, V_S, NPOPULATION, MAX_ITERATION, SEED, x0, SIGMA_INIT):
    # save the configs in a file
    filename = dir_solver+'/' + 'configs.csv'
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow( ["V_S",            V_S] )
        writer.writerow( ["NPOPULATION",    NPOPULATION] )
        writer.writerow( ["MAX_ITERATION",  MAX_ITERATION] )
        writer.writerow( ["SEED",           SEED] )
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

# def save_best_result(dir_seed, solver_name, V_S, Npop, Mit, seed, result):
#     filename = create_file(dir_seed, 'best_results_' + solver_name)
#     #
#     Z             = result[0]
#     D, AEdAO, PdD = result[1]
#     fitness       = result[2]
#     append_to_file_order(filename, D=D, AEdAO=AEdAO, PdD=PdD, Z=Z, P_B=-fitness, fitness=fitness)
#     # if there is history to save
#     if (len(result) > 3):
#         history   = result[3]
#         append_to_file(filename, ['history'])
#         append_to_file(filename, history)
#     # config
#     append_to_file(filename, ['solver Name', 'V_S', 'NPOPULATION', 'MAX_ITERATION', 'SEED'])
#     append_to_file(filename, [ solver_name,    V_S,  Npop,         Mit,            seed])
#
#     print('saved', filename)

# ----------------- ES Logic -----------------------------------
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



#
#
#     # =========== OPENAI_ES PARALLEL ===========
#     # if save_file:
#     #     dir_solver = dir_run +'/'+ str(V_S).replace('.','_') +'/' + str(seed) + '/' + 'openaies'
#     #     mkdir(dir_solver)
#     #
#     # solver = openaies
#     # results_openaies = []
#     # with Pool() as pool:
#     #     solver_zs = [(solver, z, dir_solver) for z in range(range_Z[0],range_Z[1]+1)]
#     #     for result in pool.starmap(solver_for_Z, solver_zs):
#     #         results_openaies.append(result)
#     #
#     # # sort by Z
#     # results_openaies.sort(key=(lambda r: r[0]))
#     #
#     # # get only the valid ones
#     # valid_results_openaies = get_valid_results(results_openaies)
#     #
#     # if len(valid_results_openaies) > 0:
#     #     print("Best result openai-es")
#     #     best_result_openaies = get_best_result(valid_results_openaies)
#
#     # ======== SAVE ============
#     if len(valid_results_cmaes) > 0:
#         save_best_result(dir_seed, 'cmaes',    V_S, NPOPULATION, MAX_ITERATION, seed, best_result_cmaes)
#     # if len(valid_results_openaies) > 0:
#     #     save_best_result(dir_seed, 'openaies', V_S, NPOPULATION, MAX_ITERATION, seed, best_result_openaies)
#
#
#
# # ===========================================================
#
# save_file = True
# save_in_same_dir = True
#
# # run for this number of seeds
# NUMBER_OF_SEEDS_TO_RUN = 2
#
# # list of V_S, each V_S in the list will be run NUMBER_OF_SEEDS_TO_RUN times
# # V_S_list = [7.0, 7.5, 8.0, 8.5]
# V_S_list = [7.0, 7.2]
 # # --- choose fitness calculation ---
# global new_fitness_list
# # False = DE dif evo
# # True = modified fitness dif evo
# new_fitness_list = [False, True]
# # new_fitness_list = [True]
#
# # whether to run old fitness (original dif evo) if V_S >= 8.0
# # True  = doenst run old fit, (only new fitness calculation)
# # False = run new_fitness_list
# not_run_old_fit_above_8 = True

#
# global dir_run
#
# now = datetime.now()
# dir_run = 'run_'+ now.strftime("%Y_%m_%d_%Hh%M")
# mkdir(dir_run)
#
# for vs in V_S_list:
#     global V_S
#     V_S = vs
#
#     # create VS dir
#     dir_vs = dir_run +'/'+ str(V_S).replace('.','_')
#     mkdir(dir_vs)
#
#     print('======', V_S, '======')
#     for seed in range(NUMBER_OF_SEEDS_TO_RUN):
#         print('-----', seed, '-----')
#
#         run_cmaes(seed, V_S, dir_vs)




# # ==== parallel run DE ====
# def get_best_fit_number(x):
#     for i in range(len(x)):
#         x.iloc[i] = x.iloc[i][len('best fit at iteration '):]
#     return x
#
# def parallel_seed_run(seed, V_S):
#     print('-----', seed, '-----')
#
#     # create config file
#
#     # ex: run/7_0/1
#     dir_seed = dir_run +'/'+ str(V_S).replace('.','_') +'/' + str(seed)
#     mkdir(dir_seed)
#     # save the configs in a file
#     filename_config = dir_seed +'/' + 'configs.csv'
#     with open(filename_config, 'w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow( ["V_S",            V_S] )
#         writer.writerow( ["NPOPULATION",    NPOPULATION] )
#         writer.writerow( ["MAX_ITERATION",  MAX_ITERATION] )
#         writer.writerow( ["SEED",           seed] )
#         writer.writerow( ["New Fitness"]+ new_fitness_list)
#         # writer.writerow( ["x0 D",           0] )
#         # writer.writerow( ["x0 AEdAO",       0] )
#         # writer.writerow( ["x0 PdD",         0] )
#         # writer.writerow( ["SIGMA_INIT_CMAES",    SIGMA_INIT_CMAES] )
#         # writer.writerow( ["SIGMA_INIT_OPENAIES", SIGMA_INIT_OPENAIES] )
#
#     # not run old fitness for V_S >= 8.0
#     if not_run_old_fit_above_8 and (V_S >= 8.0):
#         fitness_list = [True]
#     else:
#         fitness_list = new_fitness_list
#
#     for new_fitness in fitness_list:
#         solver_name = 'DE_mod' if new_fitness else 'DE'
#
#         # ===========  ===========
#         dir_solver = dir_seed + '/' + solver_name
#         mkdir(dir_solver)
#
#         filename_allRun = dir_solver + '/' + 'allRunSaved_' + str(seed) + '.csv'
#
#         # run DE
#         if new_fitness:
#             D, Z, AEdAO, PdD, P_B = F_DifEvo_LH2_return_constraints_fitness(V_S, filename_allRun)
#         else:
#             D, Z, AEdAO, PdD, P_B = F_DifEvo_LH2_return_constraints(V_S, filename_allRun)
#
#         print("Best result", solver_name)
#         print('P_B:',P_B)
#         print('D:',D)
#         print('AEdAO:',AEdAO)
#         print('PdD:',PdD)
#         print('Z:',Z)
#
#         # ======== Make CSV in same pattern as CMA-ES and OpenAI-ES ============
#         col_names_DE = ['D', 'Z', 'AEdAO', 'PdD', 'P_B', 'n', 'etaO', 'etaR', 't075dD','tmin075dD', 'tal07R','cavLim', 'Vtip','Vtipmax', 'fitness', 'iteration', 'population_i']
#         col_names = ['D', 'AEdAO', 'PdD', 'Z', 'P_B', 'n', 'fitness', 't075dD','tmin075dD', 'tal07R','cavLim', 'Vtip','Vtipmax', 'penalty', 'valid']
#
#         df = pd.read_csv(filename_allRun, header=None, skiprows=1, names=col_names_DE)
#
#         df = df[['D', 'AEdAO', 'PdD', 'Z', 'P_B', 'n', 'fitness', 't075dD','tmin075dD', 'tal07R','cavLim', 'Vtip','Vtipmax']]
#
#         # -- Calculate validity --
#
#         # insert the other collumns
#         df.insert(df.shape[1], 'penalty', None)
#
#         df.insert(df.shape[1], 'valid', True)
#
#         # create temporary cols
#         df['temp_cav'] = (df['tal07R'] - df['cavLim'])/df['cavLim']
#         df['temp_cav'] = df['temp_cav'].clip(lower=0)
#         df['temp_spd'] = (df['Vtip'] - df['Vtipmax'])/df['Vtipmax']
#         df['temp_spd'] = df['temp_spd'].clip(lower=0)
#         df['temp_str'] = (df['tmin075dD'] - df['t075dD'])/df['tmin075dD']
#         df['temp_str'] = df['temp_str'].clip(lower=0)
#         # calculate
#         df['penalty'] = df['temp_cav'] + df['temp_spd'] + df['temp_str']
#         df['valid'] = (df['penalty'] == 0)
#         # drop temporary cols
#         df = df.drop(['temp_cav', 'temp_spd', 'temp_str'], axis=1)
#
#
#         # ajust the iteration counter with fitness
#         df['D'] = df['D'].astype(str)
#         df.loc[df['D'].str.contains('best'), 'fitness'] = df.loc[df['D'].str.contains('best'), 'Z']
#         df.loc[df['D'].str.contains('best'), 'Z'] = None
#
#         df.loc[df['D'].str.contains('best'), 'AEdAO'] = get_best_fit_number(df.loc[df['D'].str.contains('best'), 'D'])
#         df.loc[df['D'].str.contains('best'), 'D'] = 'fitness at iteration'
#
#         # -- add best value to the end --
#         best_fit_to_find = df.loc[len(df)-1]['fitness'] # best fitness at last interation
#         result_row = df[(df['P_B'] == best_fit_to_find) & (df['D'] != 'fitness at iteration')] # find row with best fitness
#         df.loc[len(df)] = {'D': 'Best Solution'} # add text to the bottom
#         df.loc[len(df)] = result_row.iloc[0] # add row with values in the end
#
#         # save file
#         filename_out = dir_solver+'/'+str(seed)+'.csv'
#         df.to_csv(filename_out, index=False, header=True)
#
#         print('saved:', filename_out)
#
#         # ================ Best result file ================
#         D       = float(result_row.iloc[0]['D'])
#         Z       = int(result_row.iloc[0]['Z'])
#         AEdAO   = float(result_row.iloc[0]['AEdAO'])
#         PdD     = float(result_row.iloc[0]['PdD'])
#         # fitness = float(result_row.iloc[0]['fitness'])
#         P_B = float(result_row.iloc[0]['P_B'])
#         fitness = P_B
#         n = float(result_row.iloc[0]['n'])
#
#         # read csv file to generate history
#         history = []
#         with open(filename_out, 'r', newline='') as file:
#             reader = csv.reader(file, delimiter=',')
#             for row in reader:
#                 if 'best' in row[0]:
#                     # iteration = row[0].split(' ')[-1]
#                     fit = -float(row[1])
#                     history.append(str(fit))
#
#         save_best_result(dir_seed, solver_name, V_S, NPOPULATION, MAX_ITERATION, seed, D, Z, AEdAO, PdD, fitness, P_B=P_B, n=n, history=history)
#
#     return [P_B, D, AEdAO, PdD, Z, seed]
#
# # ========= RUN THE SEEDs ============
# global dir_run
#
# now = datetime.now()
# dir_run = 'run_'+ now.strftime("%Y_%m_%d_%Hh%M")
# mkdir(dir_run)
#
# for vs in V_S_list:
#     V_S = vs
#
#     # create dir
#     mkdir(dir_run +'/'+ str(V_S).replace('.','_'))
#
#     print('======', V_S, '======')
#
#     list_r = []
#     with Pool() as pool:
#         seeds_list = [(seed, V_S) for seed in range(NUMBER_OF_SEEDS_TO_RUN)]
#         for result in pool.starmap(parallel_seed_run, seeds_list):
#             print(result)
#             list_r.append(result)
#
#     print("what i want")
#     for result in list_r:
#         # if (result[0] < 171.2):
#         if (result[0] < 173.2):
#             print('P_B', result[0], 'seed', result[-1])
