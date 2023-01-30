import os
import multiprocessing
import yaml

import BFModel
import misc
import postproccesing

# Read parameters for set of simulations
with open('settings/run_L_NB.yml', 'r') as f:
    parameters = yaml.safe_load(f)

# Create folder for results
foldername_L = misc.create_name(parameters, 'L')
if not os.path.exists('results'):
    os.mkdir('results')
if not os.path.exists('results/'+foldername_L):
    os.mkdir('results/'+foldername_L)

# Create set of parameters for simulations for varying L and NB
L_list = []
NB_list = []
foldername_NB_list = []
sim_parameters_list = []
for ii in range(0, parameters['NL']):

    # Change chain lenght(L)
    parameters['L'] = parameters['L_I']+ii*parameters['DL']
    L_list.append(parameters['L'])

    # Create folder for given L
    foldername_NB = misc.create_name(parameters, 'NB')
    if not os.path.exists('results/'+foldername_L+'/'+foldername_NB):
        os.mkdir('results/'+foldername_L+'/'+foldername_NB)
    foldername_NB_list.append(foldername_NB)

    # Check if boson density is exact or not, for given resolution
    if parameters['EXACT_B']:
        NB_I = int(parameters['L']*parameters['RHO_B'] + 0.5)-parameters['RES_B']
    else:
        NB_I = int(parameters['L']*parameters['RHO_B'])-parameters['RES_B']
    parameters['N_FU'] = int(parameters['L']*parameters['RHO_FU'] + 0.5)
    parameters['N_FD'] = int(parameters['L']*parameters['RHO_FD'] + 0.5)

    # Save simulations for given range of NB
    for jj in range(0, 2*parameters['RES_B']+1):
        parameters['N_B'] = NB_I + jj
        sim_parameters_list.append(misc.read_settings(parameters, 'results/'+foldername_L+'/'+foldername_NB, ii*(2*parameters['RES_B']+1)+jj))
        NB_list.append(parameters['N_B'])

# Run all simulations in parallel while notifying telegram for each finished simulation
progress = ['▢'*(2*parameters['RES_B']+1)]*parameters['NL']
total_progress = progress[0]
for n in range(1, len(progress)):
    total_progress = total_progress + '\n' + progress[n]
total_L = str(L_list[0])
for n in range(1, len(L_list)):
    total_L = total_L+','+str(L_list[n])
misc.send_to_telegram('Started: '+str(parameters['NL']*(2*parameters['RES_B']+1))+' jobs:\n'+foldername_L+'\n'+'L= '+total_L+'\n'+total_progress, 'settings/telegram.yml')
pool = multiprocessing.Pool(processes=parameters['cores'])
for result in pool.imap_unordered(BFModel.run, sim_parameters_list):
    ii = result//(2*parameters['RES_B']+1)
    jj = result%(2*parameters['RES_B']+1)
    progress[ii] = progress[ii][0:jj]+'▣'+progress[ii][jj+1:]

    # If all of simulations for given L are completed, analyse data
    if progress[ii] == '▣'*(2*parameters['RES_B']+1):
        postproccesing.postproccesing_NB('results/'+foldername_L+'/'+foldername_NB_list[ii])

    total_progress = progress[0]
    for n in range(1, len(progress)):
        total_progress = total_progress + '\n' + progress[n]
    misc.send_to_telegram('Finished L='+str(L_list[ii])+' NB='+str(NB_list[result])+' from\n'+foldername_L+'\n'+total_progress, 'settings/telegram.yml')
misc.send_to_telegram('Finished:\n'+foldername_L, 'settings/telegram.yml')
