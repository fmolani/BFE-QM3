#!/usr/bin/env python
"""
Summary report for all result_scaling.csv files.

For every target folder it reports:
  1. The scaling factor (a) that gives the LOWEST MAE
     ? corresponding slope, average_offset, correlation
  2. The scaling factor (a) whose slope is CLOSEST to 1.0
     ? corresponding MAE, correlation, average_offset
  3. The results for a = 0.50 (exact)
  4. The results for a = 1.00 (exact)
"""

from pathlib import Path
import pandas as pd
import numpy as np

# -------------------------------------------------
# Root directory
# -------------------------------------------------
root_dir = Path(".")          # change if needed
# root_dir = Path("/path/to/parent/folder")

# Find every result_scaling.csv
csv_files = list(root_dir.rglob("result_scaling.csv"))

if not csv_files:
    print("No 'result_scaling.csv' files found.")
    exit()

print(f"Found {len(csv_files)} result_scaling.csv file(s).\n")

summary_rows = []

for csv_path in sorted(csv_files):
    folder = csv_path.parent
    try:
        df = pd.read_csv(csv_path)

        # -------------------------------------------------
        # 1. Lowest MAE
        # -------------------------------------------------
        idx_mae = df["MAE"].idxmin()
        best_mae = df.loc[idx_mae]

        # -------------------------------------------------
        # 2. Slope closest to 1.0
        # -------------------------------------------------
        idx_slope = (df["slope"] - 1.0).abs().idxmin()
        best_slope = df.loc[idx_slope]

        # -------------------------------------------------
        # 3. Exact a = 0.50
        # -------------------------------------------------
        row_050 = df.loc[df["a"].round(2) == 0.50]
        if len(row_050) == 0:
            idx_050 = (df["a"] - 0.50).abs().idxmin()
            a050 = df.loc[idx_050]
            a050_note = f"(closest a={a050['a']:.2f})"
        else:
            a050 = row_050.iloc[0]
            a050_note = ""

        # -------------------------------------------------
        # 4. Exact a = 1.00
        # -------------------------------------------------
        row_100 = df.loc[df["a"].round(2) == 1.00]
        if len(row_100) == 0:
            idx_100 = (df["a"] - 1.00).abs().idxmin()
            a100 = df.loc[idx_100]
            a100_note = f"(closest a={a100['a']:.2f})"
        else:
            a100 = row_100.iloc[0]
            a100_note = ""

        # Collect for global summary
        summary_rows.append({
            "folder": str(folder),
            # lowest MAE
            "best_MAE_a":           best_mae["a"],
            "best_MAE":             best_mae["MAE"],
            "best_MAE_slope":       best_mae["slope"],
            "best_MAE_offset":      best_mae["average_offset"],
            "best_MAE_correlation": best_mae["correlation"],
            # slope closest to 1
            "slope1_a":             best_slope["a"],
            "slope1_value":         best_slope["slope"],
            "slope1_MAE":           best_slope["MAE"],
            "slope1_offset":        best_slope["average_offset"],
            "slope1_correlation":   best_slope["correlation"],
            # a = 0.50
            "a050_MAE":             a050["MAE"],
            "a050_slope":           a050["slope"],
            "a050_offset":          a050["average_offset"],
            "a050_correlation":     a050["correlation"],
            # a = 1.00
            "a100_MAE":             a100["MAE"],
            "a100_slope":           a100["slope"],
            "a100_offset":          a100["average_offset"],
            "a100_correlation":     a100["correlation"],
        })

        # Pretty print for this folder
        print("=" * 70)
        print(f"Folder : {folder}")
        print("-" * 70)

        print("LOWEST MAE")
        print(f"  a               = {best_mae['a']:.2f}")
        print(f"  MAE             = {best_mae['MAE']:.2f}")
        print(f"  slope           = {best_mae['slope']:.2f}")
        print(f"  average_offset  = {best_mae['average_offset']:.2f}")
        print(f"  correlation     = {best_mae['correlation']:.2f}")
        print()

        print("SLOPE CLOSEST TO 1.0")
        print(f"  a               = {best_slope['a']:.2f}")
        print(f"  slope           = {best_slope['slope']:.2f}")
        print(f"  MAE             = {best_slope['MAE']:.2f}")
        print(f"  average_offset  = {best_slope['average_offset']:.2f}")
        print(f"  correlation     = {best_slope['correlation']:.2f}")
        print()

        print(f"a = 0.50  {a050_note}")
        print(f"  MAE             = {a050['MAE']:.2f}")
        print(f"  slope           = {a050['slope']:.2f}")
        print(f"  average_offset  = {a050['average_offset']:.2f}")
        print(f"  correlation     = {a050['correlation']:.2f}")
        print()

        print(f"a = 1.00  {a100_note}")
        print(f"  MAE             = {a100['MAE']:.2f}")
        print(f"  slope           = {a100['slope']:.2f}")
        print(f"  average_offset  = {a100['average_offset']:.2f}")
        print(f"  correlation     = {a100['correlation']:.2f}")
        print()

    except Exception as e:
        print(f"Error processing {csv_path}: {e}")

# -------------------------------------------------
# Global summary table
# -------------------------------------------------
if summary_rows:
    summary_df = pd.DataFrame(summary_rows)

    # Save CSV
    out_csv = root_dir / "summary_report.csv"
    summary_df.to_csv(out_csv, index=False, float_format="%.2f")
    print("=" * 70)
    print(f"Global summary saved to: {out_csv}")

    # Save readable text
    out_txt = root_dir / "summary_report.txt"
    with open(out_txt, "w") as f:
        f.write("SUMMARY REPORT  lowest MAE / slope 1.0 / a=0.50 / a=1.00\n")
        f.write("=" * 70 + "\n\n")
        f.write(summary_df.to_string(index=False, float_format="%.2f"))
        f.write("\n")
    print(f"Readable text report saved to: {out_txt}")

print("\nAll done.")