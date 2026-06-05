
# BFE-QM3: Hybrid Quantum-Classical Framework for Scalable Protein–Ligand Binding Free Energy Prediction
<img width="975" height="187" alt="image" src="https://github.com/user-attachments/assets/137c8e16-1ce9-47fd-95bc-9bb0505dfdc3" />
<img width="1372" height="439" alt="image" src="https://github.com/user-attachments/assets/23bebed6-125c-4b56-8e29-c3aa2d387c98" />

# BFE-QM3
Accurate free-energy estimation in high-dimensional molecular systems remains a fundamental challenge in computational statistical mechanics, as conventional alchemical methods demand extensive sampling and electronic-structure approaches are prohibitively expensive at scale. Here we introduce a hybrid computational framework that decouples configurational entropy estimation from electronic-structure refinement within a unified free-energy reconstruction scheme. By separating large-scale configurational sampling from quantum-mechanical energy correction, the method enables scalable multiscale free-energy prediction while preserving electronic fidelity. We benchmark the approach across 23 structurally diverse protein–ligand systems comprising 543 ligands and multiple target classes. The framework consistently recovers experimental rank ordering with accuracy comparable to established alchemical free-energy methods, while substantially reducing computational cost. The entropy–electronic separation provides a physically interpretable route to integrating statistical mechanics with quantum corrections and is compatible with variational quantum eigensolver architectures. More broadly, this decoupled reconstruction strategy offers a general paradigm for free-energy estimation in complex molecular systems, including biomolecular recognition, supramolecular assembly, and materials binding, suggesting a scalable pathway toward quantum-compatible molecular simulation frameworks.

We introduce BFE-QM3 (read BFE-QM “cubed”), a computational framework that explicitly decouples configurational entropy from electronic-structure refinement. It is devised as a refined Binding Free-Energy workflow that integrates Quantum-Mechanically derived ESP ligand charges, Mining-Minima–based thermodynamic sampling, and interaction energy corrections evaluated using a QM/MM framework augmented by VQE calculations. The central idea is to treat the configurational ensemble using statistical thermodynamics over representative minima, while applying quantum-mechanical corrections only where they are most informative at the level of interaction energies within localized binding environments. This separation allows electronic accuracy to be introduced in a controlled and scalable manner, without requiring quantum-level evaluation of the full configurational space. 

#Key Features

Decoupled entropy–electronic workflow
QM-derived ESP (RESP) ligand charges (QMFF)
Classical Mining Minima (MM-VM2) thermodynamic sampling
Hybrid QM/MM + Variational Quantum Eigensolver (VQE) interaction energy refinement
Universal Scaling Factor (USF) for final ΔG values
Modular design — easily swap classical QM/MM with future quantum solvers


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

## Usage

Detailed instructions for executing the complete BFE-QM3 workflow are available in:

`src/README.md`



<img width="471" height="394" alt="image" src="https://github.com/user-attachments/assets/aea5c48c-98a4-42fb-a7cc-37633becdbb1" />

