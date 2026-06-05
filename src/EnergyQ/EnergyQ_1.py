#!/usr/bin/env python3

import os
import shutil
import glob
import subprocess

def remove_ter_and_renumber(pdb_file):
    new_lines = []
    new_atom_index = 1
    with open(pdb_file, "r") as fin:
        for line in fin:
            if line.startswith(("ATOM", "HETATM")):
                newline = line[:6] + f"{new_atom_index:5d}" + line[11:]
                new_lines.append(newline)
                new_atom_index += 1
            elif line.startswith("END"):
                new_lines.append(line)
    with open(pdb_file, "w") as fout:
        fout.writelines(new_lines)

def select_protein_top(top_folder):
    top_files = glob.glob(os.path.join(top_folder, "protein*.top"))
    return top_files[0] if top_files else None

# === CONFIGURATION ===
pdb_base = os.path.abspath("../system/system_vm2/run1/results/forpostprocess/pdb/complexes/protein_p4a_tleap")
top_base = os.path.abspath("../system/system_vm2/run1/results/forpostprocess/top/complexes/protein_p4a_tleap")
work_dir = os.getcwd()

qm_mm_input_script         = "inQMMMVQE.py"
dispersion_input_script = "dispersion.py"

# === MAIN LOOP ===
for i in range(1, 100001):
    pdb_folder = os.path.join(pdb_base, f"protein_p4a_tleap--lig_{i}", "1")
    top_folder = os.path.join(top_base, f"protein_p4a_tleap--lig_{i}", "1")

    pdb_files = glob.glob(os.path.join(pdb_folder, "*.pdb"))
    top_file = select_protein_top(top_folder)

    if not pdb_files or not top_file:
        continue

    dest_dir = os.path.join(work_dir, f"lig_{i}")
    if os.path.exists(dest_dir):
        continue

    os.makedirs(dest_dir, exist_ok=True)

    copied_pdb = shutil.copy(pdb_files[0], dest_dir)
    copied_top = shutil.copy(top_file, dest_dir)
    shutil.copy(qm_mm_input_script, dest_dir)
    shutil.copy(dispersion_input_script, dest_dir)

    new_pdb = os.path.join(dest_dir, "complex.pdb")
    new_top = os.path.join(dest_dir, "topology.top")
    os.rename(copied_pdb, new_pdb)
    os.rename(copied_top, new_top)

    remove_ter_and_renumber(new_pdb)

    ligand_pdb_path = os.path.join(dest_dir, "ligand.pdb")
    with open(new_pdb, "r") as fin, open(ligand_pdb_path, "w") as fout:
        for line in fin:
            if line.startswith(("ATOM", "HETATM")) and line[17:20].strip() == "MOL":
                fout.write(line)

    conv_result = subprocess.run(
        ["obabel", "-ipdb", "ligand.pdb", "-oxyz", "-O", "ligand.xyz"],
        cwd=dest_dir, capture_output=True, text=True
    )
    if conv_result.returncode != 0:
        print(f"[Ligand {i}] Open Babel conversion error:\n{conv_result.stderr}")
        continue

    # === Run QM/MM script in parallel ===

    result = subprocess.run(["python", qm_mm_input_script], cwd=dest_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[Ligand {i}] Script {qm_mm_solvate_input_script} failed:\n{result.stderr}")
