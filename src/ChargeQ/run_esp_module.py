import numpy as np
from pyscf import gto, scf, mp
from pyscf.data.nist import BOHR
from pyscf.data import radii
from pyscf.lib import logger
import sys

# Conversion factor: 1 Angstrom = 1/BOHR Bohr
ang2bohr = 1.0 / BOHR

def read_xyz(filename):
    """
    Read an xyz file and return a list of atoms.
    Each atom is represented as [symbol, np.array([x,y,z])],
    with coordinates converted from Angstrom to Bohr.
    """
    atoms = []
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        sys.exit("Error reading file {}: {}".format(filename, e))

    try:
        natoms = int(lines[0])
    except Exception as e:
        sys.exit("Error reading the number of atoms from {}: {}".format(filename, e))
    # Skip the comment line (line 2) and process the following natoms lines.
    for line in lines[2:2+natoms]:
        parts = line.split()
        if len(parts) < 4:
            continue
        symbol = parts[0]
        # Convert coordinates from Angstrom to Bohr
        coords = np.array([float(x) for x in parts[1:4]]) * ang2bohr
        atoms.append([symbol, coords])
    return atoms

def get_esp_radii(probe):
    ''' Obtain Solvent Inaccessible Radii '''
    ESP_RADII = ang2bohr * np.array(
        [0, # Ghost atom
         0.30,                                     1.22, # 1s
         1.23, 0.89, 0.88, 0.77, 0.70, 0.66, 0.58, 1.60, # 2s2p
         1.40, 1.36, 1.25, 1.17, 1.10, 1.04, 0.99, 1.91, # 3s3p
         2.03, 1.74,                                     # 4s (K, Ca)
         1.44, 1.32, 1.22, 1.19, 1.17, 1.17, 1.16, 1.15, 1.17, 1.25, # 3d (Sc,.., Zn)
         1.25, 1.22, 1.21, 1.17, 1.14, 1.98, # 4p (Ga, .., Kr)
         2.22, 1.92,                                     # 5s (Rb, Sr)
         1.62, 1.45, 1.34, 1.29, 1.27, 1.24, 1.25, 1.28, 1.34, 1.41, # 4d (Y,..,Cd)
         1.50, 1.40, 1.41, 1.37, 1.33, 2.09, # 5p (In,.., Xe)
         2.35, 1.98])                                     # 6s

    prob_radius = probe * ang2bohr
    ESP_RADII += prob_radius
    return ESP_RADII

def esp_grid(mol, rcut=3.0, space=0.5, probe=0.7):
    ''' Generate grid points '''
    ESP_RADII = get_esp_radii(probe)
    qm_xyz = mol.atom_coords()
    qm_znum = mol.atom_charges()
    natom = qm_znum.shape[0]

    grid_min = np.array([min(qm_xyz[:, 0]), min(qm_xyz[:, 1]), min(qm_xyz[:, 2])])
    grid_max = np.array([max(qm_xyz[:, 0]), max(qm_xyz[:, 1]), max(qm_xyz[:, 2])])

    _rcut = rcut * ang2bohr
    _rcut2 = _rcut * _rcut
    _spac = space * ang2bohr

    ngrid_x = int((grid_max[0] - grid_min[0] + 2.0 * _rcut) / _spac) + 1
    ngrid_y = int((grid_max[1] - grid_min[1] + 2.0 * _rcut) / _spac) + 1
    ngrid_z = int((grid_max[2] - grid_min[2] + 2.0 * _rcut) / _spac) + 1

    small = 1.0e-8
    grids = []

    for iz in range(ngrid_z):
        for iy in range(ngrid_y):
            for ix in range(ngrid_x):
                gv = grid_min - _rcut + _spac * np.array([ix, iy, iz])
                rmin2 = _rcut2
                lupdate = True
                for ia in range(natom):
                    znum = qm_znum[ia]
                    rad = ESP_RADII[znum]
                    rad2 = rad * rad
                    dr = gv - qm_xyz[ia]
                    r2 = np.einsum('i,i', dr, dr)
                    if rad2 - r2 > small:
                        lupdate = False
                        break
                    if rmin2 - r2 > small:
                        rmin2 = r2
                if lupdate and (_rcut2 - rmin2 > small):
                    grids.append(list(gv))
    return np.array(grids)

def esp_esp(mol, dm, grids):
    ''' Estimate the electrostatic potential at each grid point '''
    qm_xyz = mol.atom_coords()
    qm_charges = mol.atom_charges()
    drg = qm_xyz[:, None, :] - grids  # (Natom, Ngrid, 3)
    dr = np.linalg.norm(drg, axis=2)   # (Natom, Ngrid)
    z_val = np.einsum('ig, i->g', 1.0 / dr, qm_charges)
    g_val = []
    for gv in grids:
        with mol.with_rinv_origin(gv):
            v = mol.intor('int1e_rinv')
        gval = -np.einsum('ij,ij', dm, v)
        g_val.append(gval)
    return np.array(g_val) + z_val

def esp_fit(mol, grids, grids_val,
            restraint, hfree, resp_a, resp_b, maxiter, tolerance, verbose):
    ''' Fitting procedure for (R)ESP atomic charges '''
    qm_xyz = mol.atom_coords()
    qm_znum = mol.atom_charges()
    natoms = qm_xyz.shape[0]
    ndim = natoms + 1
    am = np.zeros((ndim, ndim))
    drg = qm_xyz[:, None, :] - grids    # (Natom, Ngrid, 3)
    dr = np.linalg.norm(drg, axis=2)      # (Natom, Ngrid)
    am[:natoms, :natoms] = np.einsum('ig, jg->ij', 1.0 / dr, 1.0 / dr)
    am[:natoms, natoms] = 1.0
    am[natoms, :natoms] = 1.0

    bv = np.zeros((ndim))
    bv[:natoms] = np.einsum('ig, g->i', 1.0 / dr, grids_val)
    bv[natoms] = mol.charge

    am_inv = np.linalg.inv(am)
    qf = np.einsum('ij,j->i', am_inv, bv)

    if restraint:
        qf_keep = np.copy(qf)
        am_keep = np.copy(am)
        niter = 0
        while niter < maxiter:
            niter += 1
            am = np.copy(am_keep)
            for ia in range(natoms):
                if (not hfree) or qm_znum[ia] != 1:
                    am[ia, ia] = am_keep[ia, ia] + resp_a / np.sqrt(qf[ia]**2 + resp_b**2)
            am_inv = np.linalg.inv(am)
            difm = 0.0
            for ia in range(natoms):
                vsum = 0.0
                for jb in range(ndim):
                    vsum += am_inv[ia, jb] * bv[jb]
                qf[ia] = vsum
                dif = (vsum - qf_keep[ia])**2
                if difm < dif:
                    difm = dif
            difm = np.sqrt(difm)
            qf_keep = np.copy(qf)
            if difm < tolerance:
                break
    return qf[:natoms]

def esp_atomic_charges(mol, dm, options_dict={}, verbose=0):
    ''' Estimate (R)ESP atomic charges '''
    options = {
        "RCUT": 3.0,       # Angstrom
        "SPACE": 0.5,      # Angstrom
        "PROBE": 0.7,      # Angstrom
        "RESTRAINT": True,
        "RESP_HFREE": True,
        "RESP_A": 0.001,   # au
        "RESP_B": 0.1,     # au
        "RESP_MAXITER": 25,
        "RESP_TOLERANCE": 1.0e-4, # e
    }
    for key in options_dict.keys():
        key_upper = key.upper()
        if key_upper in options:
            options[key_upper] = options_dict[key]

    grids = esp_grid(mol,
                     options['RCUT'],
                     options['SPACE'],
                     options['PROBE'])
    grids_val = esp_esp(mol, dm, grids)
    return esp_fit(mol, grids, grids_val,
                   options['RESTRAINT'],
                   options['RESP_HFREE'],
                   options['RESP_A'],
                   options['RESP_B'],
                   options['RESP_MAXITER'],
                   options['RESP_TOLERANCE'],
                   verbose)

def make_rdm1_with_orbital_response(mp_inst):
    """
    Build the MP2 one-particle density matrix including orbital response.
    """
    from pyscf import lib
    from pyscf.grad.mp2 import _response_dm1, _index_frozen_active, _shell_prange
    from pyscf.mp import mp2
    from pyscf.ao2mo import _ao2mo
    from functools import reduce

    log = lib.logger.new_logger(mp_inst)
    mol = mp_inst.mol
    d1 = mp2._gamma1_intermediates(mp_inst, mp_inst.t2)
    doo, dvv = d1

    with_frozen = not (mp_inst.frozen is None or mp_inst.frozen == 0)
    OA, VA, OF, VF = _index_frozen_active(mp_inst.get_frozen_mask(), mp_inst.mo_occ)
    orbo = mp_inst.mo_coeff[:, OA]
    orbv = mp_inst.mo_coeff[:, VA]
    nao, nocc = orbo.shape
    nvir = orbv.shape[1]

    part_dm2 = _ao2mo.nr_e2(mp_inst.t2.reshape(nocc**2, nvir**2),
                            np.asarray(orbv.T, order='F'), (0, nao, 0, nao),
                            's1', 's1').reshape(nocc, nocc, nao, nao)
    part_dm2 = (part_dm2.transpose(0, 2, 3, 1) * 4 -
                part_dm2.transpose(0, 3, 2, 1) * 2)

    offsetdic = mol.offset_nr_by_atom()
    diagidx = np.arange(nao)
    diagidx = diagidx * (diagidx+1) // 2 + diagidx
    Imat = np.zeros((nao, nao))

    max_memory = max(0, mp_inst.max_memory - lib.current_memory()[0])
    blksize = max(1, int(max_memory * .9e6 / 8 / (nao**3 * 2.5)))

    for ia in range(mol.natm):
        shl0, shl1, p0, p1 = offsetdic[ia]
        ip1 = p0
        for b0, b1, nf in _shell_prange(mol, shl0, shl1, blksize):
            ip0, ip1 = ip1, ip1 + nf
            dm2buf = lib.einsum('pi,iqrj->pqrj', orbo[ip0:ip1], part_dm2)
            dm2buf += lib.einsum('qi,iprj->pqrj', orbo, part_dm2[:, ip0:ip1])
            dm2buf = lib.einsum('pqrj,sj->pqrs', dm2buf, orbo)
            dm2buf = dm2buf + dm2buf.transpose(0, 1, 3, 2)
            dm2buf = lib.pack_tril(dm2buf.reshape(-1, nao, nao)).reshape(nf, nao, -1)
            dm2buf[:, :, diagidx] *= .5

            shls_slice = (b0, b1, 0, mol.nbas, 0, mol.nbas, 0, mol.nbas)
            eri0 = mol.intor('int2e', aosym='s2kl', shls_slice=shls_slice)
            Imat += lib.einsum('ipx,iqx->pq', eri0.reshape(nf, nao, -1), dm2buf)
    from functools import reduce
    mo_coeff = mp_inst.mo_coeff
    mo_energy = mp_inst._scf.mo_energy
    nao, nmo = mo_coeff.shape
    nocc = np.count_nonzero(mp_inst.mo_occ > 0)
    Imat = reduce(np.dot, (mo_coeff.T, Imat, mp_inst._scf.get_ovlp(), mo_coeff)) * -1

    dm1mo = np.zeros((nmo, nmo))
    if with_frozen:
        dco = Imat[OF[:, None], OA] / (mo_energy[OF, None] - mo_energy[OA])
        dfv = Imat[VF[:, None], VA] / (mo_energy[VF, None] - mo_energy[VA])
        dm1mo[OA[:, None], OA] = doo + doo.T
        dm1mo[OF[:, None], OA] = dco
        dm1mo[OA[:, None], OF] = dco.T
        dm1mo[VA[:, None], VA] = dvv + dvv.T
        dm1mo[VF[:, None], VA] = dfv
        dm1mo[VA[:, None], VF] = dfv.T
    else:
        dm1mo[:nocc, :nocc] = doo + doo.T
        dm1mo[nocc:, nocc:] = dvv + dvv.T

    dm1 = reduce(np.dot, (mo_coeff, dm1mo, mo_coeff.T))
    vhf = mp_inst._scf.get_veff(mp_inst.mol, dm1) * 2
    Xvo = reduce(np.dot, (mo_coeff[:, nocc:].T, vhf, mo_coeff[:, :nocc]))
    Xvo += Imat[:nocc, nocc:].T - Imat[nocc:, :nocc]
    dm1mo += _response_dm1(mp_inst, Xvo)
    dm1 = reduce(np.dot, (mo_coeff, dm1mo, mo_coeff.T))
    dm1 += mp_inst._scf.make_rdm1(mp_inst.mo_coeff, mp_inst.mo_occ)
    return dm1

def apply_solvent_effect(mf, solvent_options):
    """
    Wrap the SCF object with ddCOSMO to include solvent effects.
    The solvent name provided in solvent_options (e.g., "water") is mapped to a dielectric constant.
    """
    from pyscf import solvent
    mf = solvent.ddCOSMO(mf)  # Apply ddCOSMO
    # Map solvent names to dielectric constants
    solvent_dict = {
        "water": 78.39,
        "methanol": 32.63,
        "acetonitrile": 35.69,
        "chloroform": 4.81,
    }
    if "solvent" in solvent_options:
        sol_name = solvent_options["solvent"].lower()
        if sol_name in solvent_dict:
            mf.with_solvent.eps = solvent_dict[sol_name]
        else:
            raise ValueError("Unknown solvent: {}".format(solvent_options["solvent"]))
    if "conv" in solvent_options:
        mf.with_solvent.conv = solvent_options["conv"]
    mf.with_solvent.build()
    return mf

def run_esp_charges(xyz_filename, esp_options=None, basis="aug-cc-pvdz",
                    calc_methods=("RHF"), charge=0, solvent_options=None):
    """
    Run the ESP charge calculation using the geometry in xyz_filename.
    Builds the molecule with the specified basis set and molecular charge,
    performs the requested calculations, and saves the results to files.
    
    Optional:
      solvent_options : dict
          If provided, the calculation will be run with a ddCOSMO solvent model.
          For example: {"solvent": "water", "conv": 1e-6}
    """
    if esp_options is None:
        esp_options = {
            "probe": 0.7,
            "restraint": True,
            "resp_hfree": True,
            "resp_a": 0.001,
            "resp_b": 0.1,
            "resp_maxiter": 25,
            "resp_tolerance": 1.0e-4,
        }
    qm_atm_list = read_xyz(xyz_filename)
    atom_symbols = [atom[0] for atom in qm_atm_list]

    mol = gto.Mole()
    mol.basis = basis
    mol.atom = qm_atm_list
    mol.charge = charge
    mol.unit = 'Bohr'
    mol.build()

    # RHF calculation with optional solvent effect
    if "RHF" in calc_methods:
        mf = scf.RHF(mol)
        mf.chkfile = None
        mf = mf.run(verbose=0)
        if solvent_options is not None:
            mf = apply_solvent_effect(mf, solvent_options)
            mf.kernel(verbose=0)
        dm_rhf = mf.make_rdm1()
        with open("esp_charges_RHF.txt", "w") as f:
            f.write("RHF ESP Charges (Charge = {}):\n".format(charge))
            for symbol, charge_val in zip(atom_symbols, esp_atomic_charges(mol, dm_rhf, esp_options, verbose=0)):
                f.write("{:s} {:.8f}\n".format(symbol, charge_val))

    # MP2 calculation with optional solvent effect
    if "MP2" in calc_methods:
        mf = scf.RHF(mol)
        mf.chkfile = None
        mf = mf.run(verbose=0)
        if solvent_options is not None:
            mf = apply_solvent_effect(mf, solvent_options)
            mf.kernel(verbose=0)
        mp2_inst = mp.MP2(mf, frozen=1).run(verbose=0)
        dm_mp2 = make_rdm1_with_orbital_response(mp2_inst)
        with open("esp_charges_MP2.txt", "w") as f:
            f.write("MP2 ESP Charges (Charge = {}):\n".format(charge))
            for symbol, charge_val in zip(atom_symbols, esp_atomic_charges(mol, dm_mp2, esp_options, verbose=0)):
                f.write("{:s}: {:.8f}\n".format(symbol, charge_val))
    
    # DFT calculation with optional solvent effect
    if "DFT" in calc_methods:
        from pyscf import dft
        mf = dft.RKS(mol)
        mf.xc = "b3lyp"  # Change the functional as needed
        mf.chkfile = None
        mf = mf.run(verbose=0)
        if solvent_options is not None:
            mf = apply_solvent_effect(mf, solvent_options)
            mf.kernel(verbose=0)
        dm_dft = mf.make_rdm1()
        with open("esp_charges_DFT.txt", "w") as f:
            f.write("DFT ESP Charges (Charge = {}):\n".format(charge))
            for symbol, charge_val in zip(atom_symbols, esp_atomic_charges(mol, dm_dft, esp_options, verbose=0)):
                f.write("{:s}: {:.8f}\n".format(symbol, charge_val))
