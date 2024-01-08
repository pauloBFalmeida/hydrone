import numpy as np
import random
from es import CMAES, OpenES

from ES_logic_multiple_runs import *

from files_def_multiple_runs import create_config_file_ES

SIGMA_INIT_CMAES = 0.1
SOLVER_NAME = 'cmaes'

# === Start ===
def run_multiple_Cmaes(NUMBER_OF_SEEDS_TO_RUN, V_S_list, NPOPULATION, MAX_ITERATION):
    global dir_run

    now = datetime.now()
    dir_run = SOLVER_NAME+'_'+ now.strftime("%Y_%m_%d_%Hh%M")
    mkdir(dir_run)

    for vs in V_S_list:
        global V_S
        V_S = vs

        # create dir for VS
        dir_vs = dir_run +'/'+ str(V_S).replace('.','_')
        mkdir(dir_vs)

        print('======', V_S, '======')
        for seed in range(NUMBER_OF_SEEDS_TO_RUN):
            print('-----', seed, '-----')

            random.seed(seed)
            x0 =  [
                    random.uniform(range_D[0],     range_D[1]),
                    random.uniform(range_AEdAO[0], range_AEdAO[1]),
                    random.uniform(range_PdD[0],   range_PdD[1])
                  ]

            # defines CMA-ES algorithm solver
            cmaes = CMAES(NPARAMS,
                          x0=x0,                     # initial parameters values to generate the population
                          popsize=NPOPULATION,
                          weight_decay=0.0,
                          sigma_init = SIGMA_INIT_CMAES,
                          lower_bounds=lower_bounds,
                          upper_bounds=upper_bounds,
                      )

            # dir for the seed execution
            dir_seed = dir_run +'/'+ str(V_S).replace('.','_') +'/' + str(seed)
            mkdir(dir_seed)

            # create config file
            create_config_file_ES(dir_seed, SOLVER_NAME, V_S, NPOPULATION, MAX_ITERATION, seed, x0, SIGMA_INIT_CMAES)

            try:
                best_result = run_solver(dir_seed, cmaes, SOLVER_NAME, V_S, seed, NPOPULATION, MAX_ITERATION)
                print(best_result)
            except: pass

if __name__ == '__main__':
    # run for this number of seeds
    NUMBER_OF_SEEDS_TO_RUN = 10

    # list of V_S, each V_S in the list will be run NUMBER_OF_SEEDS_TO_RUN times
    V_S_list = [7.0, 7.5, 8.0, 8.5]

    # ES settings
    NPOPULATION   = 10 # size of population
    MAX_ITERATION = 30 # run solver for this generations

    run_multiple_Cmaes(NUMBER_OF_SEEDS_TO_RUN, V_S_list, NPOPULATION, MAX_ITERATION)
