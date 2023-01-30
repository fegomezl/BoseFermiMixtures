import yaml

import BFModel
import misc

# Read parameters
with open('settings/run.yml', 'r') as f:
    parameters = yaml.safe_load(f)
sim_parameters = misc.read_settings(parameters, 'results')

# Run simulation and notify telegram
filename = sim_parameters['filename']
misc.send_to_telegram('Started: \n'+filename, 'settings/telegram.yml')
BFModel.run(sim_parameters)
misc.send_to_telegram('Finished: \n'+filename, 'settings/telegram.yml')
