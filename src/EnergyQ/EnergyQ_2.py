import subprocess
import os
import csv
import numpy as np
import shutil
from datetime import datetime
import glob
import re
import pandas as pd
from scipy.stats import pearsonr, spearmanr, kendalltau

##################################
# Copy SUMMARY files to current directory
##################################
for csv_file in glob.glob("../system/system_vm2/run1/results/*SUMMARY.csv"):
    shutil.copy(csv_file, ".")

root_directory = "."
data = []

# Regex pattern for energy extraction
energy_pattern = re.compile(r"The QM/MM binding energy is\s+(-?\d+\.\d+)\s+Ha\.")

for folder in os.listdir(root_directory):
    folder_path = os.path.join(root_directory, folder)
    if folder.startswith("lig_") and os.path.isdir(folder_path):
        file_path = os.path.join(folder_path, "output_inQMMMVQE.txt")
        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                for line in file:
                    match = energy_pattern.search(line)
                    if match:
                        energy = float(match.group(1))
                        data.append([folder, energy])
                        break

##################################
# Save VQE energies
##################################
vqe_csv = "VQE_energies.csv"
pd.DataFrame(data, columns=["Folder Name", "inQMMMVQE Energy"]).to_csv(vqe_csv, index=False)

# Sort by ligand number
vqe_df = pd.read_csv(vqe_csv)
vqe_df["lig_num"] = vqe_df["Folder Name"].apply(lambda x: int(x.split("_")[1]))
vqe_df.sort_values("lig_num", inplace=True)
vqe_df.drop(columns="lig_num", inplace=True)
vqe_df.to_csv("sorted_VQE_energies.csv", index=False)

##################################
# Clean unnecessary files
##################################
def remove_extra_files(directory):
    extensions = [".AC0", ".AC", ".ESP", ".FRCMOD", ".chk", ".INF", ".fchk", ".7"]
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                os.remove(os.path.join(root, file))

remove_extra_files(".")

##################################
# Load SUMMARY CSV
##################################
summary_files = [f for f in os.listdir(".") if f.endswith("vm2_SUMMARY.csv")]
if len(summary_files) != 1:
    raise FileNotFoundError("Expected exactly one vm2_SUMMARY.csv file.")

summary_data = pd.read_csv(summary_files[0])

##################################
# Combine VQE + classical free energy (qu3+)
##################################
vqe_energy = pd.read_csv("sorted_VQE_energies.csv")["inQMMMVQE Energy"]
classic_energy = summary_data.iloc[:, 8]
experimental_values = summary_data.iloc[:, 4]

VQE_QMMM_VM2_energy = vqe_energy + classic_energy

pd.DataFrame({
    "EXP deltaG": experimental_values,
    "VQE+MM deltaG": VQE_QMMM_VM2_energy
}).to_csv("QM3_energy.csv", index=False)

##################################
# Scaling offset for QM3 energies
##################################
scale_factor = 0.50
rows_qu3 = []
for exp, combined in zip(experimental_values, VQE_QMMM_VM2_energy):
    scaled_energy = combined * scale_factor
    rows_qu3.append([exp, combined, scaled_energy])

for row in rows_qu3:
    error = (row[2] - row[0])
    row.append(error)
mean_error = np.mean([row[3] for row in rows_qu3])
for row in rows_qu3:
    row.append(mean_error)
for row in rows_qu3:
    scaled_offset = row[2] - row[4]
    row.append(scaled_offset)
for row in rows_qu3:
    scaled_abs_error = abs(row[0] - row[5])
    row.append(scaled_abs_error)
mean_scaled_abs_err_offset = np.mean([row[6] for row in rows_qu3])
for row in rows_qu3:
    row.append(mean_scaled_abs_err_offset)

columns_qu3 = ['EXP deltaG','VQE+MM deltaG','scaled_energy','error','mean_err','scaled_energy_offset','scaled_abs_err_offset','mean_scaled_abs_err_offset']
df_qu3 = pd.DataFrame(rows_qu3, columns=columns_qu3)


##################################
# Statistical metrics
##################################
def compute_metrics(pred, exp):
    pred = np.array(pred)
    exp = np.array(exp)
    return {
        "Pearson_r": pearsonr(pred, exp)[0],
        "Spearman_rho": spearmanr(pred, exp)[0],
        "Kendall_tau": kendalltau(pred, exp)[0],
        "MAE": np.mean(np.abs(pred - exp)),
        "RMSE": np.sqrt(np.mean((pred - exp) ** 2)),
        "SD_error": np.std(np.abs(pred - exp))
    }

metrics_qu3 = compute_metrics(df_qu3["scaled_energy_offset"], experimental_values)

##################################
# Write results summary
##################################
current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open("Results-BFE-QM3.txt", "w") as f:
    f.write("*****************************BFE-QM3 Version 4.0, Sep 2025********************************\n")
    f.write('"Statistical mechanics, quantum Mechanics & quantum computing for Protein Ligand Affinity Scoring"\n')
    f.write("Written by: Dr. Farzad Molani\n")
    f.write("http://www.incerebro.com\n")
    f.write("HallaEcoValley, Seoul, Republic of Korea\n")
    f.write(f"Date of Printing: {current_datetime}\n")
    f.write("=" * 90 + "\n")
    f.write("STATISTICS SUMMARY\n")
    f.write("=" * 90 + "\n")

    f.write("MIND-qu3+:\n")
    for k, v in metrics_qu3.items():
        f.write(f"  {k:15s}: {v:.2f}\n")

##################################
# Save CSV outputs
##################################
df_qu3.to_csv("output_QM3_scaled_offset.csv", index=False)

##################################
# Final cleanup (Python-safe replacement for `rm`)
##################################
for fname in ["protein_p4a_tleap_vm2_SUMMARY.csv", "VQE_energies.csv","sorted_VQE_energies.csv"]:
    if os.path.isfile(fname):
        os.remove(fname)
