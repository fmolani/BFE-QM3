
<img width="661" height="140" alt="Capture" src="https://github.com/user-attachments/assets/a16201fd-8905-433e-b14c-cf56c70f86f8" />
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


## Usage

Detailed instructions for executing the complete BFE-QM3 workflow are available in:

`src/README.md`



<img width="628" height="520" alt="image" src="https://github.com/user-attachments/assets/e861f196-0161-4b49-8dda-d0fadf020a4f" />

