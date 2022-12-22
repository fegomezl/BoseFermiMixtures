import sys
import numpy as np
import yaml
import tenpy

import config

# Parametros de la simulación
with open('settings/run_NB.yml', 'r') as f:
    parameters = yaml.safe_load(f)
parameters['N_B'] = int(sys.argv[1])
sim_params = config.read_settings(parameters)
sim_params['log_params']['filename'] = 'results/'+config.create_foldername(parameters)+'/'+config.create_filename(parameters)+'.log'

# Importar modelo (ladder or chain)
exec('import '+parameters['Type']+' as BFModel')

# Ejectar simulación
results = tenpy.run_simulation(**sim_params)

print(results['energy'])
