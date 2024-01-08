import numpy as np
import random
from es import CMAES, OpenES

from oct2py import Oct2Py
from multiprocessing.pool import ThreadPool
from multiprocessing import Pool

from files_def_multiple_runs import *


# -------- range of the variables ----------
range_D     = [0.5, 0.8]
range_AEdAO = [0.3, 1.05]
range_PdD   = [0.5, 1.4]
range_Z     = [2, 7]

# Define the lower and upper bounds for each variable
lower_bounds = [range_D[0], range_AEdAO[0], range_PdD[0]]
upper_bounds = [range_D[1], range_AEdAO[1], range_PdD[1]]

NPARAMS = 3  # number of parameters to evaluate

# diretories tree
#
# dir_run
#   |_ dir_vs
#        |_ dir_seed

# ------- logic ---------
def run_octave_evaluation(V_S,D,Z,AEdAO,PdD):
    P_B, t075dD,tmin075dD, tal07R,cavLim, Vtip,Vtipmax = [-1, -1, -1, -1, -1, -1, -1]
    with Oct2Py() as octave:
        octave.warning ("off", "Octave:data-file-in-path");
        octave.addpath('./allCodesOctave');
        P_B, n, etaO,etaR, t075dD,tmin075dD, tal07R,cavLim, Vtip,Vtipmax = octave.F_LabH2_return_constraints(V_S,D,Z,AEdAO,PdD, nout=10)
    return [P_B, t075dD,tmin075dD, tal07R,cavLim, Vtip,Vtipmax]

# calculate the fitness
# fitness function, to find the minimal power brake
def evaluate_solution(x):
    D     = x[0]
    AEdAO = x[1]
    PdD   = x[2]

#     P_B, t075dD,tmin075dD, tal07R,cavLim, Vtip,Vtipmax
    P_B, strength,strengthMin, cavitation,cavitationMax, velocity,velocityMax = run_octave_evaluation(V_S,D,Z,AEdAO,PdD)

    # Fitness is Power Brake multiplied by 1 + the percentage of each constraint
    fit_value = P_B * (1 + max(((cavitation - cavitationMax)/cavitationMax), 0) + max(((velocity - velocityMax)/velocityMax), 0) + max(((strengthMin - strength)/strengthMin), 0) )

    # we want the minimal P_B
    # the solvers use the max value as best fitness, so
    fit_value *= -1

    # save to the file
    penalty = max(((cavitation - cavitationMax)/cavitationMax), 0) + max(((velocity - velocityMax)/velocityMax), 0) + max(((strengthMin - strength)/strengthMin), 0)
    valid = (penalty == 0)
    append_to_file(filename, [D, AEdAO, PdD, Z, P_B, 0, fit_value, strength,strengthMin, cavitation,cavitationMax, velocity,velocityMax, penalty, valid])

    return fit_value
# use evaluate_solution as the fitness function
fit_func = evaluate_solution

# defines a function to use solver to solve fit_func
def test_solver(solver):
    # history of the best fitness at each iteration (generation)
    history = np.zeros(MAX_ITERATION)
    for j in range(MAX_ITERATION):
        # ask for the population
        solutions = solver.ask()
        # create a list with the fitness
        fitness_list = np.zeros(solver.popsize)
        # parallel run of fitness evaluation
        with ThreadPool() as pool:
            id_solutions = [(i, solutions[i]) for i in range(len(solutions))]
            # wrapper to add the index of solution in the array, to the response of the ThreadPool
            # this keeps the fitness_list and solutions list in the same order (necessary)
            fit_func_parallel_wrapper = (lambda i, x: [i, fit_func(x)] )
            for result in pool.starmap(fit_func_parallel_wrapper, id_solutions, chunksize=4):
                i, fitness = result
                fitness_list[i] = fitness
        # pass the fitness to the solver so it can decide the best individual
        solver.tell(fitness_list)
        result = solver.result() # first element is the best solution, second element is the best fitness
        history[j] = result[1]   # best fitness
        # print the process name (Z) and the iteration, and save in the csv
        print('Z:',Z, "fitness at iteration", (j+1), result[1], flush=True)
        append_to_file_order(filename, "fitness at iteration", j, fitness=result[1])
    # best solution at the end of the solver's run
    print("local optimum discovered by solver:\n", result[0])
    print("fitness score at this local optimum:", result[1])
    return (history, result[0])

# ==== Logic ====
def solver_for_Z(solver, z, dir_solver):
    global Z
    Z = z

    # create the csv file with the headers
    global filename
    filename = create_file(dir_solver, str(Z))

    # run the solver
    history, best_solution = test_solver(solver)

    # print best solution
    D       = best_solution[0]
    AEdAO   = best_solution[1]
    PdD     = best_solution[2]
    fitness = history[-1]
    print("Z:",Z, "Best Solution:", best_solution, 'with fitness:', fitness)

    # write best solution to file
    append_to_file(filename, ["Best Solution"])
    append_to_file_order(filename, D=D, AEdAO=AEdAO, PdD=PdD, Z=Z, fitness=fitness)

    return [Z, best_solution, fitness, history]

def get_valid_results(results):
    valid_results = []

    for r in results:
        Z             =  r[0]
        D, AEdAO, PdD =  r[1]
        fitness       = -r[2]
        # run the evaluation
        P_B, t075dD,tmin075dD, tal07R,cavLim, Vtip,Vtipmax = run_octave_evaluation(V_S,D,Z,AEdAO,PdD)
        # if the fitness and the P_B are the same, then there is no penalty on the fitness, and thus a valid result
        if fitness == P_B:
            valid_results.append(r)

    return valid_results

# === Start ===
def run_solver(dir_seed, solver, solver_name, vs, seed, n_population, max_iteration):
    global V_S, NPOPULATION, MAX_ITERATION
    V_S = vs
    NPOPULATION = n_population
    MAX_ITERATION = max_iteration

    random.seed(seed)

    # run the solver in parallel
    results_list = []
    with Pool() as pool:
        solver_zs = [(solver, z, dir_seed) for z in range(range_Z[0],range_Z[1]+1)]
        for result in pool.starmap(solver_for_Z, solver_zs):
            results_list.append(result)

            # sort by Z
            results_list.sort(key=(lambda r: r[0]))

            # get only the valid ones
            valid_results = get_valid_results(results_list)

            if len(valid_results) > 0:
                print("Best result", solver_name)
                best_result = get_best_result(valid_results)
                # save
                Z             =  best_result[0]
                D, AEdAO, PdD =  best_result[1]
                fitness       = -best_result[2]
                history       =  best_result[3]
                save_best_result(dir_seed, solver_name, V_S, NPOPULATION, MAX_ITERATION, seed, D, Z, AEdAO, PdD, fitness, history=history)

    return best_result
