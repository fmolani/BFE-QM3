
# BFE-QM3: Hybrid Quantum-Classical Framework for Scalable Protein–Ligand Binding Free Energy Prediction
<img width="975" height="187" alt="image" src="https://github.com/user-attachments/assets/137c8e16-1ce9-47fd-95bc-9bb0505dfdc3" />
<img width="1372" height="439" alt="image" src="https://github.com/user-attachments/assets/23bebed6-125c-4b56-8e29-c3aa2d387c98" />

# BFE-QM3
Accurate free-energy estimation in high-dimensional molecular systems remains a fundamental challenge in computational statistical mechanics, as conventional alchemical methods demand extensive sampling and electronic-structure approaches are prohibitively expensive at scale. Here we introduce a hybrid computational framework that decouples configurational entropy estimation from electronic-structure refinement within a unified free-energy reconstruction scheme. By separating large-scale configurational sampling from quantum-mechanical energy correction, the method enables scalable multiscale free-energy prediction while preserving electronic fidelity. We benchmark the approach across 23 structurally diverse protein–ligand systems comprising 543 ligands and multiple target classes. The framework consistently recovers experimental rank ordering with accuracy comparable to established alchemical free-energy methods, while substantially reducing computational cost. The entropy–electronic separation provides a physically interpretable route to integrating statistical mechanics with quantum corrections and is compatible with variational quantum eigensolver architectures. More broadly, this decoupled reconstruction strategy offers a general paradigm for free-energy estimation in complex molecular systems, including biomolecular recognition, supramolecular assembly, and materials binding, suggesting a scalable pathway toward quantum-compatible molecular simulation frameworks.

We introduce BFE-QM3 (read BFE-QM “cubed”), a computational framework that explicitly decouples configurational entropy from electronic-structure refinement. It is devised as a refined Binding Free-Energy workflow that integrates Quantum-Mechanically derived ESP ligand charges, Mining-Minima–based thermodynamic sampling, and interaction energy corrections evaluated using a QM/MM framework augmented by VQE calculations. The central idea is to treat the configurational ensemble using statistical thermodynamics over representative minima, while applying quantum-mechanical corrections only where they are most informative at the level of interaction energies within localized binding environments. This separation allows electronic accuracy to be introduced in a controlled and scalable manner, without requiring quantum-level evaluation of the full configurational space. 

## Requirements

The workflow has been tested with the following software:

- NumPy
- SciPy
- PySCF
- OpenMM
- Tangelo 0.4.3

In addition, the VM2 workflow and its associated external dependencies (https://www.verachem.com/) should be installed and configured according to the corresponding software documentation.


---

## Algorithmic Details & Computational Parameters

### 1. QM Charge Derivation (QMFF)

**Method:** HF/ma-def2-SVP + ddCOSMO (water)

**Software:** PySCF

#### RESP Charge Fitting

| Parameter | Value |
|-----------|---------|
| Probe radius | 0.7 Å |
| α (non-H atoms) | 0.001 au |
| β (non-H atoms) | 0.1 au |
| Maximum iterations | 25 |
| Convergence threshold | 1.0 × 10⁻⁴ electrons |

---

### 2. Classical Minima Mining (MM-VM2)

#### Search Algorithms

- Rigid-body translation/rotation search
- Mode distort-minimize search

#### Solvation

| Stage | Model |
|---------|---------|
| Minima search | Generalized Born (GB) |
| Final evaluation | Poisson-Boltzmann Surface Area (PBSA) |

#### Dielectric Constants

- Protein: 1
- Solvent: 80

#### Flexible Regions

- Live set: Ligand + residues within 4 Å
- Real set: Atoms within 6 Å of the live region

#### Entropy

- Harmonic approximation
- Mode scanning

---

### 3. Hybrid QM/MM + VQE Refinement

#### Ligand VQE

| Parameter | Value |
|-----------|---------|
| Quantum emulator | 10 qubits |
| Active electrons | 6 |
| Basis | MINAO |
| Ansatz | UCCSD |
| Mapping | Symmetry-conserving Bravyi-Kitaev (scBK) |
| Optimizer | SLSQP |

#### QM/MM Complex

| Parameter | Value |
|-----------|---------|
| QM method | B3LYP-D4 |
| QM basis | def2-SVPD |
| RI approximation | RI-DFT (def2-universal-jfit) |
| MM force field | ff99SB point charges |
| QM/MM embedding | Electrostatic embedding |
| MM cutoff | Residues within 8.0 Å of ligand |

#### Scaling Factors

- QM correction scaling factor (α): 1.59 × 10⁻³
- Universal Scaling Factor (USF): 0.50

---

### 4. Free Energy Expression

The final binding free energy combines the classical VM2 free-energy estimate with the QM/MM-VQE correction term.

For the complete mathematical formulation of ΔG, ΔU, ΔW, and the QM correction term, please refer to Equations (1)–(6) of the accompanying manuscript.


## How to Run

The complete BFE-QM3 workflow consists of four sequential stages. Before starting, ensure that all required dependencies are installed and that the input files are located in the appropriate directories.

### Step 1: System Preparation

Navigate to the `System` directory and execute:

```bash
bash vc_workflow_1_setup.sh
bash vc_workflow_2_ligconfs.sh
```

### Step 2: ESP Charge Calculation (ChargeQ)

Navigate to the `ChargeQ` directory and run:

```bash
python ChargeQ_1.py
python ChargeQ_2.py
```

### Step 3: VM2 Workflow Execution

Return to the `System` directory and execute:

```bash
bash vc_workflow_3_genrundirs.sh
bash vc_workflow_4_run.sh
bash vc_workflow_5_extract_results.sh
```

### Step 4: QM/MM-VQE Energy Refinement (EnergyQ)

Navigate to the `EnergyQ` directory and run:

```bash
python EnergyQ_1.py
python EnergyQ_2.py
```

The final output of the workflow is the QM/MM-refined binding free energy prediction generated by the EnergyQ module.




<img width="471" height="394" alt="image" src="https://github.com/user-attachments/assets/aea5c48c-98a4-42fb-a7cc-37633becdbb1" />

## How to Cite

If you use **BFE-QM3** in your research, please cite:

```bibtex
@article{molani2026bfeqm3,
  title   = {A hybrid computational framework decoupling configurational entropy and electronic-structure refinement for scalable multiscale free-energy prediction},
  author  = {Molani, Farzad and Cho, Art E.},
  journal = {arXiv preprint arXiv:2512.06141},
  year    = {2026},
  url     = {https://arxiv.org/abs/2512.06141}
}
```

**Preprint:**

https://arxiv.org/abs/2512.06141


