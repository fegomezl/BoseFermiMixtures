import os
import multiprocessing
import yaml

import BFModel
import misc
import postproccesing

# Read parameters for set of simulations
with open('settings/run_NB.yml', 'r') as f:
    parameters = yaml.safe_load(f)

# Create folder for results
foldername = misc.create_name(parameters, 'NB')
if not os.path.exists('results'):
    os.mkdir('results')
if not os.path.exists('results/'+foldername):
    os.mkdir('results/'+foldername)

# Calculate bounds for boson number
NB_I = int(parameters['L']*parameters['RHO_B_I'] + 0.5)
NB_F = int(parameters['L']*parameters['RHO_B_F'] + 0.5)
parameters['N_FU']  = int(parameters['L']*parameters['RHO_FU']  + 0.5)
parameters['N_FD']  = int(parameters['L']*parameters['RHO_FD']  + 0.5)

# Save set of parameters for simulations
sim_parameters_list = []
for nb in range(NB_I, NB_F+1):
    parameters['N_B'] = nb
    sim_parameters_list.append(misc.read_settings(parameters, 'results/'+foldername, nb))

# Run all simulations in parallel while notifying telegram for each finished simulation
progress = '▢'*(NB_F-NB_I+1)
misc.send_to_telegram('Started: '+str(NB_F-NB_I+1)+' jobs:\n'+foldername+'\nNB= '+str(NB_I)+':'+str(NB_F)+'\n'+progress, 'settings/telegram.yml')
pool = multiprocessing.Pool(processes=parameters['cores'])
for result in pool.imap_unordered(BFModel.run, sim_parameters_list):
    progress = progress[0:result-NB_I]+'▣'+progress[result-NB_I+1:]
    misc.send_to_telegram('Finished NB='+str(result)+' from\n'+foldername+'\n'+progress, 'settings/telegram.yml')

# Get global results from all of the simulations
postproccesing.postproccesing_NB('results/'+foldername)
misc.send_to_telegram('Finished:\n'+foldername, 'settings/telegram.yml')
