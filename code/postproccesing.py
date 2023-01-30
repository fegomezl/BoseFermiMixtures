import sys
import os
import numpy as np
import pandas as pd

# Read last line from log files
def read_last(filepath):
    file = open(filepath, "r")
    N = -1
    for line in file.readlines():
        if line in ['\n', '\r\n']:
            break
        N +=1
    return list(pd.read_csv(filepath, sep=',', nrows=N).iloc[-1])

# Get global information for a set of simulations with changing boson number
def postproccesing_NB(folder):

    # Check folder format
    if folder[-1] != '/':
        folder = folder+'/'

    # Get last line from each log file of the simulations
    data = []
    for file in os.listdir(os.fsencode(folder)):
        filename = os.fsdecode(file)
        if filename.endswith(".log"): 
            nb = int(filename[filename.find('NB')+2:filename.find('NFU')-1])
            data.append(np.concatenate(([nb], read_last(folder+filename))))

    # Organice data in a pandas format
    data = pd.DataFrame(data, columns=['NB', 'Sweeps', 'Time', 'Energy', 'Energy_error', 'Entropy', 'Entropy_error'])
    data = data.astype({'NB': int, 'Sweeps': int})
    data = data.sort_values(by=['NB'], ignore_index=True)

    # Calculate boson chemical potential
    old_nb = data['NB'][0]
    mu = []
    for ii in range(0, len(data['NB'])):
        nb = data['NB'][ii]
        if data['NB'][ii] == old_nb+1:
            mu.append(data['Energy'][ii]-data['Energy'][ii-1])
        else:
            mu.append(np.NaN)
        old_nb = data['NB'][ii]
    data.insert(4, 'Mu_B', mu, True)

    # Save data to folder
    filename = os.path.basename(os.path.normpath(folder))+'.txt'
    data.to_csv(folder+filename, index=False)


if __name__ == '__main__':

    # Analyse data from each requested folder
    for ii in range(1, len(sys.argv)):
        print('Processing '+sys.argv[ii], end=' ... ')
        postproccesing_NB(sys.argv[ii])
        print('Done')
