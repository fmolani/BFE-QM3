import os
import shutil
import glob

# Remove specific file types from the current directory
for file_type in ["*.top", "*.mol2", "*.xyz"]:
    for file in glob.glob(file_type):
        try:
            os.remove(file)
        except OSError as e:
            print(f"Error removing {file}: {e}")

# Loop through all items in the current directory
for item in os.listdir("."):
    if os.path.isdir(item) and item.startswith("model_"):  # If it's a directory like 'model_X'
        # Copy all *top_ESP files to the current directory
        for top_esp_file in glob.glob(os.path.join(item, "*top_ESP")):
            shutil.copy(top_esp_file, ".")
        
        # Extract the ligand ID (e.g., '1' from 'model_1')
        try:
            ligand_id = item.split('_')[1]
            # Copy ligand.mol2 from the model directory to the current directory, renaming it to lig_X.mol2
            source_mol2 = os.path.join(item, "ligand.mol2")
            destination_mol2 = f"lig_{ligand_id}.mol2"
            if os.path.exists(source_mol2):
                shutil.copy(source_mol2, destination_mol2)
            else:
                print(f"Warning: {source_mol2} not found in {item}. Skipping mol2 copy for this model.")
        except IndexError:
            print(f"Warning: Directory name {item} does not follow 'model_X' format. Skipping mol2 copy.")


        # Remove all *fchk and *chk files in the directory
        for fchk_file in glob.glob(os.path.join(item, "*fchk")):
            try:
                os.remove(fchk_file)
            except OSError as e:
                print(f"Error removing {fchk_file}: {e}")
        for chk_file in glob.glob(os.path.join(item, "*chk")):
            try:
                os.remove(chk_file)
            except OSError as e:
                print(f"Error removing {chk_file}: {e}")

# Rename *top_ESP files to *.top
for file in glob.glob("*top_ESP"):
    os.rename(file, file.replace(".top_ESP", ".top"))


# Define the destination directory for ligand files
esp_dir = "../system/system_vm2/setup/prepared_input_data/ligands/"

# Ensure the destination directory exists (though shutil.copytree above should handle its creation)
if not os.path.exists(esp_dir):
    print(f"Creating destination directory: {esp_dir}")
    os.makedirs(esp_dir)


# Copy lig_*.top files to specified locations
for i in range(1, 100000): # Assuming ligand IDs go up to a reasonable number
    top_file = f"lig_{i}.top"
    if os.path.exists(top_file):  # Check if the file exists in the current directory
        try:
            shutil.copy(top_file, esp_dir)
        except Exception as e:
            print(f"Error copying {top_file} to {esp_dir}: {e}")


# Copy lig_*.mol2 files to specified locations
for i in range(1, 100000): # Assuming ligand IDs go up to a reasonable number
    mol2_file = f"lig_{i}.mol2"
    if os.path.exists(mol2_file):  # Check if the file exists in the current directory
        try:
            shutil.copy(mol2_file, esp_dir)
        except Exception as e:
            print(f"Error copying {mol2_file} to {esp_dir}: {e}")

