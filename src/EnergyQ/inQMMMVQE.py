import tangelo
import numpy as np

# Tangelo common imports.
from tangelo import SecondQuantizedMolecule
from tangelo.algorithms.variational import VQESolver, BuiltInAnsatze
from tangelo.toolboxes.molecular_computation.frozen_orbitals import get_orbitals_excluding_homo_lumo
from tangelo.toolboxes.molecular_computation.molecule import atom_string_to_list

# QM/MM-related imports.
from tangelo.problem_decomposition.qmmm.qmmm_problem_decomposition import QMMMProblemDecomposition
from tangelo.problem_decomposition.oniom._helpers.helper_classes import Fragment
from scipy.optimize import minimize

import time
from datetime import datetime
import os

# PySCF imports for QM/MM
from pyscf import gto, dft, qmmm
# Placeholder for dispersion correction; replace with your actual module or implementation
from dispersion import get_dispersion

# Start timing the process
start_time = time.time()

# Basis set and constants.
Basis_Set = "minao"
ha_to_kcalmol = 627.509
cal_to_j = 4.184

method = "B3LYP-d4"
basis = "def2-svpd"
aux_basis_set = "def2-universal-jfit"

# Set total charge of free ligand
Charge = 0
CUT_OFF = 8.0
ACTIVE_OCC = 3
ACTIVE_UNOCC = 2
Optimizer = "SLSQP" #CG, BFGS, L-BFGS-B, POWELL, COBYLA
QMapping = "scBK" #jw, bk, parity

#############################################
# Helper Functions
#############################################
def read_ligand_xyz(xyz_file):
    with open(xyz_file, 'r') as f:
        lines = f.readlines()
    molecule_str = ""
    for line in lines[2:]:
        parts = line.split()
        if len(parts) < 4:
            continue
        element = parts[0]
        x, y, z = parts[1:4]
        molecule_str += f"{element} {x} {y} {z}\n"
    return molecule_str

def get_ligand_coordinates(xyz_file):
    coords = []
    with open(xyz_file, 'r') as f:
        lines = f.readlines()
    for line in lines[2:]:
        parts = line.split()
        if len(parts) < 4:
            continue
        coords.append([float(parts[1]), float(parts[2]), float(parts[3])])
    return np.array(coords)

def read_mm_data(topol_file):
    mm_data = []
    reading_atoms = False
    with open(topol_file, 'r') as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith('!'):
                if reading_atoms:
                    break
                else:
                    continue
            if stripped[0].isdigit():
                reading_atoms = True
                cols = stripped.split()
                if len(cols) < 4:
                    continue
                atom_index = int(cols[0])
                charge = float(cols[3])
                mm_data.append((atom_index, charge))
    return mm_data

def read_coords_from_pdb(pdb_file):
    coords_dict = {}
    with open(pdb_file, 'r') as f:
        for line in f:
            if line.startswith("ATOM") or line.startswith("HETATM"):
                try:
                    serial = int(line[6:11])
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    coords_dict[serial] = [x, y, z]
                except ValueError:
                    continue
    return coords_dict

def filter_mm_atoms(ligand_coords, mm_coords, mm_charges, cutoff=10.0):
    filtered_coords = []
    filtered_charges = []
    for i, mm_coord in enumerate(mm_coords):
        distances = np.linalg.norm(ligand_coords - mm_coord, axis=1)
        if np.min(distances) <= cutoff:
            filtered_coords.append(mm_coord)
            filtered_charges.append(mm_charges[i])
    return np.array(filtered_coords), np.array(filtered_charges)

##################################
# File names (adjust as needed)
##################################
ligand_xyz_file = "ligand.xyz"
topol_file = "topology.top"
pdb_file = "complex.pdb"

##################################
# Build the QM (ligand) region
##################################
ligand_xyz_str = read_ligand_xyz(ligand_xyz_file)
ligand_coords = get_ligand_coordinates(ligand_xyz_file)

ligand = SecondQuantizedMolecule(ligand_xyz_str, basis=Basis_Set, q=Charge, spin=0)
frozen_orbitals_lig = get_orbitals_excluding_homo_lumo(
    ligand, homo_minus_n=ACTIVE_OCC-1, lumo_plus_n=ACTIVE_UNOCC-1
)
ligand.freeze_mos(frozen_orbitals_lig, inplace=True)

# Global to store optimizer history
opt_history = []

Optimizer = "SLSQP"  # or "CG", "BFGS", "L-BFGS-B", "Powell", "COBYLA"
#tolerance = 1e-7     # Convergence threshold in Ha

def real_optimizer(func, var_params):
    global opt_history
    opt_history = []
    Tolerance = 1e-7
    max_outer_loops = 20  # to prevent infinite loops
    final_energy, final_params = None, var_params

    for outer in range(max_outer_loops):
        converged = False

        def real_fun(x):
            val = func(x)
            return np.real_if_close(val)

        def record_progress(xk):
            nonlocal converged
            current_energy = real_fun(xk)
            opt_history.append((len(opt_history) + 1, current_energy))
            if len(opt_history) > 1:
                delta_e = abs(opt_history[-1][1] - opt_history[-2][1])
                if delta_e < Tolerance:
                    converged = True
                    raise StopIteration  # stop current SciPy run

        try:
            res = minimize(real_fun, final_params,
                           method=Optimizer,
                           callback=record_progress,
                           options={"maxiter": 1000})
            final_energy = opt_history[-1][1]
            final_params = res.x
        except StopIteration:
            final_energy = opt_history[-1][1]
            final_params = res.x if "res" in locals() else final_params

        # Exit outer loop if converged
        if converged:
            break

    return final_energy, final_params

quantum_solver_lig = VQESolver({
    "molecule": ligand,
    "ansatz": BuiltInAnsatze.UCCSD,
    "qubit_mapping": QMapping,
    "up_then_down": True,
    "optimizer": real_optimizer,  # use our custom optimizer
})
quantum_solver_lig.build()
e_quantum_lig = quantum_solver_lig.simulate()

##################################
# Build the MM (protein) region
##################################
mm_data = read_mm_data(topol_file)
pdb_coords_dict = read_coords_from_pdb(pdb_file)

mm_coords_list = []
mm_charges_list = []
for atom_index, charge in mm_data:
    if atom_index in pdb_coords_dict:
        mm_coords_list.append(pdb_coords_dict[atom_index])
        mm_charges_list.append(charge)
    else:
        print(f"Warning: Atom index {atom_index} from topology file not found in PDB.")

mm_coords_array = np.array(mm_coords_list)
mm_charges_array = np.array(mm_charges_list)

filtered_mm_coords, filtered_mm_charges = filter_mm_atoms(
    ligand_coords, mm_coords_array, mm_charges_array, cutoff=CUT_OFF
)
protein_charges = list(zip(filtered_mm_charges.tolist(), filtered_mm_coords.tolist()))

##################################
# Build the QM/MM model.
##################################
qm_molecule = gto.Mole()
qm_molecule.atom = ligand_xyz_str
qm_molecule.basis = basis
qm_molecule.charge = Charge
qm_molecule.spin = 0
qm_molecule.build()

mf_vac = dft.RKS(qm_molecule).density_fit()
mf_vac.xc = method
mf_vac.with_df.auxbasis = aux_basis_set

dispersion_energy = get_dispersion(mf_vac)

qm_molecule_env = gto.Mole()
qm_molecule_env.atom = ligand_xyz_str
qm_molecule_env.basis = basis
qm_molecule_env.charge = Charge
qm_molecule_env.spin = 0
qm_molecule_env.build()

mf_qm = dft.RKS(qm_molecule_env).density_fit()
mf_qm.xc = method
mf_qm.with_df.auxbasis = aux_basis_set
mf_qmmm = qmmm.add_mm_charges(mf_qm, filtered_mm_coords, filtered_mm_charges)
energy_qmmm = mf_qmmm.kernel()

energy_qmmm_total = energy_qmmm + dispersion_energy

##################################
Binding_energy_Ha = (energy_qmmm_total - e_quantum_lig)

end_time = time.time()
elapsed_time = (end_time - start_time) / 60
current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

##################################
# Write output
##################################
output_file = "output_inQMMMVQE.txt"
with open(output_file, "w") as file:
    file.write("*****************************BFE-QM3 Version 4.0, Sep 2025********************************\n")
    file.write('"Statistical mechanics, quantum Mechanics & quantum computing for Protein Ligand Affinity Scoring"\n')
    file.write("Written by: Dr. Farzad Molani\n")
    file.write("http://www.incerebro.com\n")
    file.write("HallaEcoValley, 25, Ttukseom-ro 1-gil, Seongdong-gu, Seoul, Republic of Korea (04778)\n")
    file.write("Tel. +821097838309\n")
    file.write(f"Date of Printing: {current_datetime}\n")
    file.write("=============================================================\n")
    file.write("                      SUMMARY\n")
    file.write("=============================================================\n")
    file.write("-------------------------------------------------------------\n")
    file.write(f"The QM region (ligand) is described by an active space of {ligand.n_active_mos} MOs and {ligand.n_active_electrons} electrons.\n")
    file.write(f"The gas phase molecular energy of the ligand is {e_quantum_lig:.5f} Ha.\n")
    file.write(f"The QM/MM binding energy is {Binding_energy_Ha:5.3f} Ha.\n")
    file.write(f"Run time: {elapsed_time:.2f} minutes\n")
    file.write("=============================================================\n")

