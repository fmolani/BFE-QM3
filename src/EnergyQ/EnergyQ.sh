#!/bin/bash
#SBATCH -p QML_server
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:0
#SBATCH --cpus-per-task=64
#SBATCH --time=36:00:00
#SBATCH -J inVQE
#SBATCH -o outName.o%j
source /home/fmolani/.bashrc
conda activate inVQE
python Qenergy_1.py
python Qenergy_2.py



