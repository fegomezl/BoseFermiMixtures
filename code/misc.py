
def read_settings(parameters):

    # Configurar el formato correcto
    sim_params = {
        'simulation_class': 'GroundStateSearch',

        'model_class': 'BoseFermiHubbard',
        'model_params': {
            'bc_MPS': 'finite',
            'N_B_max': parameters['N_B_max'],

            'L': parameters['L'],
            
            't_B': parameters['t_B'],
            't_F': parameters['t_F'],
            'U_BB': parameters['U_BB'],
            'U_FF': parameters['U_FF'],
            'U_BF': parameters['U_BF'],
            'V_BB': parameters['V_BB'],
            'V_FF': parameters['V_FF'],
            'V_BF': parameters['V_BF'],
        },

        'initial_state_builder_class': 'BoseFermiState',
        'initial_state_params': {
            'method': 'filling',
            'N_B': parameters['N_B'],
            'N_FU': parameters['N_FU'],
            'N_FD': parameters['N_FD'],
        },
        
        'algorithm_class': 'TwoSiteDMRGEngine',
        'algorithm_params': {
            'min_sweeps': parameters['min_sweeps'],
            'max_sweeps': parameters['max_sweeps'],
            'max_E_err': parameters['max_E_err'],
            'max_S_err': parameters['max_S_err'],
            'trunc_params': {'chi_max': parameters['chi_max'],},
            'mixer': True,
        },

        'overwrite_output': parameters['overwrite_output'],
        'save_psi': parameters['save_psi'],
        'save_stats': parameters['save_stats'],
        'save_resume_data': parameters['save_resume_data'],
        'measure_initial': parameters['measure_initial'],
        'use_default_measurements': parameters['use_default_measurements'],

        'log_params': {
            'to_stdout': 'INFO',
            'to_file': 'INFO',
        },
    }

    return sim_params

def create_filename(parameters):

    # Crear nombre de archivo
    filename = 'BF{}_L{}_NB{}_NFU{}_NFD{}'.format(parameters['Type'],
                                                  parameters['L'],
                                                  parameters['N_B'],
                                                  parameters['N_FU'],
                                                  parameters['N_FD'])
    interactions =[['_UBB',parameters['U_BB']],
                   ['_UFF',parameters['U_FF']],
                   ['_UBF',parameters['U_BF']],
                   ['_VBB',parameters['V_BB']],
                   ['_VFF',parameters['V_FF']],
                   ['_VBF',parameters['V_BF']]]
    for ii in range(0, len(interactions)):
        if interactions[ii][1] != 0.:
            filename += interactions[ii][0]+'{0:.1f}'.format(interactions[ii][1])

    return filename

def create_foldername(parameters):

    # Crear nombre de archivo
    foldername = 'BF{}_L{}_NB_RHOFU{:.2f}_RHOFD{:.2f}'.format(parameters['Type'],
                                                                        parameters['L'],
                                                                        parameters['RHO_FU'],
                                                                        parameters['RHO_FD'])
    interactions =[['_UBB',parameters['U_BB']],
                   ['_UFF',parameters['U_FF']],
                   ['_UBF',parameters['U_BF']],
                   ['_VBB',parameters['V_BB']],
                   ['_VFF',parameters['V_FF']],
                   ['_VBF',parameters['V_BF']]]
    for ii in range(0, len(interactions)):
        if interactions[ii][1] != 0.:
            foldername += interactions[ii][0]+'{0:.1f}'.format(interactions[ii][1])

    return foldername
