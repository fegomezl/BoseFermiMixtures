import os
import yaml

import misc

# Parametros de la simulación
with open('settings/run_NB.yml', 'r') as f:
    parameters = yaml.safe_load(f)

# Actualizar número de particulas por densidades
parameters['N_B_I'] = int(parameters['L']*parameters['RHO_B_I'] + 0.5)
parameters['N_B_F'] = int(parameters['L']*parameters['RHO_B_F'] + 0.5)
parameters['N_FU'] = int(parameters['L']*parameters['RHO_FU'] + 0.5)
parameters['N_FD'] = int(parameters['L']*parameters['RHO_FD'] + 0.5)

with open('settings/run_NB.yml', 'w') as f:
    yaml.dump(parameters, f, default_flow_style=False, sort_keys=False)

# Crear carpeta para los datos
foldername = misc.create_foldername(parameters)
if not os.path.exists('results'):
    os.mkdir('results')
if not os.path.exists('results/'+foldername):
    os.mkdir('results/'+foldername)
