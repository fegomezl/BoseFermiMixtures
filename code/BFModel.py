import os
import numpy as np
import pandas as pd

from tenpy import run_simulation
from tenpy.linalg import np_conserved as npc
from tenpy.networks import site
from tenpy.networks.site import Site
from tenpy.networks.mps import InitialStateBuilder
from tenpy.models.lattice import Lattice
from tenpy.models.model import CouplingMPOModel

''' Bosons and spin 1/2 fermions site '''
class BoseFermiSite(Site):

    """
    Local states: |b fu fd> 
      b  : Boson number
      fu : Up fermions number
      fd : Down fermions number

    Local operators:
        Symbol | Name                          | Formula
        -----------------------------------------------------
        B      | Boson annihilation            | B
        Bt     | Boson creation                | Bt
        Nb     | Boson number                  | Bt*B
        NbNb   | Boson local interaction       | Nb*Nb
        ----------------------------------------------------
        Cu     | Up fermion annihilation       | Cu
        Cut    | Up fermion creation           | Cut
        Cd     | Down fermion annihilation     | Cd
        Cdt    | Down fermion creation         | Cdt
        Nfu    | Up fermion number             | Cut*Cu
        Nfd    | Down fermion number           | Cdt*Cd
        Nf     | Fermion number                | Nfu+Nfd
        NfuNfd | Fermion local interaction     | Nfu*Nfd
        JWu    | Up fermion anti-conmutation   | (-1)^Nfu
        JWd    | Down fermion anti-conmutation | (-1)^Nfd
        JW     | Fermion anti-conmutation      | JWu*JWd
        ----------------------------------------------------
        NbNf   | Interacción local bosón-fermión | Nb*Nf
    """
  
    def __init__(self, N_B_max=1):      # N_B_max: Maximum number of bosons per site

        # Dimension
        dim = 4*(N_B_max+1)

        # Local states
        states = []
        for ii in range(0, N_B_max+1):
            states.extend([str(ii)+'00',str(ii)+'01',str(ii)+'10',str(ii)+'11'])

        # Diagonal local matrices
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
            NbNb_diag.append(b*b)

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

        # Non-diagonal local matrices
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

        # Set of operators
        ops = dict(B=B, Bt=Bt,
                   Nb=Nb, NbNb=NbNb, 
                   Cu=Cu, Cut=Cut, Cd=Cd, Cdt=Cdt,
                   Nfu=Nfu, Nfd=Nfd, Nf=Nf, NfuNfd=NfuNfd,
                   JWu=JWu, JWd=JWd, JW=JW,
                   NbNf=NbNf)

        # Abelian charges 
        qnames = []         #Charge name
        qmod = []           #Charge group ((n=1)->Z, (n>1)->Z_n)
        charges = []        #Charge definition for local states

        #Boson number
        qnames.append('Nb')
        qmod.append(1)
        charges.append(Nb_diag)

        #Up fermion number
        qnames.append('Nfu')
        qmod.append(1)
        charges.append(Nfu_diag)

        #Down fermion number
        qnames.append('Nfd') 
        qmod.append(1)
        charges.append(Nfd_diag) 

        # Merge charges and define corresponding unsorted leg
        if len(charges) > 1:
            new_charges = charges[0]
            for ii in range(1, len(charges)):
                new_charges = np.vstack((new_charges, charges[ii]))
            charges = new_charges.T.tolist()
        else:
            charges = charges[0]
        chinfo = npc.ChargeInfo(qmod, qnames)
        leg_unsorted = npc.LegCharge.from_qflat(chinfo, charges)

        # Perform permutation of charges 
        perm_qind, leg = leg_unsorted.sort()
        perm_flat = leg_unsorted.perm_flat_from_perm_qind(perm_qind)
        self.perm = perm_flat

        # Reorganice local states and operators according to the permutation
        states = [states[i] for i in perm_flat]
        for opname in ops:
            ops[opname] = ops[opname][np.ix_(perm_flat, perm_flat)]

        # Create site
        Site.__init__(self, leg, states, **ops)

        # Define which operators need the anti-conmutation operator
        self.need_JW_string |= set(['Cu', 'Cut', 'Cd', 'Cdt', 'JWu', 'JWd', 'JW'])

''' Initial state constructor '''
class BoseFermiState(InitialStateBuilder):

    """
    Create a product state for a given number of bosons and up/down fermions
    with the particles distributed along the chain
    """

    def filling(self):
        # Inital state parameters
        L = self.lattice.Ls[0]
        N_FU = self.options.get('N_FU', L//2)
        N_FD = self.options.get('N_FD', L//2)
        N_B = self.options.get('N_B', L//2)
        
        # Create separate chains with the target fillings
        fermions_up = ['0']*L
        for ii in range (0, N_FU):
          fermions_up[(ii)*(L//N_FU)] = '1'
        
        fermions_down = ['0']*L
        for ii in range (0, N_FD):
          fermions_down[(ii)*(L//N_FD)] = '1'
        
        bosons = ['0']*L
        for ii in range (0, N_B):
          bosons[(ii)*(L//N_B)] = '1'
        
        # Merge chains to create final MPS
        product_state = [[b+fu+fd] for b,fu,fd in zip(bosons, fermions_up, fermions_down)]
        return self.lat_product_state(product_state)

''' Hamiltonian '''
class BoseFermiHubbard(CouplingMPOModel):
    
    """
    Hubbard model for bosons and spin 1/2 fermions mixture

    H = H_{B} + H_{F} + H_{BF}

    H_{B}  = - t_{B} \sum_{\langle i, j \rangle} (b_{i}^{\dagger} b_{j} + h.c) 
             + U_{BB} \sum_{i} n^{B}_{i} (n^{B}_{i} - 1) 
             + V_{BB} \sum_{\langle i, j \rangle} n^{B}_{i} n^{B}_{j}
           
    H_{F}  = - t_{F} \sum_{\langle i, j \rangle, \sigma} (c^{\dagger}_{i, \sigma} c_{j, \sigma} + h.c) 
             + U_{FF} \sum_{i} n^{F}_{i, \ uparrow} n^{F}_{i, \ downarrow}
             + V_{FF} \sum_{\langle i, j \rangle} n^{F}_{i} n^{F}_{j}

    H_{BF} = + U_{BF}\sum_{i} n^{B}_{i} n^{F}_{i} 
             + V_{BF}\sum_{\langle i, j \rangle} n^{B}_{i} n^{F}_{j}
    """

    # Define geometry and local hilbert space
    def init_lattice(self, model_params):

        # Lattice parameters
        L = model_params.get('L', 2)                # Lenght of chain
        N_B_max = model_params.get('N_B_max', 1)    # Maximum number of bosons per site

        return Lattice([L], unit_cell=[BoseFermiSite(N_B_max)])

    # Define hamiltonian
    def init_terms(self, model_params):

        # Interaction parameters
        t_B = model_params.get('t_B', 1.)
        t_F = model_params.get('t_F', 1.)
        U_BB = model_params.get('U_BB', 0.) 
        U_FF = model_params.get('U_FF', 0.) 
        U_BF = model_params.get('U_BF', 1.)
        V_BB = model_params.get('V_BB', 0.)
        V_FF = model_params.get('V_FF', 0.)
        V_BF = model_params.get('V_BF', 0.)

        # Interaction terms

        # Hopping
        self.add_coupling(-t_B, 0, 'Bt',  0, 'B',  [1], plus_hc=True)
        self.add_coupling(-t_F, 0, 'Cut', 0, 'Cu', [1], plus_hc=True)
        self.add_coupling(-t_F, 0, 'Cdt', 0, 'Cd', [1], plus_hc=True)

        # Local interactions
        self.add_onsite(U_BB, 0, 'NbNb')
        self.add_onsite(-U_BB, 0, 'Nb')
        self.add_onsite(U_FF, 0, 'NfuNfd')
        self.add_onsite(U_BF, 0, 'NbNf')

        # Next-neighbor interactions
        self.add_coupling(V_BB, 0, 'Nb', 0, 'Nb', [1])
        self.add_coupling(V_FF, 0, 'Nf', 0, 'Nf', [1])
        self.add_coupling(V_BF, 0, 'Nb', 0, 'Nf', [1])

# Run Bose-Fermi simulation with given parameters
def run(sim_parameters):

    # Get filename and foldername
    filename = sim_parameters['filename']
    foldername = sim_parameters['foldername']+'/'
    index = sim_parameters['index']
    sim_parameters.pop('filename', None)
    sim_parameters.pop('foldername', None)
    sim_parameters.pop('index', None)

    # Run simulation with given parameters
    sim_parameters['log_params']['filename'] = foldername+filename+'.aux'
    results = run_simulation(**sim_parameters)

    # Save sweep statistics in one file
    N = results['sweep_stats']['sweep']
    t = results['sweep_stats']['time']
    E = results['sweep_stats']['E']
    S = results['sweep_stats']['S']
    dE = [np.NaN]
    dS = [S[0]]
    for ii in range(1, N[-1]):
        dE.append(-(E[ii]-E[ii-1])/max(np.abs(E[ii]), 1))
        dS.append(np.abs(S[ii]-S[ii-1]))
    out = pd.DataFrame(np.array([N, t, E, dE, S, dS]).T, 
                       columns=['Sweep', 'Time', 'Energy', 'Energy_error', 'Entropy', 'Entropy_error'])
    out = out.astype({'Sweep': int})
    out.to_csv(foldername+filename+'.log', index=False)

    f1 = open(foldername+filename+'.log', 'a+')
    f2 = open(foldername+filename+'.aux', 'r')

    f1.write('\n\n')
    f1.write(f2.read())

    f1.close()
    f2.close()

    os.remove(foldername+filename+'.aux')

    # Save expected values
    if sim_parameters['save_psi'] == True:
        Nb = results['psi'].expectation_value(['Nb'])
        Nf = results['psi'].expectation_value(['Nf'])
        Nfu = results['psi'].expectation_value(['Nfu'])
        Nfd = results['psi'].expectation_value(['Nfd'])
        NfuNfd = results['psi'].expectation_value(['NfuNfd'])
        ex_val = pd.DataFrame(np.array([range(len(Nb)),Nb, Nf, Nfu, Nfd, NfuNfd]).T, columns=['Site', 'Nb', 'Nf', 'Nfu', 'Nfd', 'NfuNfd'])
        ex_val = ex_val.astype({'Site': int})
        ex_val.to_csv(foldername+filename+'.out', index=False)

    return index
