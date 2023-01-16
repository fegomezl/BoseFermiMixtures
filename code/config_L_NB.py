import sys
import os
import yaml

import misc

# Parametros de la simulación
with open('settings/run_L_NB.yml', 'r') as f:
    parameters = yaml.safe_load(f)
L = int(sys.argv[1])

# Encontrar puntos mas proximos a la densidad
# Actualizar número de particulas por densidades

if parameters['EXACT_B'] == 1:
    parameters['N_B_I'] = int(L*parameters['RHO_B'])-parameters['RES_B']
    parameters['N_B_F'] = int(L*parameters['RHO_B'])+parameters['RES_B']
else:
    parameters['N_B_I'] = int(L*parameters['RHO_B'] + 0.5)-parameters['RES_B']
    parameters['N_B_F'] = int(L*parameters['RHO_B'] + 0.5)+parameters['RES_B']

parameters['N_FU'] = int(L*parameters['RHO_FU'] + 0.5)
parameters['N_FD'] = int(L*parameters['RHO_FD'] + 0.5)

with open('settings/run_L_NB.yml', 'w') as f:
    yaml.dump(parameters, f, default_flow_style=False, sort_keys=False)

# Crear carpeta para los datos
parameters['L'] = L
foldername = misc.create_foldername(parameters)
if not os.path.exists('results'):
    os.mkdir('results')
if not os.path.exists('results/'+foldername):
    os.mkdir('results/'+foldername)

# Crear archivo de progreso
file = open('results/'+misc.create_foldername(parameters)+'/progress.txt', 'w')
file.write(str(parameters['N_B_I'])+'\n')
file.write(str(parameters['N_B_F']))
file.close()

# Notify telegram
misc.send_to_telegram('Started '+str(parameters['N_B_F']-parameters['N_B_I']+1)+' jobs:\n'+misc.create_foldername(parameters)+'\nNB: ('+str(parameters['N_B_I'])+','+str(parameters['N_B_F'])+')')
