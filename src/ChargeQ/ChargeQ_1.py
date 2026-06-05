import os
import shutil
import subprocess
import glob

working_directory = "."  # Replace with your working directory

xyz_directory = "../system/system_vm2/run1/calculations/snap"  # Replace with the actual base directory path

# Copy `.top` files to the current directory
for top_file in glob.glob("../system/system_vm2/setup/prepared_input_data/ligands/*.top"):
    shutil.copy(top_file, ".")

# Copy `.mol2` files to the current directory
for mol2_file in glob.glob("../system/system_vm2/setup/prepared_input_data/ligands/*.mol2"):
    shutil.copy(mol2_file, ".")


def extract_first_conformer(xyz_file, output_file):
    """
    Extracts the first conformer from an XYZ file containing multiple conformers.

    Parameters:
        xyz_file (str): Path to the input XYZ file with multiple conformers.
        output_file (str): Path to save the first conformer.
    """
    try:
        with open(xyz_file, 'r') as infile:
            lines = infile.readlines()

        # The first line contains the number of atoms
        num_atoms = int(lines[0].strip())

        # The first conformer includes the number of atoms, a comment, and atomic coordinates
        first_conformer = lines[:2 + num_atoms]

        # Write the first conformer to the output file
        with open(output_file, 'w') as outfile:
            outfile.writelines(first_conformer)

        # print(f"First conformer extracted and saved to {output_file}")
    except Exception as e:
        print(f"Error: {e}")


def process_ligands_and_copy_to_working_directory(xyz_dir, output_dir):
    """
    Processes the ligand folders, extracts the first conformer, and copies them to the working directory.

    Parameters:
        base_dir (str): The base directory containing ligand folders (lig_{i}_snap.xyz).
        output_dir (str): The working directory to copy the extracted conformers.
    """
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i in range(1, 100000):
        folder_name = f"lig_{i}"
        xyz_file = os.path.join(xyz_dir, folder_name, f"{folder_name}_snap.xyz")
        output_file = os.path.join(output_dir, f"lig_{i}.xyz")

        if os.path.exists(xyz_file):
            extract_first_conformer(xyz_file, output_file)
        else:
            pass


process_ligands_and_copy_to_working_directory(xyz_directory, working_directory)


# Loop over all `.mol2` files in the current directory
for mol2_file in os.listdir():
    if mol2_file.endswith(".mol2"):
        group1 = mol2_file.split("_")[1].split(".")[0]  # Extract group identifier from the filename
        folder_name = f"model_{group1}"

        # Create a directory for the model
        os.mkdir(folder_name)

        # Handle `.mol2` files
        src_file = os.path.abspath(mol2_file)
        dest_file = os.path.join(folder_name, 'ligand.mol2')
        shutil.copy(src_file, dest_file)

        # Handle `.top` files
        top_file_name = f"lig_{group1}.top"
        for top_file in os.listdir():
            if top_file.endswith(top_file_name):
                src_file = os.path.abspath(top_file)
                dest_file = os.path.join(folder_name, top_file_name)
                shutil.copy(src_file, dest_file)

        xyz_file_name = f"lig_{group1}.xyz"
        for xyz_file in os.listdir():
            if xyz_file.endswith(xyz_file_name):
                src_file = os.path.abspath(xyz_file)
                dest_file = os.path.join(folder_name, 'ligand.xyz')
                shutil.copy(src_file, dest_file)

        # Copy required files to the model folder
        shutil.copy("run_esp.py", folder_name)
        shutil.copy("run_esp_module.py", folder_name)

        # Change to the model directory and run commands
        os.chdir(folder_name)
        try:
            with open(os.devnull, 'w') as devnull:
                commands = [
                    "python run_esp.py",
                ]
                for command in commands:
                    process = subprocess.Popen(command, shell=True, stdout=devnull, stderr=subprocess.DEVNULL)
                    process.wait()

            # Process ESP charges for .top file
            top_file_name_resp = f"lig_{group1}.top"
            try:
                with open(top_file_name_resp, 'r') as f1, open('esp_charges_RHF.txt', 'r') as f2:
                    top_lines = f1.readlines()
                    chelpg_lines = f2.readlines()

                start1, end1 = None, None
                for k, line in enumerate(top_lines):
                    if '!NTITLE 3' in line:
                        start1 = k + 2
                    elif end1 is None and line.strip().startswith('!NBOND'):
                        end1 = k

                start2 = None
                for k, line in enumerate(chelpg_lines):
                    if 'RHF ESP Charges' in line:
                        start2 = k + 1

                for k in range(start1, end1):
                    top_fields = top_lines[k].split()
                    chelpg_fields = chelpg_lines[start2 + k - start1].split()
                    top_fields[3] = chelpg_fields[1]
                    top_lines[k] = '{:>5s}{:>3s}{:>13s}{:>12s}{:>11s}{:>11s}\n'.format(*top_fields)

                top_file_name_esp = f"lig_{group1}.top_ESP"
                with open(top_file_name_esp, 'w') as f:
                    f.writelines(top_lines)

            except Exception as e:
                print(f"Error processing ESP charges for .top file: {e}")

            # --- Start of new code to add (mol2 update) ---
            try:
                # Read charges from 'esp_charges_RHF.txt'
                charges = []
                with open('esp_charges_RHF.txt', 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('RHF ESP Charges'):  # Skip header
                            try:
                                # Assuming the format is "atom_index charge_value"
                                # We only need the charge value
                                parts = line.split()
                                if len(parts) >= 2:
                                    charges.append(parts[1])
                            except ValueError:
                                print(f"Skipping invalid line in esp_charges_RHF.txt: {line}")

                # Update the mol2 file, preserving original spacing
                with open('ligand.mol2', 'r') as f, open('new_ligand.mol2', 'w') as out:
                    in_atom_section = False
                    charge_index = 0
                    for line in f:
                        if line.startswith('@<TRIPOS>ATOM'):
                            in_atom_section = True
                            out.write(line)
                        elif line.startswith('@<TRIPOS>'):
                            in_atom_section = False
                            out.write(line)
                        elif in_atom_section and line.strip() and line.split()[0].isdigit():
                            fields = line.split()
                            if len(fields) >= 9:  # Ensure valid atom line
                                if charge_index < len(charges): # Prevent IndexError
                                    # Replace the charge (last field) with the new charge
                                    fields[-1] = charges[charge_index]
                                    charge_index += 1
                                    # Reconstruct the line with fixed-width formatting
                                    formatted_line = (
                                        f"{fields[0]:>7s} "    # Atom ID (string, right-aligned)
                                        f"{fields[1]:<10s}"    # Atom name (string, left-aligned)
                                        f"{float(fields[2]):>10.4f}"  # X coordinate (float)
                                        f"{float(fields[3]):>10.4f}"  # Y coordinate (float)
                                        f"{float(fields[4]):>10.4f}"  # Z coordinate (float)
                                        f"{fields[5]:<6s} "    # Atom type (string, left-aligned)
                                        f"{fields[6]:>4s} "    # Subst ID (string, right-aligned)
                                        f"{fields[7]:<8s} "    # Subst name (string, left-aligned)
                                        f"{float(fields[8]):>10.6f}\n"  # Charge (float)
                                    )
                                    out.write(formatted_line)
                                else:
                                    # If not enough charges, write the original line
                                    out.write(line)
                            else:
                                out.write(line) # Write non-atom section lines
                        else:
                            out.write(line)

                # Replace the original mol2 file with the updated one
                shutil.move('new_ligand.mol2', 'ligand.mol2')

                # Verify the number of updated charges
                if charge_index != len(charges):
                    print(f"Warning: Number of charges read from esp_charges_RHF.txt ({len(charges)}) does not match updated atoms ({charge_index}). Check atom order or file format.")

            except Exception as e:
                print(f"Error processing ESP charges for .mol2 file: {e}")
            # --- End of new code to add ---

        finally:
            os.chdir('..')