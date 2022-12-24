import os
import sys
import numpy as np
import yaml
import tenpy

import config

# Parametros de la simulación
with open('settings/run.yml', 'r') as f:
    parameters = yaml.safe_load(f)
parameters = config.use_densities(parameters)
sim_params = config.read_settings(parameters)

# Crear carpeta para los datos
foldername = config.create_foldername(parameters)
if not os.path.exists('results'):
    os.mkdir('results')
if not os.path.exists('results/'+foldername):
    os.mkdir('results/'+foldername)
sim_params['log_params']['filename'] = 'results/'+foldername+'/'+foldername+'.log'

# Importar modelo (ladder or chain)
exec('import '+parameters['Type']+' as BFModel')

#Inicializar encabezados de los resultados
data = ["{:<8} {:<15} {:<15}".format('RHO_B','E','MU')]

#Realizar primera medición
N_B = 0
sim_params['initial_state_params']['N_B'] = N_B
sim_params['output_filename'] = 'results/'+foldername+'/'+config.create_filename(parameters)+'.h5'
results = tenpy.run_simulation(**sim_params)
E_old = results['energy']
data.append("{:<8.5f} {:<15.10f}".format(0,E_old))

#Realizar las demas mediciones
for N_B in range(1, parameters['L']+1):
    parameters['N_B'] = N_B
    sim_params['initial_state_params']['N_B'] = N_B
    sim_params['output_filename'] = 'results/'+foldername+'/'+config.create_filename(parameters)+'.h5'
    results = tenpy.run_simulation(**sim_params)
    E_new = results['energy']
    MU = E_new - E_old 
    data.append("{:<8.5f} {:<15.10f} {:<15.10f}".format(N_B/parameters['L'], E_new, MU))
    E_old = E_new

#Imprimir datos finales en pantalla
for d in data:
    print(d)

#Imprimir datos finales en un archivo
with open('results/'+foldername+'/'+foldername+'.txt', 'w') as f:
    for d in data:
        f.write(d)
        f.write('\n')
