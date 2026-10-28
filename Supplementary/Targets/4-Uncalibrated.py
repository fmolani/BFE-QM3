import os
import glob
import numpy as np
import pandas as pd

from scipy.stats import pearsonr, spearmanr, kendalltau
from sklearn.linear_model import LinearRegression


# ============================================================
# SETTINGS
# ============================================================

# Start from the directory containing the target folders
ROOT_DIRECTORY = "."

FILE_NAME = "output_QM3_scaled_offset.csv"

# Output files
PER_TARGET_OUTPUT = "uncalibrated_metrics_by_target.csv"
POOLED_OUTPUT = "uncalibrated_metrics_pooled.csv"


# ============================================================
# METRIC FUNCTION
# ============================================================

def calculate_metrics(exp, pred):

    exp = np.asarray(exp, dtype=float)
    pred = np.asarray(pred, dtype=float)

    # Remove NaN / inf
    mask = (
        np.isfinite(exp) &
        np.isfinite(pred)
    )

    exp = exp[mask]
    pred = pred[mask]

    n = len(exp)

    if n < 2:
        return {
            "N": n,
            "MAE": np.nan,
            "RMSE": np.nan,
            "Slope": np.nan,
            "Pearson_R": np.nan,
            "Spearman_rho": np.nan,
            "Kendall_tau": np.nan
        }

    # --------------------------------------------------------
    # MAE
    # --------------------------------------------------------
    mae = np.mean(np.abs(pred - exp))

    # --------------------------------------------------------
    # RMSE
    # --------------------------------------------------------
    rmse = np.sqrt(np.mean((pred - exp) ** 2))

    # --------------------------------------------------------
    # Linear regression:
    # Predicted = slope * Experimental + intercept
    # --------------------------------------------------------
    X = exp.reshape(-1, 1)
    y = pred

    model = LinearRegression()
    model.fit(X, y)

    slope = model.coef_[0]
    intercept = model.intercept_

    # --------------------------------------------------------
    # Pearson R
    # --------------------------------------------------------
    if np.std(exp) == 0 or np.std(pred) == 0:
        pearson_r = np.nan
    else:
        pearson_r, pearson_p = pearsonr(exp, pred)

    # --------------------------------------------------------
    # Spearman rho
    # --------------------------------------------------------
    if np.std(exp) == 0 or np.std(pred) == 0:
        spearman_rho = np.nan
    else:
        spearman_rho, spearman_p = spearmanr(exp, pred)

    # --------------------------------------------------------
    # Kendall tau
    # --------------------------------------------------------
    if np.std(exp) == 0 or np.std(pred) == 0:
        kendall_tau = np.nan
    else:
        kendall_tau, kendall_p = kendalltau(exp, pred)

    return {
        "N": n,
        "MAE": mae,
        "RMSE": rmse,
        "Slope": slope,
        "Pearson_R": pearson_r,
        "Spearman_rho": spearman_rho,
        "Kendall_tau": kendall_tau
    }


# ============================================================
# FIND ALL TARGET FILES
# ============================================================

pattern = os.path.join(
    ROOT_DIRECTORY,
    "**",
    FILE_NAME
)

files = sorted(
    glob.glob(pattern, recursive=True)
)

print("=" * 80)
print("UNCALIBRATED BFE-QM3 ANALYSIS")
print("=" * 80)

print(f"\nSearching for: {FILE_NAME}")
print(f"Root directory: {os.path.abspath(ROOT_DIRECTORY)}")
print(f"Found {len(files)} files.\n")

if len(files) == 0:
    raise FileNotFoundError(
        f"No '{FILE_NAME}' files were found under "
        f"{os.path.abspath(ROOT_DIRECTORY)}"
    )


# ============================================================
# PROCESS EACH TARGET
# ============================================================

all_data = []
target_results = []

for file_path in files:

    # --------------------------------------------------------
    # Determine target name from parent directory
    # --------------------------------------------------------
    target_folder = os.path.basename(
        os.path.dirname(file_path)
    )

    print(f"Processing: {target_folder}")
    print(f"  File: {file_path}")

    # --------------------------------------------------------
    # Read CSV
    # --------------------------------------------------------
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"  ERROR reading file: {e}")
        continue

    # --------------------------------------------------------
    # Check columns
    # --------------------------------------------------------
    if df.shape[1] < 2:
        print("  ERROR: File has fewer than 2 columns.")
        continue

    # ========================================================
    # IMPORTANT:
    # Column 1 = experimental
    # Column 2 = raw/un-calibrated prediction
    # ========================================================

    exp = pd.to_numeric(
        df.iloc[:, 0],
        errors="coerce"
    )

    pred = pd.to_numeric(
        df.iloc[:, 1],
        errors="coerce"
    )

    # Remove invalid values
    valid = (
        np.isfinite(exp) &
        np.isfinite(pred)
    )

    exp = exp[valid].to_numpy()
    pred = pred[valid].to_numpy()

    if len(exp) == 0:
        print("  WARNING: No valid data.")
        continue

    # --------------------------------------------------------
    # Calculate metrics
    # --------------------------------------------------------
    metrics = calculate_metrics(exp, pred)

    result = {
        "Target": target_folder,
        **metrics
    }

    target_results.append(result)

    # --------------------------------------------------------
    # Keep data for pooled analysis
    # --------------------------------------------------------
    for e, p in zip(exp, pred):
        all_data.append({
            "Target": target_folder,
            "Experimental": e,
            "Raw_Prediction": p
        })

    print(
        f"  N = {metrics['N']}, "
        f"R = {metrics['Pearson_R']:.3f}, "
        f"rho = {metrics['Spearman_rho']:.3f}, "
        f"tau = {metrics['Kendall_tau']:.3f}"
    )


# ============================================================
# SAVE PER-TARGET RESULTS
# ============================================================

target_df = pd.DataFrame(target_results)

if len(target_df) == 0:
    raise RuntimeError(
        "No valid target data were found."
    )

target_df = target_df.sort_values("Target")

target_df.to_csv(
    PER_TARGET_OUTPUT,
    index=False
)

print("\n" + "=" * 80)
print("PER-TARGET UNCALIBRATED RESULTS")
print("=" * 80)

print(
    target_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.3f}"
    )
)

print(
    f"\nSaved: {os.path.abspath(PER_TARGET_OUTPUT)}"
)


# ============================================================
# MEAN ACROSS TARGETS
# ============================================================

mean_results = {
    "N_targets": len(target_df),
    "Mean_N_per_target": target_df["N"].mean(),
    "Mean_MAE": target_df["MAE"].mean(),
    "Mean_RMSE": target_df["RMSE"].mean(),
    "Mean_Slope": target_df["Slope"].mean(),
    "Mean_Pearson_R": target_df["Pearson_R"].mean(),
    "Mean_Spearman_rho": target_df["Spearman_rho"].mean(),
    "Mean_Kendall_tau": target_df["Kendall_tau"].mean()
}

print("\n" + "=" * 80)
print("MEAN ACROSS TARGETS")
print("=" * 80)

print(
    f"Number of targets : {mean_results['N_targets']}"
)

print(
    f"Mean N/target     : "
    f"{mean_results['Mean_N_per_target']:.2f}"
)

print(
    f"MAE               : "
    f"{mean_results['Mean_MAE']:.3f} kcal/mol"
)

print(
    f"RMSE              : "
    f"{mean_results['Mean_RMSE']:.3f} kcal/mol"
)

print(
    f"Slope             : "
    f"{mean_results['Mean_Slope']:.3f}"
)

print(
    f"Pearson R         : "
    f"{mean_results['Mean_Pearson_R']:.3f}"
)

print(
    f"Spearman rho      : "
    f"{mean_results['Mean_Spearman_rho']:.3f}"
)

print(
    f"Kendall tau       : "
    f"{mean_results['Mean_Kendall_tau']:.3f}"
)


# ============================================================
# POOLED 543-LIGAND ANALYSIS
# ============================================================

pooled_df = pd.DataFrame(all_data)

print("\n" + "=" * 80)
print("POOLED UNCALIBRATED ANALYSIS")
print("=" * 80)

pooled_metrics = calculate_metrics(
    pooled_df["Experimental"].values,
    pooled_df["Raw_Prediction"].values
)

print(
    f"N                 : {pooled_metrics['N']}"
)

print(
    f"MAE               : "
    f"{pooled_metrics['MAE']:.3f} kcal/mol"
)

print(
    f"RMSE              : "
    f"{pooled_metrics['RMSE']:.3f} kcal/mol"
)

print(
    f"Slope             : "
    f"{pooled_metrics['Slope']:.3f}"
)

print(
    f"Pearson R         : "
    f"{pooled_metrics['Pearson_R']:.3f}"
)

print(
    f"Spearman rho      : "
    f"{pooled_metrics['Spearman_rho']:.3f}"
)

print(
    f"Kendall tau       : "
    f"{pooled_metrics['Kendall_tau']:.3f}"
)


# ============================================================
# SAVE POOLED RESULTS
# ============================================================

pooled_output = pd.DataFrame([{
    "N": pooled_metrics["N"],
    "MAE": pooled_metrics["MAE"],
    "RMSE": pooled_metrics["RMSE"],
    "Slope": pooled_metrics["Slope"],
    "Pearson_R": pooled_metrics["Pearson_R"],
    "Spearman_rho": pooled_metrics["Spearman_rho"],
    "Kendall_tau": pooled_metrics["Kendall_tau"]
}])

pooled_output.to_csv(
    POOLED_OUTPUT,
    index=False
)

print(
    f"\nSaved: {os.path.abspath(POOLED_OUTPUT)}"
)


# ============================================================
# SAVE ALL RAW DATA USED IN ANALYSIS
# ============================================================

pooled_df.to_csv(
    "uncalibrated_raw_data_all_targets.csv",
    index=False
)

print(
    f"Saved: {os.path.abspath('uncalibrated_raw_data_all_targets.csv')}"
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)

print("\nMean across targets:")
print(
    f"  MAE          = {mean_results['Mean_MAE']:.3f} kcal/mol"
)
print(
    f"  RMSE         = {mean_results['Mean_RMSE']:.3f} kcal/mol"
)
print(
    f"  Slope        = {mean_results['Mean_Slope']:.3f}"
)
print(
    f"  Pearson R    = {mean_results['Mean_Pearson_R']:.3f}"
)
print(
    f"  Spearman rho = {mean_results['Mean_Spearman_rho']:.3f}"
)
print(
    f"  Kendall tau  = {mean_results['Mean_Kendall_tau']:.3f}"
)

print("\nPooled all-ligand result:")
print(
    f"  N            = {pooled_metrics['N']}"
)
print(
    f"  MAE          = {pooled_metrics['MAE']:.3f} kcal/mol"
)
print(
    f"  RMSE         = {pooled_metrics['RMSE']:.3f} kcal/mol"
)
print(
    f"  Slope        = {pooled_metrics['Slope']:.3f}"
)
print(
    f"  Pearson R    = {pooled_metrics['Pearson_R']:.3f}"
)
print(
    f"  Spearman rho = {pooled_metrics['Spearman_rho']:.3f}"
)
print(
    f"  Kendall tau  = {pooled_metrics['Kendall_tau']:.3f}"
)

print("\nDone.")