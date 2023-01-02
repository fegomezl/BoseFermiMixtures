import sys
import os
import yaml

import misc

# Parametros de la simulación
with open('settings/run_L_NB.yml', 'r') as f:
    parameters = yaml.safe_load(f)
L = int(sys.argv[1])

# Encontrar puntos mas proximos a la densidad
# Actualizar número de particulas por densidades
N_B = int(L*parameters['RHO_B'] + 0.5)
RHO_B_aux = N_B/L

if RHO_B_aux < parameters['RHO_B']:
    parameters['N_B_I'] = N_B - parameters['RES_B']
    parameters['N_B_F'] = N_B + parameters['RES_B']
elif RHO_B_aux > parameters['RHO_B']:
    parameters['N_B_I'] = N_B - parameters['RES_B'] - 1
    parameters['N_B_F'] = N_B + parameters['RES_B'] - 1
elif RHO_B_aux == parameters['RHO_B']:
    parameters['N_B_I'] = N_B - parameters['RES_B'] - 1
    parameters['N_B_F'] = N_B + parameters['RES_B']

parameters['N_FU'] = int(L*parameters['RHO_FU'] + 0.5)
parameters['N_FD'] = int(L*parameters['RHO_FD'] + 0.5)

with open('settings/run_L_NB.yml', 'w') as f:
    yaml.dump(parameters, f, default_flow_style=False, sort_keys=False)

# Crear carpeta para los datos
parameters['L'] = L
foldername = misc.create_foldername(parameters)
if not os.path.exists('results'):
    os.mkdir('results')
if not os.path.exists('results/'+foldername):
    os.mkdir('results/'+foldername)