import numpy as np

from tenpy.linalg import np_conserved as npc
from tenpy.networks import site
from tenpy.networks.site import Site
from tenpy.networks.mps import InitialStateBuilder
from tenpy.models.model import CouplingMPOModel

FILENAME_PREFIX = 'ladder'

''' Sitio de fermiones con spin 1/2 '''
class SpinFermiSite(Site):
  
    """
    Estados locales: |fu fd> 
      fu : Número de fermiones up
      fd : Número de fermiones down

    Operadores locales:
        Simbolo | Nombre                          | Expresión
        -----------------------------------------------------
        Cu      | Aniquilación de fermión up      | Cu
        Cut     | Creación de fermión up          | Cut
        Cd      | Aniquilación de fermión down    | Cd
        Cdt     | Creación de fermión down        | Cdt
        Nu      | Número de fermiones up          | Cut*Cu
        Nd      | Número de fermiones down        | Cdt*Cd
        N       | Número de fermiones             | Nu+Nd
        NuNd    | Interacción local de fermiones  | Nu*Nd
        JWu     | Anti-conmutación fermiones up   | (-1)^Nu
        JWd     | Anti-conmutación fermiones down | (-1)^Nd
        JW      | Anti-conmutación fermiones      | JWu*JWd
    """

    def __init__(self):

        #Dimensión
        dim = 4

        #Estados locales
        states = ['00', '01', '10', '11']

        #Creación matrices diagonales
        Nu_diag = []
        Nd_diag = []
        N_diag = []
        NuNd_diag = []
        JWu_diag = []
        JWd_diag = []
        JW_diag = []

        for ii in range(0, dim):
            fu = (ii//2)%2
            fd = ii%2

            Nu_diag.append(fu)
            Nd_diag.append(fd)
            N_diag.append(fu+fd)
            NuNd_diag.append(fu*fd)
            JWu_diag.append(1-2*fu)
            JWd_diag.append(1-2*fd)
            JW_diag.append((1-2*fu)*(1-2*fd))

        Nu = np.diag(Nu_diag).astype(float)
        Nd = np.diag(Nd_diag).astype(float)
        N = np.diag(N_diag).astype(float)
        NuNd = np.diag(NuNd_diag).astype(float)
        JWu = np.diag(JWu_diag).astype(float)
        JWd = np.diag(JWd_diag).astype(float)
        JW = np.diag(JW_diag).astype(float)

        #Creación matrices no diagonales
        Cu = np.zeros((dim, dim), dtype=float)
        Cd_noJW = np.zeros((dim, dim), dtype=float) #Le falta la anti-conmutación

        for ii in range(0, dim-2):
          Cu[ii, ii+2] = (1+ii//2)%2

        for ii in range(0, dim-1):
          Cd_noJW[ii, ii+1] = (1+ii)%2

        Cut = Cu.transpose()

        Cd = np.dot(JWu, Cd_noJW)   #Se agrega la anticonmutación
        Cdt = Cd.transpose()

        #Conjunto de operadores
        ops = dict(Cu=Cu, Cut=Cut, Cd=Cd, Cdt=Cdt,
                   Nu=Nu, Nd=Nd, N=N, NuNd=NuNd,
                   JWu=JWu, JWd=JWd, JW=JW)

        #Definición de cargas
        qnames = []         #Nombre de la carga
        qmod = []           #Grupo de la carga (1->Z, n>1->Z_n)
        charges = []        #Cargas para los estados locales

        #Número de fermiones up
        qnames.append('Nu')
        qmod.append(1)
        charges.append(Nu_diag)

        #Número de fermiones down
        qnames.append('Nd') 
        qmod.append(1)
        charges.append(Nd_diag) 

        #Unión de las cargas y definición de indices correspondientes
        charges = [[q1, q2] for q1, q2 in zip(charges[0], charges[1])]
        chinfo = npc.ChargeInfo(qmod, qnames)
        leg_unsorted = npc.LegCharge.from_qflat(chinfo, charges)

        #Permutación asociada a las cargas
        perm_qind, leg = leg_unsorted.sort()
        perm_flat = leg_unsorted.perm_flat_from_perm_qind(perm_qind)
        self.perm = perm_flat

        #Reorganización de estados y operadores locales
        states = [states[i] for i in perm_flat]
        for opname in ops:
            ops[opname] = ops[opname][np.ix_(perm_flat, perm_flat)]

        #Inicialización de la estructura de sitio
        Site.__init__(self, leg, states, **ops)

        #Se necesita definir que operadores requieren del operador de anti-conmutación
        self.need_JW_string |= set(['Cu', 'Cut', 'Cd', 'Cdt', 'JWu', 'JWd', 'JW'])

''' Constructor del estado inicial '''
class BosonFermiState(InitialStateBuilder):

    """
    El constructor recibe el número de fermiones (up,down) y bosones
    deseados y construye un MPS con las particulas distribuidas
    a lo largo de la cadena. 
    """

    def filling(self):

        #Parametros del estado inicial
        L = self.lattice.Ls[0]
        N_FU = self.options.get('N_FU', L//2)
        N_FD = self.options.get('N_FD', L//2)
        N_B = self.options.get('N_B', L//2)
        
        #Crear cadenas separadas con los llenados deseados
        fermions_up = ['0']*L
        for ii in range (0, N_FU):
          fermions_up[(ii)*(L//N_FU)] = '1'
        
        fermions_down = ['0']*L
        for ii in range (0, N_FD):
          fermions_down[(ii)*(L//N_FD)] = '1'
        
        bosons = ['vac']*L
        for ii in range (0, N_B):
          bosons[(ii)*(L//N_B)] = '1'
        
        #Unir cadenas para crear el MPS
        product_state = [(b,fu+fd) for b,fu,fd in zip(bosons, fermions_up, fermions_down)]
        return self.lat_product_state(product_state)

''' Hamiltoniano '''
class BosonFermiHubbard(CouplingMPOModel):
    
    """
    Modelo de Hubbard para mezclas de bosones y fermiones spin 1/2

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

    #Enforzar una geometria de 'escalera' 
    #Distintos sitios para bosones y fermiones
    default_lattice = "Ladder"
    force_default_lattice = True

    #Definir espacio de Hilbert local
    def init_sites(self, model_params):

        #Sitio de bosones
        N_B_max = model_params.get('N_B_max', 1)        #Máximo número de bosones por sitio
        site_b = site.BosonSite(Nmax = N_B_max)

        #Sitio de fermiones con spin 1/2
        site_f = SpinFermiSite()

        #Concatenación de sitios
        sites = [site_b, site_f]
        site.set_common_charges(sites, new_charges='independent')
        return sites

    #Definir hamiltoniano
    def init_terms(self, model_params):

        #Parametros de interacción
        t_B = model_params.get('t_B', 1.)
        t_F = model_params.get('t_F', 1.)
        U_BB = model_params.get('U_BB', 0.) 
        U_FF = model_params.get('U_FF', 0.) 
        U_BF = model_params.get('U_BF', 1.)
        V_BB = model_params.get('V_BB', 0.)
        V_FF = model_params.get('V_FF', 0.)
        V_BF = model_params.get('V_BF', 0.)

        #Términos de interacción (0->Fermiones, 1->Bosones)

        #Hopping
        self.add_coupling(-t_B, 0, 'Bd',  0, 'B',  [1], plus_hc=True)
        self.add_coupling(-t_F, 1, 'Cut', 1, 'Cu', [1], plus_hc=True)
        self.add_coupling(-t_F, 1, 'Cdt', 1, 'Cd', [1], plus_hc=True)

        #Interacciones locales
        self.add_onsite(U_BB, 0, 'NN')
        self.add_onsite(-U_BB, 0, 'N')
        self.add_onsite(U_FF, 1, 'NuNd')
        self.add_coupling(U_BF, 0, 'N', 1, 'N', [0])

        #Interacciones a primeros vecinos
        self.add_coupling(V_BB, 0, 'N', 0, 'N', [1])
        self.add_coupling(V_FF, 1, 'N', 1, 'N', [1])
        self.add_coupling(V_BF, 0, 'N', 1, 'N', [1])
