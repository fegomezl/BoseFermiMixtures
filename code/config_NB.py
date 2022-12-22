import os
import sys
import numpy as np
import yaml
import tenpy

import config

# Parametros de la simulación
with open('settings/run_NB.yml', 'r') as f:
    parameters = yaml.safe_load(f)

# Actualizar número de particulas por densidades
parameters = config.use_densities(parameters)
with open('settings/run_NB.yml', 'w') as f:
    yaml.dump(parameters, f, default_flow_style=False, sort_keys=False)

# Crear carpeta para los datos
foldername = config.create_foldername(parameters)
if not os.path.exists('results'):
    os.mkdir('results')
if not os.path.exists('results/'+foldername):
    os.mkdir('results/'+foldername)
