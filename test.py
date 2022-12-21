import numpy as np
import tenpy
from tenpy.networks.mps import MPS
from tenpy.models.hubbard import FermiHubbardModel
from tenpy.algorithms.dmrg import TwoSiteDMRGEngine

L = 2

U = 1.

sim_params = {
    'algorithm_class': 'TwoSiteDMRGEngine',
    'algorithm_params': {
        'trunc_params': {
            'chi_max': 100
        },
    },
    'model_class': 'FermiHubbardModel',
    'model_params': {
        'bc_MPS': 'infinite',
        'L': L,
        'U': U
    },
    'initial_state_params': {
        'method': 'lat_product_state',
        'product_state': [['up'], ['down']]
    },
}

tenpy.run_simulation(**sim_params)
