import sys
import numpy as np
import yaml
import tenpy

import config

# Parametros de la simulación
with open('settings/run.yml', 'r') as f:
    parameters = yaml.safe_load(f)
sim_params = config.read_settings(parameters)
sim_params['output_filename'] = 'results/'+config.create_filename(parameters)

# Importar modelo (ladder or chain)
exec('import '+parameters['Type']+' as BFModel')

# Ejectar simulación
results = tenpy.run_simulation(**sim_params)

print(results['energy'])
