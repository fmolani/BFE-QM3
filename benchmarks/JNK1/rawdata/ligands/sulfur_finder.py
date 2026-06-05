from rdkit import Chem
import os

def find_sulfur_ligands(molfile_dir):
    sulfur_ligands = []
    for filename in os.listdir(molfile_dir):
        if filename.endswith(".mol"):
            filepath = os.path.join(molfile_dir, filename)
            mol = Chem.MolFromMolFile(filepath, sanitize=False)
            if mol:
                atom_symbols = [atom.GetSymbol() for atom in mol.GetAtoms()]
                if 'S' in atom_symbols:
                    sulfur_ligands.append(filename)
    return sulfur_ligands

# Example usage
molfile_directory = "."
sulfur_ligands = find_sulfur_ligands(molfile_directory)
print("Ligands with sulfur atoms:")
for ligand in sulfur_ligands:
    print(ligand)
