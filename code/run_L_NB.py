import sys
import yaml
import tenpy

import misc

# Parametros de la simulación
with open('settings/run_L_NB.yml', 'r') as f:
    parameters = yaml.safe_load(f)
parameters['L'] = int(sys.argv[1])
parameters['N_FU'] = int(sys.argv[2])
parameters['N_FD'] = int(sys.argv[3])
parameters['N_B'] = int(sys.argv[4])
sim_params = misc.read_settings(parameters)
sim_params['log_params']['filename'] = 'results/'+misc.create_foldername(parameters)+'/'+misc.create_filename(parameters)+'.log'

# Importar modelo (ladder or chain)
exec('import '+parameters['Type']+' as BFModel')

# Ejectar simulación
results = tenpy.run_simulation(**sim_params)

# Notify telegram
misc.send_to_telegram('Finished: \n'+misc.create_filename(parameters))
