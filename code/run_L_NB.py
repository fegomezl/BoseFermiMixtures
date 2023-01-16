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

# Actualizar archivo de progreso
file = open('results/'+misc.create_foldername(parameters)+'/progress.txt', 'a')
file.write('\n'+str(parameters['N_B']))
file.close()

# Leer progreso actual
file = open('results/'+misc.create_foldername(parameters)+'/progress.txt', 'r')
A = []
for line in file.readlines():
    A.append(int(line))
file.close()

progress = '▢'*(A[1]-A[0]+1)
for ii in range(2, len(A)):
    progress = progress[0:A[ii]-A[0]]+'▣'+progress[A[ii]-A[0]+1:]
if len(A) == A[1]-A[0]+3:
    progress += '\n Finished: \n'+misc.create_foldername(parameters)

# Enviar notificación
misc.send_to_telegram('Finished: \n'+misc.create_filename(parameters)+'\n'+str(len(A)-2)+'/'+str(A[1]-A[0]+1)+'\n'+progress)
