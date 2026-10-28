import pandas as pd
import numpy as np
from scipy import stats
import os

# -----------------------------
# Files
# -----------------------------
csv_files = [
    "stacked_MMVM2.csv",
    "stacked_QMFF.csv",
    "stacked_QM3.csv",
]

PAIRS = [
    ("stacked_QM3.csv",  "stacked_MMVM2.csv", "QM3_minus_MM"),
    ("stacked_QM3.csv",  "stacked_QMFF.csv",  "QM3_minus_QMFF"),
    ("stacked_QMFF.csv", "stacked_MMVM2.csv", "QMFF_minus_MM"),
]

N_BOOT = 10000
CI_LEVEL = 0.95
RNG_SEED = 83
rng = np.random.default_rng(RNG_SEED)

def ci_from_boot(boot_vals, lo_pct, hi_pct):
    boot_vals = np.asarray(boot_vals, dtype=float)
    boot_vals = boot_vals[~np.isnan(boot_vals)]
    if len(boot_vals) == 0:
        return (np.nan, np.nan)
    return tuple(np.percentile(boot_vals, [lo_pct, hi_pct]))

def process_file(csv_file):
    print(f"\n{'='*60}")
    print(f"Processing (unpaired): {csv_file}")
    print(f"{'='*60}")

    df = pd.read_csv(csv_file)
    labels = df.iloc[:, 0].astype(str)
    exp = df.iloc[:, 1].to_numpy(dtype=float)
    calc = df.iloc[:, 2].to_numpy(dtype=float)
    n = len(exp)
    alpha = 1 - CI_LEVEL
    lo_pct, hi_pct = 100 * (alpha / 2), 100 * (1 - alpha / 2)

    pearson_r, pearson_p = stats.pearsonr(exp, calc)
    spearman_r, spearman_p = stats.spearmanr(exp, calc)
    kendall_tau, kendall_p = stats.kendalltau(exp, calc)
    slope, intercept, lr_r, lr_p, lr_stderr = stats.linregress(exp, calc)
    resid = calc - exp
    mae = np.mean(np.abs(resid))
    rmse = np.sqrt(np.mean(resid ** 2))
    sd = np.std(resid, ddof=1)

    boot_pearson = np.full(N_BOOT, np.nan)
    boot_spearman = np.full(N_BOOT, np.nan)
    boot_kendall = np.full(N_BOOT, np.nan)
    boot_mae = np.full(N_BOOT, np.nan)
    boot_rmse = np.full(N_BOOT, np.nan)
    boot_sd = np.full(N_BOOT, np.nan)
    boot_slope = np.full(N_BOOT, np.nan)
    boot_intercept = np.full(N_BOOT, np.nan)

    idx_all = np.arange(n)
    for b in range(N_BOOT):
        idx = rng.choice(idx_all, size=n, replace=True)
        e_b, c_b = exp[idx], calc[idx]
        if np.std(e_b) > 0 and np.std(c_b) > 0:
            boot_pearson[b] = stats.pearsonr(e_b, c_b)[0]
            boot_spearman[b] = stats.spearmanr(e_b, c_b)[0]
            boot_kendall[b] = stats.kendalltau(e_b, c_b)[0]
            s_b, i_b, *_ = stats.linregress(e_b, c_b)
            boot_slope[b] = s_b
            boot_intercept[b] = i_b
        r_b = c_b - e_b
        boot_mae[b] = np.mean(np.abs(r_b))
        boot_rmse[b] = np.sqrt(np.mean(r_b ** 2))
        boot_sd[b] = np.std(r_b, ddof=1) if n > 1 else np.nan

    ci_pearson = ci_from_boot(boot_pearson, lo_pct, hi_pct)
    ci_spearman = ci_from_boot(boot_spearman, lo_pct, hi_pct)
    ci_kendall = ci_from_boot(boot_kendall, lo_pct, hi_pct)
    ci_mae = ci_from_boot(boot_mae, lo_pct, hi_pct)
    ci_rmse = ci_from_boot(boot_rmse, lo_pct, hi_pct)
    ci_sd = ci_from_boot(boot_sd, lo_pct, hi_pct)
    ci_slope = ci_from_boot(boot_slope, lo_pct, hi_pct)
    ci_intercept = ci_from_boot(boot_intercept, lo_pct, hi_pct)

    se_pearson = np.nanstd(boot_pearson, ddof=1)
    se_spearman = np.nanstd(boot_spearman, ddof=1)
    se_kendall = np.nanstd(boot_kendall, ddof=1)
    se_mae = np.nanstd(boot_mae, ddof=1)
    se_rmse = np.nanstd(boot_rmse, ddof=1)
    se_sd = np.nanstd(boot_sd, ddof=1)
    se_slope = np.nanstd(boot_slope, ddof=1)
    se_intercept = np.nanstd(boot_intercept, ddof=1)

    tcrit = stats.t.ppf(1 - alpha / 2, df=n - 2) if n > 2 else np.nan
    if n > 2:
        resid_lr = calc - (slope * exp + intercept)
        resid_std = np.sqrt(np.sum(resid_lr ** 2) / (n - 2))
        mean_exp = np.mean(exp)
        ss_exp = np.sum((exp - mean_exp) ** 2)
        pred_se = resid_std * np.sqrt(1 + 1 / n + (exp - mean_exp) ** 2 / ss_exp)
        pred_half_width = tcrit * pred_se
    else:
        pred_half_width = np.full(n, np.nan)

    target_df = pd.DataFrame({
        "Label": labels,
        "Experimental": exp,
        "Calculated": calc,
        "Residual (Calc-Exp)": resid,
        "AbsResidual": np.abs(resid),
        "Z_vs_overall_SD": resid / sd if sd > 0 else np.nan,
        "95%_Prediction_HalfWidth": pred_half_width,
        "Outside_95%_PredictionBand": np.abs(resid) > pred_half_width if n > 2 else np.nan,
    })

    base = os.path.splitext(csv_file)[0]
    txt_file = base + ".txt"
    with open(txt_file, "w") as f:
        f.write(f"File: {csv_file}\n")
        f.write(f"N points: {n}\n")
        f.write(f"Bootstrap resamples: {N_BOOT}, CI level: {CI_LEVEL*100:.0f}%\n")
        f.write("---------------------------------\n\n")
        f.write("Correlation statistics (point estimate, 95% bootstrap CI, bootstrap SE, analytic p-value)\n")
        f.write(f"Pearson r   : {pearson_r:.4f}  CI[{ci_pearson[0]:.4f}, {ci_pearson[1]:.4f}]  SE={se_pearson:.4f}  p={pearson_p:.3e}\n")
        f.write(f"Spearman rho: {spearman_r:.4f}  CI[{ci_spearman[0]:.4f}, {ci_spearman[1]:.4f}]  SE={se_spearman:.4f}  p={spearman_p:.3e}\n")
        f.write(f"Kendall tau : {kendall_tau:.4f}  CI[{ci_kendall[0]:.4f}, {ci_kendall[1]:.4f}]  SE={se_kendall:.4f}  p={kendall_p:.3e}\n\n")
        f.write("Error statistics (point estimate, 95% bootstrap CI, bootstrap SE)\n")
        f.write(f"MAE  : {mae:.4f}  CI[{ci_mae[0]:.4f}, {ci_mae[1]:.4f}]  SE={se_mae:.4f}\n")
        f.write(f"RMSE : {rmse:.4f}  CI[{ci_rmse[0]:.4f}, {ci_rmse[1]:.4f}]  SE={se_rmse:.4f}\n")
        f.write(f"SD   : {sd:.4f}  CI[{ci_sd[0]:.4f}, {ci_sd[1]:.4f}]  SE={se_sd:.4f}\n\n")
        f.write("Linear regression: Calc = slope*Exp + intercept\n")
        f.write(f"Slope     : {slope:.4f}  CI[{ci_slope[0]:.4f}, {ci_slope[1]:.4f}]  SE(analytic)={lr_stderr:.4f}  SE(boot)={se_slope:.4f}\n")
        f.write(f"Intercept : {intercept:.4f}  CI[{ci_intercept[0]:.4f}, {ci_intercept[1]:.4f}]  SE(boot)={se_intercept:.4f}\n")
        f.write(f"R (regression)  : {lr_r:.4f}\n")
        f.write(f"p-value (slope != 0): {lr_p:.3e}\n\n")
        f.write("Target-level uncertainty: see accompanying CSV for per-point residuals,\n")
        f.write("95% prediction-interval half-widths, and flags for points outside that band.\n")

    target_csv = base + "_target_uncertainty.csv"
    target_df.to_csv(target_csv, index=False)
    print(f"Summary results saved to: {txt_file}")
    print(f"Per-target uncertainty table saved to: {target_csv}")

def load_exp_calc(path):
    df = pd.read_csv(path)
    exp = df.iloc[:, 1].to_numpy(dtype=float)
    calc = df.iloc[:, 2].to_numpy(dtype=float)
    return exp, calc

def paired_bootstrap(test_csv, base_csv, label):
    print(f"\n{'='*60}")
    print(f"Paired comparison: {label}")
    print(f"{'='*60}")

    exp_test, calc_test = load_exp_calc(test_csv)
    exp_base, calc_base = load_exp_calc(base_csv)

    if len(exp_test) != len(exp_base):
        raise ValueError(f"Row count mismatch: {test_csv} vs {base_csv}")
    if not np.allclose(exp_test, exp_base, equal_nan=True):
        raise ValueError(f"Experimental values differ between {test_csv} and {base_csv}")

    n = len(exp_test)
    alpha = 1 - CI_LEVEL
    lo_pct, hi_pct = 100 * (alpha / 2), 100 * (1 - alpha / 2)

    def pearson(e, c):
        return stats.pearsonr(e, c)[0] if np.std(e) > 0 and np.std(c) > 0 else np.nan
    def spearman(e, c):
        return stats.spearmanr(e, c)[0] if np.std(e) > 0 and np.std(c) > 0 else np.nan
    def kendall(e, c):
        return stats.kendalltau(e, c)[0] if np.std(e) > 0 and np.std(c) > 0 else np.nan
    def mae_fn(e, c):
        return np.mean(np.abs(c - e))
    def rmse_fn(e, c):
        return np.sqrt(np.mean((c - e) ** 2))
    def sd_fn(e, c):
        return np.std(c - e, ddof=1)
    def slope_fn(e, c):
        return stats.linregress(e, c).slope if np.std(e) > 0 else np.nan

    metrics = [
        ("Pearson R", pearson, "higher"),
        ("Spearman rho", spearman, "higher"),
        ("Kendall tau", kendall, "higher"),
        ("MAE", mae_fn, "lower"),
        ("RMSE", rmse_fn, "lower"),
        ("SD", sd_fn, "lower"),
        ("Slope", slope_fn, "none"),
    ]

    rows = []
    print(f"{'metric':<14} {'delta':>8} {'95% CI':>22}  exclude0  p-value   better")
    print("-" * 80)

    for name, fn, direction in metrics:
        deltas = np.full(N_BOOT, np.nan)
        for b in range(N_BOOT):
            idx = rng.integers(0, n, n)
            d_test = fn(exp_test[idx], calc_test[idx])
            d_base = fn(exp_base[idx], calc_base[idx])
            deltas[b] = d_test - d_base

        valid = deltas[~np.isnan(deltas)]
        point = fn(exp_test, calc_test) - fn(exp_base, calc_base)
        lo, hi = np.percentile(valid, [lo_pct, hi_pct]) if len(valid) else (np.nan, np.nan)
        exclude0 = (lo > 0) or (hi < 0) if not np.isnan(lo) else False

        if len(valid) > 0 and not np.isnan(point):
            if point >= 0:
                p_boot = 2 * np.mean(valid <= 0)
            else:
                p_boot = 2 * np.mean(valid >= 0)
            p_boot = min(p_boot, 1.0)
        else:
            p_boot = np.nan

        if direction == "higher":
            better = "TEST" if (exclude0 and point > 0) else ("BASE" if (exclude0 and point < 0) else "ns")
        elif direction == "lower":
            better = "TEST" if (exclude0 and point < 0) else ("BASE" if (exclude0 and point > 0) else "ns")
        else:
            better = "-"

        print(f"{name:<14} {point:8.3f}   [{lo:7.3f}, {hi:7.3f}]  {str(exclude0):<8}  {p_boot:7.4f}  {better}")
        rows.append({
            "metric": name,
            "delta_TEST_minus_BASE": point,
            "ci_low": lo,
            "ci_high": hi,
            "excludes_zero": exclude0,
            "p_value": p_boot,
            "resolved_better": better,
        })

    out_csv = f"paired_{label}.csv"
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    print(f"Saved: {out_csv}")

# -----------------------------
# Run
# -----------------------------
for csv_file in csv_files:
    if os.path.exists(csv_file):
        process_file(csv_file)
    else:
        print(f"WARNING: File not found, skipping: {csv_file}")

for test_csv, base_csv, label in PAIRS:
    if os.path.exists(test_csv) and os.path.exists(base_csv):
        try:
            paired_bootstrap(test_csv, base_csv, label)
        except Exception as e:
            print(f"Paired analysis failed for {label}: {e}")
    else:
        print(f"Skipping paired {label}: one or both files missing")

print("\nAll done.")