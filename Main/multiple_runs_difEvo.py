import pandas as pd

from oct2py import Oct2Py
from multiprocessing import Pool

from files_def_multiple_runs import *

SOLVER_NAME = 'DE'

# population and generations arent set here, this is only to put in the config files
NPOPULATION   = 30
MAX_ITERATION = 30


# ==== parallel run DE ====
def get_best_fit_number(x):
    for i in range(len(x)):
        x.iloc[i] = x.iloc[i][len('best fit at iteration '):]
    return x

def parallel_seed_run(dir_vs, seed, V_S):
    print('-----', seed, '-----')

    # ex: run/7_0/1
    dir_seed = dir_vs +'/' + str(seed)
    mkdir(dir_seed)

    create_config_file_DifEvo(dir_seed, SOLVER_NAME, V_S, NPOPULATION, MAX_ITERATION, seed, False)

    filename_allRun = dir_seed + '/' + 'allRunSaved_' + str(seed) + '.csv'

    # run DE
    with Oct2Py() as octave:
        octave.warning ("off", "Octave:data-file-in-path");
        octave.addpath('./allCodesOctave');
        octave.eval('pkg load statistics')
        D, Z, AEdAO, PdD, P_B = octave.F_DifEvo_LH2_return_constraints(V_S, filename_allRun, nout=5)

    best_result = (D, Z, AEdAO, PdD, P_B)
    print("Best result", SOLVER_NAME)
    print('P_B:',P_B)
    print('D:',D)
    print('AEdAO:',AEdAO)
    print('PdD:',PdD)
    print('Z:',Z)

    # ======== Make CSV in same pattern as CMA-ES and OpenAI-ES ============
    col_names_DE = ['D', 'Z', 'AEdAO', 'PdD', 'P_B', 'n', 'etaO', 'etaR', 't075dD','tmin075dD', 'tal07R','cavLim', 'Vtip','Vtipmax', 'fitness', 'iteration', 'population_i']
    col_names = ['D', 'AEdAO', 'PdD', 'Z', 'P_B', 'n', 'fitness', 't075dD','tmin075dD', 'tal07R','cavLim', 'Vtip','Vtipmax', 'penalty', 'valid']

    df = pd.read_csv(filename_allRun, header=None, skiprows=1, names=col_names_DE)

    df = df[['D', 'AEdAO', 'PdD', 'Z', 'P_B', 'n', 'fitness', 't075dD','tmin075dD', 'tal07R','cavLim', 'Vtip','Vtipmax']]

    # -- Calculate validity --

    # insert the other collumns
    df.insert(df.shape[1], 'penalty', None)

    df.insert(df.shape[1], 'valid', True)

    # create temporary cols
    df['temp_cav'] = (df['tal07R'] - df['cavLim'])/df['cavLim']
    df['temp_cav'] = df['temp_cav'].clip(lower=0)
    df['temp_spd'] = (df['Vtip'] - df['Vtipmax'])/df['Vtipmax']
    df['temp_spd'] = df['temp_spd'].clip(lower=0)
    df['temp_str'] = (df['tmin075dD'] - df['t075dD'])/df['tmin075dD']
    df['temp_str'] = df['temp_str'].clip(lower=0)
    # calculate
    df['penalty'] = df['temp_cav'] + df['temp_spd'] + df['temp_str']
    df['valid'] = (df['penalty'] == 0)
    # drop temporary cols
    df = df.drop(['temp_cav', 'temp_spd', 'temp_str'], axis=1)


    # ajust the iteration counter with fitness
    df['D'] = df['D'].astype(str)
    df.loc[df['D'].str.contains('best'), 'fitness'] = df.loc[df['D'].str.contains('best'), 'Z']
    df.loc[df['D'].str.contains('best'), 'Z'] = None

    df.loc[df['D'].str.contains('best'), 'AEdAO'] = get_best_fit_number(df.loc[df['D'].str.contains('best'), 'D'])
    df.loc[df['D'].str.contains('best'), 'D'] = 'fitness at iteration'

    # -- add best value to the end --
    best_fit_to_find = df.loc[len(df)-1]['fitness'] # best fitness at last interation
    result_row = df[(df['P_B'] == best_fit_to_find) & (df['D'] != 'fitness at iteration')] # find row with best fitness
    df.loc[len(df)] = {'D': 'Best Solution'} # add text to the bottom
    df.loc[len(df)] = result_row.iloc[0] # add row with values in the end

    # save file
    filename_out = dir_seed+'/'+str(seed)+'.csv'
    df.to_csv(filename_out, index=False, header=True)

    print('saved:', filename_out)

    # ================ Best result file ================
    fitness = P_B

    # read csv file to generate history
    history = []
    with open(filename_out, 'r', newline='') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            if 'fitness' in row[0]:
                fit = -float(row[6])
                history.append(str(fit))

    save_best_result(dir_seed, SOLVER_NAME, V_S, NPOPULATION, MAX_ITERATION, seed, D, Z, AEdAO, PdD, fitness, P_B=P_B, history=history)

    return [P_B, D, AEdAO, PdD, Z, seed]


def run_multiple_DifEvo(NUMBER_OF_SEEDS_TO_RUN, V_S_list):
    global dir_run

    now = datetime.now()
    dir_run = SOLVER_NAME+'_'+ now.strftime("%Y_%m_%d_%Hh%M")
    mkdir(dir_run)

    for vs in V_S_list:
        V_S = vs

        # create dir for VS
        dir_vs = dir_run +'/'+ str(V_S).replace('.','_')
        mkdir(dir_vs)

        print('======', V_S, '======')

        results_list = []
        with Pool() as pool:
            seeds_list = [(dir_vs, seed, V_S) for seed in range(NUMBER_OF_SEEDS_TO_RUN)]
            for result in pool.starmap(parallel_seed_run, seeds_list):
                results_list.append(result)

        for result in results_list:
            print(result)


if __name__ == '__main__':
    # run for this number of seeds
    NUMBER_OF_SEEDS_TO_RUN = 10

    # list of V_S, each V_S in the list will be run NUMBER_OF_SEEDS_TO_RUN times
    # dont run for V_S >= 8.0
    V_S_list = [7.0, 7.5]

    run_multiple_DifEvo(NUMBER_OF_SEEDS_TO_RUN, V_S_list)
