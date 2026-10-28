#!/usr/bin/env python3
"""
Unpaired bootstrap 95% CIs for R / rho / Kendall / MAE / RMSE / SD / Slope
+ paired bootstrap difference analysis (TEST - BASE)

SD = np.std(|error|)  (same definition as your script)
Saves all printed output to bootstrap_results.txt
"""
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, kendalltau, linregress
import sys
from datetime import datetime

class Tee:
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    def flush(self):
        for f in self.files:
            f.flush()

output_file = open("bootstrap_results.txt", "w", encoding="utf-8")
output_file.write(f"Bootstrap analysis results  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
output_file.write("=" * 70 + "\n\n")

original_stdout = sys.stdout
sys.stdout = Tee(original_stdout, output_file)

FILES = [
    "output_MM_scaled_offset.csv",
    "output_QMFF_scaled_offset.csv",
    "output_QM3_scaled_offset.csv",
]
N_BOOT_UNPAIRED = 10_000
SEED_UNPAIRED = 42

def unpaired_cis(path):
    df = pd.read_csv(path)
    exp = df["EXP deltaG"].to_numpy(dtype=float)
    pred = df["scaled_energy_offset"].to_numpy(dtype=float)
    signed_err = exp - pred
    abs_err = np.abs(signed_err)          # absolute errors (matches your code)
    n = len(exp)
    rng = np.random.default_rng(SEED_UNPAIRED)

    r_boot   = np.empty(N_BOOT_UNPAIRED)
    rho_boot = np.empty(N_BOOT_UNPAIRED)
    tau_boot = np.empty(N_BOOT_UNPAIRED)
    mae_boot = np.empty(N_BOOT_UNPAIRED)
    rmse_boot = np.empty(N_BOOT_UNPAIRED)
    sd_boot  = np.empty(N_BOOT_UNPAIRED)
    slope_boot = np.empty(N_BOOT_UNPAIRED)

    for i in range(N_BOOT_UNPAIRED):
        idx = rng.choice(n, size=n, replace=True)
        e, p = exp[idx], pred[idx]
        se = e - p
        r_boot[i]    = pearsonr(e, p)[0]
        rho_boot[i]  = spearmanr(e, p)[0]
        tau_boot[i]  = kendalltau(e, p)[0]
        mae_boot[i]  = np.mean(np.abs(se))
        rmse_boot[i] = np.sqrt(np.mean(se ** 2))
        sd_boot[i]   = np.std(np.abs(se))          # <-- same as your code
        slope_boot[i] = linregress(e, p).slope if np.std(e) > 0 else np.nan

    def ci(arr):
        valid = arr[np.isfinite(arr)]
        return np.percentile(valid, [2.5, 97.5])

    return {
        "n": n,
        "R":     (pearsonr(exp, pred)[0], ci(r_boot)),
        "rho":   (spearmanr(exp, pred)[0], ci(rho_boot)),
        "tau":   (kendalltau(exp, pred)[0], ci(tau_boot)),
        "MAE":   (np.mean(np.abs(signed_err)), ci(mae_boot)),
        "RMSE":  (np.sqrt(np.mean(signed_err ** 2)), ci(rmse_boot)),
        "SD":    (np.std(abs_err), ci(sd_boot)),   # <-- same as your code
        "Slope": (linregress(exp, pred).slope, ci(slope_boot)),
    }

print("=" * 70)
print("UNPAIRED 95% BOOTSTRAP INTERVALS")
print("=" * 70)

for f in FILES:
    try:
        res = unpaired_cis(f)
        print(f"\n{f}  (n = {res['n']})")
        print(f"  Pearson R     : {res['R'][0]:7.2f}   [{res['R'][1][0]:7.2f}, {res['R'][1][1]:7.2f}]")
        print(f"  Spearman rho  : {res['rho'][0]:7.2f}   [{res['rho'][1][0]:7.2f}, {res['rho'][1][1]:7.2f}]")
        print(f"  Kendall tau   : {res['tau'][0]:7.2f}   [{res['tau'][1][0]:7.2f}, {res['tau'][1][1]:7.2f}]")
        print(f"  MAE  (kcal/mol): {res['MAE'][0]:7.2f}   [{res['MAE'][1][0]:7.2f}, {res['MAE'][1][1]:7.2f}]")
        print(f"  RMSE (kcal/mol): {res['RMSE'][0]:7.2f}   [{res['RMSE'][1][0]:7.2f}, {res['RMSE'][1][1]:7.2f}]")
        print(f"  SD   (kcal/mol): {res['SD'][0]:7.2f}   [{res['SD'][1][0]:7.2f}, {res['SD'][1][1]:7.2f}]")
        print(f"  Slope         : {res['Slope'][0]:7.2f}   [{res['Slope'][1][0]:7.2f}, {res['Slope'][1][1]:7.2f}]")
    except FileNotFoundError:
        print(f"\n{f}  --> FILE NOT FOUND")
    except Exception as e:
        print(f"\n{f}  --> ERROR: {e}")

# ------------------------------------------------------------------
# Paired bootstrap difference analysis (unchanged)
# ------------------------------------------------------------------
print("\n" + "=" * 70)
print("PAIRED BOOTSTRAP DIFFERENCE ANALYSIS")
print("=" * 70)

N_BOOT = 10_000
SEED = 83
BASE_CSV = "output_MM_scaled_offset.csv"
TEST_CSV = "output_QM3_scaled_offset.csv"

def pearson_r(yt, yp):
    if np.std(yt) == 0 or np.std(yp) == 0:
        return np.nan
    return pearsonr(yt, yp)[0]

def spearman_rho(yt, yp):
    if np.std(yt) == 0 or np.std(yp) == 0:
        return np.nan
    return spearmanr(yt, yp)[0]

def kendall_t(yt, yp):
    if np.std(yt) == 0 or np.std(yp) == 0:
        return np.nan
    return kendalltau(yt, yp)[0]

def rmse(yt, yp):
    return np.sqrt(np.mean((yt - yp) ** 2))

def mae(yt, yp):
    return np.mean(np.abs(yt - yp))

def slope(yt, yp):
    if np.std(yt) == 0:
        return np.nan
    return linregress(yt, yp).slope

def abs_slope_minus_one(yt, yp):
    s = slope(yt, yp)
    return np.nan if np.isnan(s) else abs(s - 1.0)

metrics = [
    ("Pearson R", pearson_r, "higher"),
    ("Spearman rho", spearman_rho, "higher"),
    ("Kendall tau", kendall_t, "higher"),
    ("RMSE", rmse, "lower"),
    ("MAE", mae, "lower"),
    ("Slope", slope, "none"),
    ("|Slope-1|", abs_slope_minus_one, "lower"),
]

def load_xy(path):
    df = pd.read_csv(path)
    yt = df.iloc[:, 0].to_numpy(dtype=float)
    yp = df.iloc[:, 5].to_numpy(dtype=float)
    return yt, yp

try:
    yt_base, yp_base = load_xy(BASE_CSV)
    yt_test, yp_test = load_xy(TEST_CSV)

    if len(yt_base) != len(yt_test):
        raise ValueError("Row counts differ; align ligands before pairing.")
    if not np.allclose(yt_base, yt_test, equal_nan=True):
        raise ValueError("Experimental columns differ; rows are not the same ligands.")

    n = len(yt_base)
    rng = np.random.default_rng(SEED)

    print(f"n = {n}")
    print(f"delta = TEST - BASE")
    print(f"TEST = {TEST_CSV}")
    print(f"BASE = {BASE_CSV}\n")
    print(f"{'metric':<14} {'delta':>8} {'95% CI':>22}  exclude0  better")
    print("-" * 70)

    rows = []
    for name, fn, direction in metrics:
        deltas = np.empty(N_BOOT)
        for i in range(N_BOOT):
            idx = rng.integers(0, n, n)
            d_test = fn(yt_test[idx], yp_test[idx])
            d_base = fn(yt_base[idx], yp_base[idx])
            deltas[i] = d_test - d_base

        valid = deltas[np.isfinite(deltas)]
        point = fn(yt_test, yp_test) - fn(yt_base, yp_base)
        lo, hi = np.percentile(valid, [2.5, 97.5])
        exclude0 = (lo > 0) or (hi < 0)

        if direction == "higher":
            better = "TEST" if (exclude0 and point > 0) else ("BASE" if (exclude0 and point < 0) else "ns")
        elif direction == "lower":
            better = "TEST" if (exclude0 and point < 0) else ("BASE" if (exclude0 and point > 0) else "ns")
        else:
            better = "-"

        print(f"{name:<14} {point:8.2f}   [{lo:7.2f}, {hi:7.2f}]  {str(exclude0):<8}  {better}")
        rows.append({
            "metric": name,
            "delta_test_minus_base": point,
            "ci_low": lo,
            "ci_high": hi,
            "excludes_zero": exclude0,
            "resolved_better": better,
        })

    pd.DataFrame(rows).to_csv("paired_difference_bootstrap.csv", index=False)
    print("\nSaved: paired_difference_bootstrap.csv")

except FileNotFoundError as e:
    print(f"Paired analysis skipped: {e}")
except Exception as e:
    print(f"Paired analysis error: {e}")

print("\nDone.")

sys.stdout = original_stdout
output_file.close()
print("Results also saved to: bootstrap_results.txt")