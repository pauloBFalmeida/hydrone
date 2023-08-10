import numpy as np
import random
import cma
from es import CMAES, OpenES

from oct2py import Oct2Py
from multiprocessing.pool import ThreadPool
from multiprocessing import Pool

# -------- range of the variables ----------
# run for this number of seeds
NUMBER_OF_SEEDS_TO_RUN = 10

# V_S list
V_S_list = [7.0, 7.5, 8.0, 8.5]

# V_S = 7.0                   # service speed [kn]
range_D     = [0.5, 0.8]
range_AEdAO = [0.3, 1.05]
range_PdD   = [0.5, 1.4]
range_Z     = [2, 7]

# Define the lower and upper bounds for each variable
lower_bounds = [range_D[0], range_AEdAO[0], range_PdD[0]]
upper_bounds = [range_D[1], range_AEdAO[1], range_PdD[1]]

# OPENAI-ES and CMAES
NPOPULATION   = 12 # size of population
MAX_ITERATION = 30 # run solver for this generations

NPARAMS = 3  # number of parameters to evaluate
SIGMA_INIT_CMAES    = 0.1
SIGMA_INIT_OPENAIES = 0.1

save_file = True
save_in_same_dir = True

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
    P_B, t075dD,tmin075dD, tal07R,cavLim, Vtip,Vtipmax = [-1, -1, -1, -1, -1, -1, -1]
    with Oct2Py() as octave:
        octave.warning ("off", "Octave:data-file-in-path");
        octave.addpath('./allCodesOctave');
        P_B, n, etaO,etaR, t075dD,tmin075dD, tal07R,cavLim, Vtip,Vtipmax = octave.F_LabH2_return_constraints(V_S,D,Z,AEdAO,PdD, nout=10)
    return [P_B, t075dD,tmin075dD, tal07R,cavLim, Vtip,Vtipmax]

# ---- calculate the fitness ------------------
# fitness function, to find the minimal power brake
def evaluate_solution(x, i=None):
    D     = x[0]
    AEdAO = x[1]
    PdD   = x[2]

#     P_B, t075dD,tmin075dD, tal07R,cavLim, Vtip,Vtipmax
    P_B, strength,strengthMin, cavitation,cavitationMax, velocity,velocityMax = run_octave_evaluation(V_S,D,Z,AEdAO,PdD)

    # add the constraints
    fit_value = P_B * (1 + max(((cavitation - cavitationMax)/cavitationMax), 0) + max(((velocity - velocityMax)/velocityMax), 0) + max(((strengthMin - strength)/strengthMin), 0) )
    # prof version
    # fit_value = P_B + max(((cavitation - cavitationMax)/cavitationMax), 0) + max(((velocity - velocityMax)/velocityMax), 0) + max(((strengthMin - strength)/strengthMin), 0)

    # we want the minimal P_B
    # the solvers use the max value as best fitness, so
    fit_value *= -1

#     print("D:",D,"Z:",Z,"AEdAO:",AEdAO,"PdD:",PdD, "fitness:",fit_value)
    if save_file:
        penalty = max(((cavitation - cavitationMax)/cavitationMax), 0) + max(((velocity - velocityMax)/velocityMax), 0) + max(((strengthMin - strength)/strengthMin), 0)
        valid = (penalty == 0)
        append_to_file(filename, [D, AEdAO, PdD, Z, P_B, 0, fit_value, strength,strengthMin, cavitation,cavitationMax, velocity,velocityMax, penalty, valid])

    return fit_value

# def evaluate_solution(x, i=None):
#     D     = x[0]
#     AEdAO = x[1]
#     PdD   = x[2]
#     #
#     P_B, t075dD,tmin075dD, tal07R,cavLim, Vtip,Vtipmax = run_octave_evaluation(V_S,D,Z,AEdAO,PdD)

#     # verify if broke any constraints limits
#     penalty = 0
#         # Strength Constraint
#     if (t075dD < tmin075dD):
#         penalty = tmin075dD - t075dD
# #         print('broke Strength', penalty)

#         # Cavitation Constrant
#     if (tal07R > cavLim):
#         penalty = tal07R - cavLim
# #         print('broke Cavitation', penalty)

#         # Peripherical Velocity Constraint
#     if (Vtip > Vtipmax):
#         penalty = Vtip - Vtipmax
# #         print('broke Velocity', penalty)

#     if penalty > 0:
#         penalty += PENALTY_ADD

#     # we want the minimal P_B
#     # the solvers use the max value as best fitness, so
#     fit_value = -(P_B + penalty)

# #     print("D:",D,"Z:",Z,"AEdAO:",AEdAO,"PdD:",PdD, "fitness:",fit_value)
#     if save_file:
#         valid = (penalty == 0)
#         append_to_file(filename, [D, AEdAO, PdD, Z, P_B, 0, fit_value, t075dD,tmin075dD, tal07R,cavLim, Vtip,Vtipmax, penalty, valid])

#     return fit_value

# use evaluate_solution as the fitness function
fit_func = evaluate_solution

# -------------------------------

# wrapper tho add the index of solution in the array, to the response of the ThreadPool
def fit_func_parallel_wrapper(i, solution):
    fitness = fit_func(solution, i)
    return [i, fitness]

# defines a function to use solver to solve fit_func
def test_solver(solver):
    history = np.zeros(MAX_ITERATION)
    for j in range(MAX_ITERATION):
        # ask for the population
        solutions = solver.ask()
        # create a list with the fitness
        fitness_list = np.zeros(solver.popsize)
        # parallel run of fitness evaluation
        with ThreadPool() as pool:
            id_solutions = [(i, solutions[i]) for i in range(len(solutions))]
            for result in pool.starmap(fit_func_parallel_wrapper, id_solutions, chunksize=4):
                i, fitness = result
                fitness_list[i] = fitness
        # pass the fitness to the solver so it can decide the best individual
        solver.tell(fitness_list)
        result = solver.result() # first element is the best solution, second element is the best fitness
        history[j] = result[1]   # best fitness
        # print the process name (Z) and the iteration, and save in the csv
        print('Z:',Z, "fitness at iteration", (j+1), result[1], flush=True)
        if save_file:
            append_to_file_order(filename, "fitness at iteration", j, fitness=result[1])
#         append_to_file(filename, [, j, '','','','', result[1]])
    # best solution at the end of the solver's run
    print("local optimum discovered by solver:\n", result[0])
    print("fitness score at this local optimum:", result[1])
    return (history, result[0])

# ==== Logic ====
def solver_for_Z(solver, z):
    global Z
    Z = z

    # create the csv file with the headers
    if save_file:
        global filename
        filename = create_file(str(Z))

    # run the solver
    history, best_solution = test_solver(solver)

    # print best solution

    # get the P_B from best solution
    D       = best_solution[0]
    AEdAO   = best_solution[1]
    PdD     = best_solution[2]
    fitness = history[-1]
    print("Z:",Z, "Best Solution:", best_solution, 'with fitness:', fitness)

    if save_file:
        # write best solution to file
        append_to_file(filename, ["Best Solution"])
        append_to_file_order(filename, D=D, AEdAO=AEdAO, PdD=PdD, Z=Z, fitness=fitness)

    return [Z, best_solution, fitness, history]

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

def get_valid_results(results):
    valid_results = []

    for r in results:
        Z             =  r[0]
        D, AEdAO, PdD =  r[1]
        P_B_old       = -r[2]
#         print()
#         print("D:",D,"Z:",Z,"AEdAO:",AEdAO,"PdD:",PdD)
#         print("P_B:",P_B_old)
        P_B, t075dD,tmin075dD, tal07R,cavLim, Vtip,Vtipmax = run_octave_evaluation(V_S,D,Z,AEdAO,PdD)
        penalty = 0
            # Strenght Constraint
        if (t075dD < tmin075dD):
            penalty = tmin075dD - t075dD
#             print('broke Strength', penalty)
            # Cavitation Constraint
        if (tal07R > cavLim):
            penalty = tal07R - cavLim
#             print('broke Cavitation', penalty)
            # Peripherical Velocity Constraint
        if (Vtip > Vtipmax):
            penalty = Vtip - Vtipmax
#             print('broke Velocity', penalty)
#         print("real P_B:",P_B)
        #
        if penalty == 0:
            valid_results.append(r)

    return valid_results

def save_best_result(result, solver_name, seed=None):
    # in case there is main dir, save the best results in this same dir,
    #     otherwise will save in the last dir created (openaies)
    if save_in_same_dir:
        global dir_name, main_dir_name
        dir_name = main_dir_name
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
    if (len(result) > 3):
        history   = result[3]
        append_to_file(filename, ['history'])
        append_to_file(filename, history)

# ========= RUN THE SEEDs ============
for vs in V_S_list:
    global V_S
    V_S = vs
    print('======', V_S, '======')
    for seed in range(NUMBER_OF_SEEDS_TO_RUN):
        print('-----', seed, '-----')

        random.seed(seed)
        x0 =  [
                random.uniform(range_D[0],     range_D[1]),
                random.uniform(range_AEdAO[0], range_AEdAO[1]),
                random.uniform(range_PdD[0],   range_PdD[1])
              ]


        print("D    ", x0[0])
        print("AEdAO", x0[1])
        print("PdD  ", x0[2])

        if save_file:
            import csv
            from datetime import datetime
            from os import mkdir

            if save_in_same_dir:
                # create main_date dir
                now = datetime.now()
                main_dir_name = 'main_' + now.strftime("%Y_%m_%d_%H_%M")
                try:
                    mkdir(main_dir_name)
                except: pass
                # save the configs in a file
                filename = main_dir_name+'/' + 'configs.csv'
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow( ["V_S",            V_S] )
                    writer.writerow( ["NPOPULATION",    NPOPULATION] )
                    writer.writerow( ["MAX_ITERATION",  MAX_ITERATION] )
                    writer.writerow( ["SEED",           seed] )
                    writer.writerow( ["x0 D",           x0[0]] )
                    writer.writerow( ["x0 AEdAO",       x0[1]] )
                    writer.writerow( ["x0 PdD",         x0[2]] )
                    writer.writerow( ["SIGMA_INIT_CMAES",    SIGMA_INIT_CMAES] )
                    writer.writerow( ["SIGMA_INIT_OPENAIES", SIGMA_INIT_OPENAIES] )


        # defines CMA-ES algorithm solver
        cmaes = CMAES(NPARAMS,
                      x0=x0,                     # initial parameters values to generate the population
                      popsize=NPOPULATION,
                      weight_decay=0.0,
                      sigma_init = SIGMA_INIT_CMAES,
                      lower_bounds=lower_bounds,
                      upper_bounds=upper_bounds,
                  )

        # defines OpenAI's ES algorithm solver. Note that we needed to anneal the sigma parameter
        openaies = OpenES(NPARAMS,                 # number of model parameters
                        x0=x0,                     # initial parameters values to generate the population
                        sigma_init=SIGMA_INIT_OPENAIES, # initial standard deviation
                        sigma_decay=0.999,         # don't anneal standard deviation
                        learning_rate=0.1,         # learning rate for standard deviation
                        learning_rate_decay = 1.0, # annealing the learning rate
                        popsize=NPOPULATION,       # population size
                        antithetic=False,          # whether to use antithetic sampling
                        weight_decay=0.00,         # weight decay coefficient
                        rank_fitness=False,        # use rank rather than fitness numbers
                        forget_best=False,
                        lower_bounds=lower_bounds, # list of lower bounds for the parameters
                        upper_bounds=upper_bounds) # list of upper bounds for the parameters

        # =========== CMAES PARALLEL ===========
        if save_file:
            global dir_name
            dir_name = create_dir('cmaes')

        solver = cmaes
        results_cmaes = []
        with Pool() as pool:
            solver_zs = [(solver, z) for z in range(range_Z[0],range_Z[1]+1)]
            for result in pool.starmap(solver_for_Z, solver_zs):
                results_cmaes.append(result)

        # sort by Z
        results_cmaes.sort(key=(lambda r: r[0]))

        # get only the valid ones
        valid_results_cmaes = get_valid_results(results_cmaes)

        if len(valid_results_cmaes) > 0:
            print("Best result cmaes")
            best_result_cmaes = get_best_result(valid_results_cmaes)

        # =========== OPENAI_ES PARALLEL ===========
        if save_file:
            dir_name = create_dir('openaies')

        solver = openaies
        results_openaies = []
        with Pool() as pool:
            solver_zs = [(solver, z) for z in range(range_Z[0],range_Z[1]+1)]
            for result in pool.starmap(solver_for_Z, solver_zs):
                results_openaies.append(result)

        # sort by Z
        results_openaies.sort(key=(lambda r: r[0]))

        # get only the valid ones
        valid_results_openaies = get_valid_results(results_openaies)

        if len(valid_results_openaies) > 0:
            print("Best result openai-es")
            best_result_openaies = get_best_result(valid_results_openaies)

        # ======== SAVE ============
        # if len(valid_results_cmaes) > 0:
        #     save_best_result(best_result_cmaes, 'cmaes', seed)
        if len(valid_results_openaies) > 0:
            save_best_result(best_result_openaies, 'openaies', seed)
