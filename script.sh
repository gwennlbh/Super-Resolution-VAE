#!/bin/sh

#SBATCH --nodes=1
#SBATCH --time=3-00:00:00
#SBATCH --job-name=Conditionnal_VAE
#SBATCH -o ./slurm_logs/slurm.%j.out # STDOUT
#SBATCH -e ./slurm_logs/slurm.%j.err # STDERR
#SBATCH --partition=gpu02
#SBATCH --nodelist=gpu02
#SBATCH --gres=gpu:1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=6

module load python/3.8

source activate vae-rs

export SCRATCH="/scratch/disc/e.bardet/"

python train.py --patch_size 256 --batch_size 4 --pre_epochs 0 --val_metrics_every 10
