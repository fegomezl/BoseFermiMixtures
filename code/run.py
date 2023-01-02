import yaml
import tenpy

import misc

# Parametros de la simulación
with open('settings/run.yml', 'r') as f:
    parameters = yaml.safe_load(f)
sim_params = misc.read_settings(parameters)
sim_params['output_filename'] = 'results/'+misc.create_filename(parameters)+'.h5'

# Importar modelo (ladder or chain)
exec('import '+parameters['Type']+' as BFModel')

# Ejectar simulación
results = tenpy.run_simulation(**sim_params)
