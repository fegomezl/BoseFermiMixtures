import os
import numpy as np
import tenpy
from tenpy.simulations.simulation import output_filename_from_dict

import BFChain as BFModel

#Parametros del sistema

bc = 'finite'
N_B_max = 1

L = 18
RHO_B = 0.
RHO_FU = 0.5
RHO_FD = 0.5

N_B = int(L*RHO_B+0.5)
N_FU = int(L*RHO_FU+0.5)
N_FD = int(L*RHO_FD+0.5)

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
        'max_S_err': 1e-5,  #|Delta_S| < max_S_eRR

        'trunc_params': {
            'chi_max': 500,  #Máxima dimensión de enlace
        },
        'chi_list': None,
        
        'mixer': True,  #Ayuda a evitar minimos locales
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

#Inicializar encabezados de los resultados
data = ["{:<8} {:<15} {:<15}".format('RHO_B','E','MU')]

#Crear carpeta para los datos
sim_params['initial_state_params']['N_B'] = 0
filename = output_filename_from_dict(sim_params, sim_params['output_filename_params']['parts'], '', '')[1:].replace('NB0', 'NB')
folder = 'results/'+filename+'/'
if not os.path.exists('results'):
    os.mkdir('results')
if not os.path.exists(folder):
    os.mkdir(folder)

#Actualizar nombres de archivos concorde a la carpeta
sim_params['output_filename_params']['prefix'] = folder+BFModel.FILENAME_PREFIX
sim_params['log_params']['filename'] = folder+BFModel.FILENAME_PREFIX+'_'+filename+'.log'

#Realizar primera medición
results = tenpy.run_simulation(**sim_params)
E_old = results['energy']
data.append("{:<8.5f} {:<15.10f}".format(0,E_old))

#Realizar las demas mediciones
for nb in range(1, L+1):
    sim_params['initial_state_params']['N_B'] = nb
    results = tenpy.run_simulation(**sim_params)
    E_new = results['energy']
    MU = E_new - E_old 
    data.append("{:<8.5f} {:<15.10f} {:<15.10f}".format(nb/L, E_new, MU))
    E_old = E_new

#Imprimir datos finales en pantalla
for d in data:
    print(d)

#Imprimir datos finales en un archivo
with open(folder+BFModel.FILENAME_PREFIX+'_'+filename+'.txt', 'w') as f:
    for d in data:
        f.write(d)
        f.write('\n')
