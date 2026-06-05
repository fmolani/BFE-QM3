#!/usr/bin/env python
import run_esp_module

if __name__ == '__main__':
    xyz_file = "ligand.xyz"  # Ensure this file exists or provide the full path.
    
    # Define the basis set (e.g., "aug-cc-pvdz" or "6-31g")
    basis_set = "madef2svp"
    
    # Define which methods to calculate: options include "RHF", "DFT", "MP2", or a combination.
    methods_to_calc = ("RHF",)
    
    # Define the molecular charge (e.g., 0 for neutral, 1 for cation, -1 for anion, etc.)
    mol_charge = 0
    
    # Optionally, define any ESP options (or leave as default by passing None)
    esp_options = {
        "RCUT": 3.0,       # Angstrom
        "SPACE": 0.8,      # Angstrom
        "probe": 0.8,
        "restraint": True,
        "resp_hfree": True,
        "resp_a": 0.001,
        "resp_b": 0.1,
        "resp_maxiter": 100,
        "resp_tolerance": 1.0e-4,
    }
    
    # Optionally, define solvent options for including solvent effects using the PCM model.
    solvent_options = {"solvent": "water"}

    run_esp_module.run_esp_charges(
        xyz_file,
        esp_options,
        basis=basis_set,
        calc_methods=methods_to_calc,
        charge=mol_charge,
        solvent_options=solvent_options
    )
