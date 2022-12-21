import sys
import numpy as np
import h5py

import tenpy
from tenpy.tools import hdf5_io
from tenpy.linalg import np_conserved as npc
from tenpy.networks.site import Site
from tenpy.networks.mps import InitialStateBuilder
from tenpy.models.model import CouplingMPOModel

class BosonFermiSite(Site):
  
    """
    Local states: |b fu fd> 
      b : Boson number
      fu : Fermion up number
      fd : Fermion down number

    Operators:
      Boson:
        B    : Boson annihilation      : B
        Bt   : Boson creation          : Bt
        Nb   : Boson number            : Bt*B
        NbNb : Local boson interaction : Nb*(Nb-1)
      Fermion:
        Cu     : Fermion up annihilation   : Cu
        Cut    : Fermion up creation       : Cut
        Cd     : Fermion down annihilation : Cd
        Cdt    : Fermion down creation     : Cdt
        Nfu    : Fermion up number         : Cut*Cu
        Nfd    : Fermion down number       : Cdt*Cd
        Nf     : Fermion number            : Nfu+Nfd
        NfuNfd : Local fermion interaction : Nfu*Nfd
        JWu    : Jordan-Wigner string up   : (-1)^Nfu
        JWd    : Jordan-Wigner string down : (-1)^Nfd
        JW     : Jordan-Wigner string      : JWu*JWd
      Boson-Fermion:
        NbNf : Local boson-fermion interaction : Nb*Nf
    """

    def __init__(self, N_B_max=1):

        #Dimension
        dim = 4*(N_B_max+1)

        #Local states
        states = []
        for ii in range(0, N_B_max+1):
            states.extend([str(ii)+'00',str(ii)+'01',str(ii)+'10',str(ii)+'11'])

        #Diagonal matrices
        Nb_diag  = []
        NbNb_diag = []

        Nfu_diag = []
        Nfd_diag = []
        Nf_diag = []
        NfuNfd_diag = []
        JWu_diag = []
        JWd_diag = []
        JW_diag = []

        NbNf_diag = []

        for ii in range(0, dim):
            b = ii//4
            fu = (ii//2)%2
            fd = ii%2

            Nb_diag.append(b)
            NbNb_diag.append(b*(b-1))

            Nfu_diag.append(fu)
            Nfd_diag.append(fd)
            Nf_diag.append(fu+fd)
            NfuNfd_diag.append(fu*fd)
            JWu_diag.append(1-2*fu)
            JWd_diag.append(1-2*fd)
            JW_diag.append((1-2*fu)*(1-2*fd))

            NbNf_diag.append(b*(fu+fd))

        Nb = np.diag(Nb_diag).astype(float)
        NbNb = np.diag(NbNb_diag).astype(float)

        Nfu = np.diag(Nfu_diag).astype(float)
        Nfd = np.diag(Nfd_diag).astype(float)
        Nf = np.diag(Nf_diag).astype(float)
        NfuNfd = np.diag(NfuNfd_diag).astype(float)
        JWu = np.diag(JWu_diag).astype(float)
        JWd = np.diag(JWd_diag).astype(float)
        JW = np.diag(JW_diag).astype(float)

        NbNf = np.diag(NbNf_diag).astype(float)

        #Non-diagonal matrices
        B  = np.zeros((dim, dim), dtype=float)
        Cu = np.zeros((dim, dim), dtype=float)
        Cd_noJW = np.zeros((dim, dim), dtype=float)

        for ii in range(0, dim-4):
          B[ii, ii+4] = np.sqrt(1+ii//4)

        for ii in range(0, dim-2):
          Cu[ii, ii+2] = (1+ii//2)%2

        for ii in range(0, dim-1):
          Cd_noJW[ii, ii+1] = (1+ii)%2

        Bt = B.transpose()
        Cut = Cu.transpose()

        Cd = np.dot(JWu, Cd_noJW)
        Cdt = Cd.transpose()

        #Set of operators
        ops = dict(B=B, Bt=Bt,
                   Nb=Nb, NbNb=NbNb, 
                   Cu=Cu, Cut=Cut, Cd=Cd, Cdt=Cdt,
                   Nfu=Nfu, Nfd=Nfd, Nf=Nf, NfuNfd=NfuNfd,
                   JWu=JWu, JWd=JWd, JW=JW,
                   NbNf=NbNf)

        #Charges
        qnames = []
        qmod = []
        charges = []

        qnames.append('Nb')
        qmod.append(1)
        charges.append(Nb_diag)

        qnames.append('Nfu')
        qmod.append(1)
        charges.append(Nfu_diag)

        qnames.append('Nfd') 
        qmod.append(1)
        charges.append(Nfd_diag) 

        charges = [[q1, q2, q3] for q1, q2, q3 in zip(charges[0], charges[1], charges[2])]
        chinfo = npc.ChargeInfo(qmod, qnames)
        leg_unsorted = npc.LegCharge.from_qflat(chinfo, charges)

        perm_qind, leg = leg_unsorted.sort()
        perm_flat = leg_unsorted.perm_flat_from_perm_qind(perm_qind)
        self.perm = perm_flat

        #Reordering
        states = [states[i] for i in perm_flat]
        for opname in ops:
            ops[opname] = ops[opname][np.ix_(perm_flat, perm_flat)]

        Site.__init__(self, leg, states, **ops)
        self.need_JW_string |= set(['Cu', 'Cut', 'Cd', 'Cdt', 'JWu', 'JWd', 'JW'])

class BosonFermiState(InitialStateBuilder):
  def filling(self):
    
    #Parameters
    L = self.lattice.Ls[0]
    N_FU = self.options.get('N_FU', L//2)
    N_FD = self.options.get('N_FD', L//2)
    N_B = self.options.get('N_B', L//2)
    
    #Create separate chains with given filling
    fermions_up = ['0']*L
    for ii in range (0, N_FU):
      fermions_up[(ii)*(L//N_FU)] = '1'
    
    fermions_down = ['0']*L
    for ii in range (0, N_FD):
      fermions_down[(ii)*(L//N_FD)] = '1'
    
    bosons = ['0']*L
    for ii in range (0, N_B):
      bosons[(ii)*(L//N_B)] = '1'
    
    #Merge chains to create initial product state
    product_state = [[b+fu+fd] for b,fu,fd in zip(bosons, fermions_up, fermions_down)]
    return self.lat_product_state(product_state)

class BosonFermiHubbard(CouplingMPOModel):

    #Force a 1D geometry
    default_lattice = "Chain"
    force_default_lattice = True

    #Define local hilbert space
    def init_sites(self, model_params):
        N_B_max = model_params.get('N_B_max', 1)
        return BosonFermiSite(N_B_max)

    #Define hamiltonian
    def init_terms(self, model_params):
        #Interaction parameters
        t_B = model_params.get('t_B', 1.)
        t_F = model_params.get('t_F', 1.)
        U_BB = model_params.get('U_BB', 0.) 
        U_FF = model_params.get('U_FF', 0.) 
        U_BF = model_params.get('U_BF', 1.)
        V_BB = model_params.get('V_BB', 0.)
        V_FF = model_params.get('V_FF', 0.)
        V_BF = model_params.get('V_BF', 0.)

        #Hopping
        self.add_coupling(-t_B, 0, 'Bt',  0, 'B',  [1], plus_hc=True)
        self.add_coupling(-t_F, 0, 'Cut', 0, 'Cu', [1], plus_hc=True)
        self.add_coupling(-t_F, 0, 'Cdt', 0, 'Cd', [1], plus_hc=True)

        #Local interactions
        self.add_onsite(U_BB, 0, 'NbNb')
        self.add_onsite(U_FF, 0, 'NfuNfd')
        self.add_onsite(U_BF, 0, 'NbNf')

        #Next-neighbour interactions
        self.add_coupling(V_BB, 0, 'Nb', 0, 'Nb', [1])
        self.add_coupling(V_FF, 0, 'Nf', 0, 'Nf', [1])
        self.add_coupling(V_BF, 0, 'Nb', 0, 'Nf', [1])

bc = 'finite'
N_B_max = 1

L = 24
N_B = 12
N_FU = 6
N_FD = 6

t_B = 1.
t_F = 1.
U_BB = 0.
U_FF = 4.
U_BF = 6.
V_BB = 0.
V_FF = 0.
V_BF = 0.

sim_params = {
    'simulation_class': 'GroundStateSearch',

    'model_class': 'BosonFermiHubbard',
    'model_params': {
        'bc_MPS': bc,
        'N_B_max': N_B_max,

        'L': L,
        
        't_B': t_B,
        't_F': t_F,
        'U_BB': U_BB,
        'U_FF': U_FF,
        'U_BF': U_BF,
        'V_BB': V_BB,
        'V_FF': V_FF,
        'V_BF': V_BF,
    },

    'initial_state_builder_class': 'BosonFermiState',
    'initial_state_params': {
        'method': 'filling',
        'N_FU': N_FU,
        'N_FD': N_FD,
        'N_B': N_B,
    },

    'algorithm_class': 'TwoSiteDMRGEngine',
    'algorithm_params': {
        'min_sweeps': 1,
        'max_sweeps': 1000,
        'max_hours': 12,
        'max_E_err': 1e-8,
        'max_S_err': 1e-5,

        'trunc_params': {
            'chi_max': 500,
        },
        'chi_list': None,
        
        'mixer': True,
        'mixer_params': {
            'amplitude': 1.e-6,
            'decay': 2.,
            'disable_after': 20,
        }
    },

    'directory': None,
    'output_filename_params': {
            'prefix': 'test',
            'parts': {
                'model_params.L': 'L{0:d}',
                'model_params.U_FF': 'UFF{0:.0f}',
                'model_params.U_BF': 'UBF{0:.0f}',
                'initial_state_params.N_B': 'NB{0:d}',
                'initial_state_params.N_FU': 'NFU{0:d}',
                'initial_state_params.N_FD': 'NFD{0:d}',
                'algorithm_params.trunc_params.chi_max': 'chi{0:d}',
            },
            'suffix': '.h5',
    },
    'save_every_x_seconds': None,
    'save_psi': False,
    'save_stats': True,
    'save_resume_data': False,
    'measure_initial': False,
    'use_default_measurements': False,

    'log_params': {
        'to_stdout': 'INFO',
        'to_file': None,
    },
}

def mean(data):
  n = len(data)
  mean = sum(data) / n
  return mean
 
def variance(data):
  n = len(data)
  mean = sum(data) / n
  deviations = [(x - mean) ** 2 for x in data]
  variance = sum(deviations) / n
  return variance
 
def stdev(data):
  import math
  var = variance(data)
  std_dev = math.sqrt(var)
  return std_dev

nproc = int(sys.argv[1])
N = int(sys.argv[2])

T = []
for n in range(0, N):
    results = tenpy.run_simulation(**sim_params)
    T.append(results['sweep_stats']['time'][-1])

with open("results.txt", "a") as f:
	f.write(str(nproc)+' '+str(mean(T))+' '+str(stdev(T))+'\n')

print('+'*80)
print('nproc:',nproc)
print('N:',N)
print('T:',T)
print('mean(T):',mean(T))
print('std(T):',stdev(T))
