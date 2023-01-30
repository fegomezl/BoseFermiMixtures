import requests
import yaml

# Create name for given parameters and mode:
#   None: Filename for simulation
#   NB: Foldername for NB iteration
#   L: Foldername for L iteration of NB iterations
def create_name(parameters, mode=None):

    # Create start of foldername
    if mode == 'NB':
        name = 'BFModel_L{}_NB_RHOFU{:.2f}_RHOFD{:.2f}'.format(parameters['L'],
                                                               parameters['RHO_FU'],
                                                               parameters['RHO_FD'])
    elif mode == 'L':
        name = 'BFModel_L_RHOB{:.2f}_RHOFU{:.2f}_RHOFD{:.2f}'.format(parameters['RHO_B'],
                                                                     parameters['RHO_FD'],
                                                                     parameters['RHO_FD'])
    else:
        name = 'BFModel_L{}_NB{}_NFU{}_NFD{}'.format(parameters['L'],
                                                     parameters['N_B'],
                                                     parameters['N_FU'],
                                                     parameters['N_FD'])
    
    # Add interactions
    interactions =[['_UBB',parameters['U_BB']],
                   ['_UFF',parameters['U_FF']],
                   ['_UBF',parameters['U_BF']],
                   ['_VBB',parameters['V_BB']],
                   ['_VFF',parameters['V_FF']],
                   ['_VBF',parameters['V_BF']]]
    for ii in range(0, len(interactions)):
        if interactions[ii][1] != 0.:
            name += interactions[ii][0]+'{0:.1f}'.format(interactions[ii][1])

    return name

# Set parameters to the correct format
def read_settings(parameters, foldername, index=0):

    # Configure bond dimension list
    chi_list = {0: parameters['chi_init']}
    for ii in range(1, parameters['max_sweeps']//parameters['chi_step']+1):
        chi_list[ii*parameters['chi_step']] = parameters['chi_init'] + ii*parameters['chi_increase']

    # Configure correct format
    sim_parameters = {
        'simulation_class': 'GroundStateSearch',

        'model_class': 'BoseFermiHubbard',
        'model_params': {
            'bc_MPS': 'finite',
            'N_B_max': parameters['N_B_max'],

            'L': parameters['L'],
            
            't_B': parameters['t_B'],
            't_F': parameters['t_F'],
            'U_BB': parameters['U_BB'],
            'U_FF': parameters['U_FF'],
            'U_BF': parameters['U_BF'],
            'V_BB': parameters['V_BB'],
            'V_FF': parameters['V_FF'],
            'V_BF': parameters['V_BF'],
        },

        'initial_state_builder_class': 'BoseFermiState',
        'initial_state_params': {
            'method': 'filling',
            'N_B': parameters['N_B'],
            'N_FU': parameters['N_FU'],
            'N_FD': parameters['N_FD'],
        },
        
        'algorithm_class': 'TwoSiteDMRGEngine',
        'algorithm_params': {
            'min_sweeps': parameters['min_sweeps'],
            'max_sweeps': parameters['max_sweeps'],
            'max_E_err': parameters['max_E_err'],
            'max_S_err': parameters['max_S_err'],
            'chi_list': chi_list,
            'mixer': True,
        },

        'save_psi': parameters['save_psi'],
        'save_resume_data': False,
        'save_stats': True,
        'measure_initial': False,
        'use_default_measurements': False,
        'overwrite_output': True,

        'log_params': {
            'to_stdout': 'INFO',
            'to_file': 'INFO',
        },
    }

    # Add filename, foldername and index
    sim_parameters['filename'] = create_name(parameters)
    sim_parameters['foldername'] = foldername
    sim_parameters['index'] = index

    return sim_parameters

# Send message with telegram bot
def send_to_telegram(message, config_file):

    # Get token and chat ID from config file
    try:
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
    except:
        print('No telegram config file.')
        return None

    apiToken = config['token']
    chatID = config['ID']
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'

    # Send message to chat
    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
    except Exception as e:
        print(e)
