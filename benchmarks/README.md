**Copy this into your README.md**

```markdown
# BFE-QM3

Quantum-ready hybrid framework for protein–ligand binding free-energy prediction  
(BFE-QM3 = Binding Free Energy with QM-derived charges, Mining Minima, and QM/MM-VQE).

## Repository structure

```
Supplementary//
├── targets/                  # one folder per benchmark target
│   ├── HIV1_protease/
│   │   ├── output_MM_scaled_offset.csv
│   │   ├── output_QMFF_scaled_offset.csv
│   │   └── output_QM3_scaled_offset.csv
│   ├── BACE/
│   ├── CDK2/
│   └── … (all 23 targets)
├── 1-Statistics-overall.py
├── 2-Corr-Slope.py
├── 3-Corr-Slope-Report.py
├── 4-Uncalibrated.py
├── stacked_MMVM2.csv
├── stacked_QMFF.csv
├── stacked_QM3.csv
└── README.md
```

## Contents of each target folder

- `output_MM_scaled_offset.csv` – target-mean-aligned MM-VM2 predictions  
- `output_QMFF_scaled_offset.csv` – target-mean-aligned QMFF-VM2 predictions  
- `output_QM3_scaled_offset.csv` – target-mean-aligned BFE-QM3 predictions  

All files contain stable ligand identifiers and experimental affinities.

```
