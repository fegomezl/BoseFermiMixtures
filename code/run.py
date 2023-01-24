import os
import numpy as np
import pandas as pd

import yaml
import tenpy

import misc

# Parametros de la simulación
with open('settings/run.yml', 'r') as f:
    parameters = yaml.safe_load(f)
sim_params = misc.read_settings(parameters)
filename = misc.create_filename(parameters)
sim_params['log_params']['filename'] = 'results/'+filename+'.aux'

# Importar modelo (ladder or chain)
exec('import '+parameters['Type']+' as BFModel')

# Notify telegram
misc.send_to_telegram('Started: \n'+filename)

# Ejectar simulación
results = tenpy.run_simulation(**sim_params)

# Guardar resultados
N = results['sweep_stats']['sweep']
t = results['sweep_stats']['time']
E = results['sweep_stats']['E']
S = results['sweep_stats']['S']
dt = [t[0]]
dE = [np.NaN]
dS = [S[0]]
for ii in range(1, N[-1]):
    dt.append(t[ii]-t[ii-1])
    dE.append(-(E[ii]-E[ii-1])/max(np.abs(E[ii]), 1))
    dS.append(np.abs(S[ii]-S[ii-1]))
out = pd.DataFrame(np.array([N, t, dt, E, dE, S, dS]).T, 
                   columns=['Sweep', 'Time', 'Duration', 'Energy', 'Energy_error', 'Entropy', 'Entropy_error'])
out.to_csv('results/'+filename+'.log', index=False)

f1 = open('results/'+filename+'.log', 'a+')
f2 = open('results/'+filename+'.aux', 'r')

f1.write('\n\n')
f1.write(f2.read())

f1.close()
f2.close()

os.remove('results/'+filename+'.aux')

if parameters['save_psi'] == True:
    Nb = results['psi'].expectation_value(['Nb'])
    Nf = results['psi'].expectation_value(['Nf'])
    Nfu = results['psi'].expectation_value(['Nfu'])
    Nfd = results['psi'].expectation_value(['Nfd'])
    NfuNfd = results['psi'].expectation_value(['NfuNfd'])
    ex_val = pd.DataFrame(np.array([range(len(Nb)),Nb, Nf, Nfu, Nfd, NfuNfd]).T, columns=['Site', 'Nb', 'Nf', 'Nfu', 'Nfd', 'NfuNfd'])
    ex_val.to_csv('results/'+filename+'.out', index=False)

# Notify telegram
misc.send_to_telegram('Finished: \n'+filename)
