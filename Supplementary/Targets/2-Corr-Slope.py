import os
from pathlib import Path
import pandas as pd
import numpy as np
from scipy.stats import linregress

# -------------------------------------------------
# Root directory that contains all the folders
# -------------------------------------------------
root_dir = Path(".")          # change if needed
# root_dir = Path("/path/to/parent/folder")

# Scaling factors: 0.1, 0.2, ..., 2.0
a_values = np.round(np.arange(0.1, 2.01, 0.005), 20)

# Find every target CSV
csv_files = list(root_dir.rglob("output_QM3_scaled_offset.csv"))

if not csv_files:
    print("No 'output_QM3_scaled_offset.csv' files found.")
    exit()

print(f"Found {len(csv_files)} file(s). Processing all scaling factors...\n")

for csv_path in csv_files:
    folder = csv_path.parent
    print(f"Processing: {folder}")

    try:
        # Load data once
        df = pd.read_csv(csv_path)
        exp  = df.iloc[:, 0].to_numpy(dtype=float)
        pred = df.iloc[:, 1].to_numpy(dtype=float)

        results = []

        for a in a_values:
            # Scale
            scaled = a * pred

            # Offset
            diff = scaled - exp
            average_offset = np.mean(diff)
            scaled_offset = scaled - average_offset

            # Metrics
            correlation = np.corrcoef(exp, scaled_offset)[0, 1]
            mae = np.mean(np.abs(exp - scaled_offset))
            slope, _, _, _, _ = linregress(exp, scaled_offset)

            results.append({
                "a": a,
                "average_offset": average_offset,
                "correlation": correlation,
                "MAE": mae,
                "slope": slope
            })

        # Create DataFrame
        res_df = pd.DataFrame(results)

        # ----- Save as CSV (easy to open in Excel / further analysis) -----
        csv_out = folder / "result_scaling.csv"
        res_df.to_csv(csv_out, index=False, float_format="%.6f")

        # ----- Save as readable text file -----
        txt_out = folder / "result_scaling.txt"
        with open(txt_out, "w") as f:
            f.write(f"Folder : {folder}\n")
            f.write(f"CSV    : {csv_path.name}\n")
            f.write("=" * 70 + "\n\n")
            f.write(res_df.to_string(index=False, float_format="%.6f"))
            f.write("\n")

        print(f"saved: {csv_out.name}  and  {txt_out.name}")

    except Exception as e:
        print(f"Error: {e}")

print("\nAll done.")