import numpy as np
import tenpy

import BFLadder as BFModel

#Parametros del sistema

bc = 'finite'
N_B_max = 1

L = 8
N_B = 4
N_FU = 4
N_FD = 4

t_B = 1.
t_F = 1.
U_BB = 0.
U_FF = 4.
U_BF = 6.
V_BB = 0.
V_FF = 4.
V_BF = 0.

#Parametros de la simulación

sim_params = {
    'simulation_class': 'GroundStateSearch',
    
    'model_class': 'BosonFermiHubbard',                 
    'model_params': {
        'bc_MPS': bc,
        'N_B_max': N_B_max,

        'L': L,   
        
        't_B': t_B, 
        't_F': t_F,
        'U_BB': U_BB,
        'U_FF': U_FF,
        'U_BF': U_BF,
        'V_BB': V_BB,
        'V_FF': V_FF,
        'V_BF': V_BF,
    },

    'initial_state_builder_class': 'BosonFermiState',   
    'initial_state_params': {
        'method': 'filling',
        'N_B': N_B,
        'N_FU': N_FU,
        'N_FD': N_FD,
    },
    
    'algorithm_class': 'TwoSiteDMRGEngine',
    'algorithm_params': {
        'min_sweeps': 1,
        'max_sweeps': 1000,
        'max_hours': 12,
        'max_E_err': 1e-8,  #-Delta_E/max(|E|, 1) < max_E_err 
        'max_S_err': 1e-5,  #|Delta_S| < max_S_err
        
        'trunc_params': {
            'chi_max': 500, #Máxima dimensión de enlace
        },
        
        'mixer': True,      #Ayuda a evitar minimos locales
        'mixer_params': {
            'amplitude': 1.e-6,
            'decay': 1.,
            'disable_after': 20,
        },
    },

    'output_filename_params': {
            'prefix': 'results/'+BFModel.FILENAME_PREFIX,
            'parts': {
                'model_params.L': 'L{0:d}',
                'initial_state_params.N_B': 'NB{0:d}',
                'initial_state_params.N_FU': 'NFU{0:d}',
                'initial_state_params.N_FD': 'NFD{0:d}',
                'model_params.U_BB': 'UBB{0:.0f}',
                'model_params.U_FF': 'UFF{0:.0f}',
                'model_params.U_BF': 'UBF{0:.0f}',
                'model_params.V_BB': 'VBB{0:.0f}',
                'model_params.V_FF': 'VFF{0:.0f}',
                'model_params.V_BF': 'VBF{0:.0f}',
            },
            'suffix': '.h5',
    },
    'overwrite_output': False,
    'save_every_x_seconds': None,
    'save_psi': True,
    'save_stats': True,
    'save_resume_data': True,
    'measure_initial': True,
    'use_default_measurements': True,

    'log_params': {
        'to_stdout': 'INFO',
        'to_file': 'INFO',
    },
}

results = tenpy.run_simulation(**sim_params)

print(results['energy'])
