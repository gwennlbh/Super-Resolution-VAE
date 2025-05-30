import os
import time

import torch
from matplotlib import pyplot as plt

from model import Cond_SRVAE


def test(device, model: Cond_SRVAE, val_loader):
    """
    Test the model on the validation set and compute error maps for a given image.
    Args:
        model (torch.nn.Module): The trained model.
        val_loader (DataLoader): DataLoader for the validation set
    """
    slurm_job_id = os.environ.get(
        "SLURM_JOB_ID", f"local_{time.strftime('%Y%m%D-%H%M%S')}"
    )
    os.makedirs(slurm_job_id, exist_ok=True)
    model.eval()
    batch = next(iter(val_loader))
    y, x = batch
    y, x = y[0:1, :, :, :].to(device), x[0:1, :, :, :].to(device)

    with torch.no_grad():
        samples = model.sample(y, samples=1000)

    # Compute error map of samples and GT x
    diff = (samples - x).mean(dim=1)
    error_map = diff.cpu().numpy().mean(axis=0)
    plt.figure(figsize=(10, 10))
    plt.subplot(2, 3, 1)
    plt.imshow(y[0, [2, 1, 0], :, :].cpu().numpy().transpose(1, 2, 0))
    plt.title("Input Image")
    plt.subplot(2, 3, 2)
    plt.imshow(samples[0, [2, 1, 0], :, :].cpu().numpy().transpose(1, 2, 0))
    plt.title("Sampled Image")
    plt.subplot(2, 3, 3)
    plt.imshow(x[0, [2, 1, 0], :, :].cpu().numpy().transpose(1, 2, 0))
    plt.title("Ground Truth Image")
    plt.subplot(2, 3, 4)
    plt.imshow(error_map, cmap="hot")
    plt.colorbar()
    plt.title("Error Map")
    plt.subplot(2, 3, 5)
    var = samples.std(dim=0).mean(dim=0).cpu().numpy()
    plt.imshow(var, cmap="hot")
    plt.colorbar()
    plt.title(f"Std Map, Mean: {var.mean():.2f}")
    plt.savefig(f"{slurm_job_id}/variance_map_with_title.png", bbox_inches="tight")
    plt.close()

    MMSE = (samples - x).pow(2).mean()
    print(f"MMSE: {MMSE:.4f}")

    plt.figure(figsize=(10, 10))
    with torch.no_grad():
        y_gen, x_gen = model.generation()
    plt.subplot(2, 1, 1)
    plt.imshow(y_gen[0, [2, 1, 0], :, :].detach().cpu().numpy().transpose(1, 2, 0))
    plt.title("Generated Image")
    plt.subplot(2, 1, 2)
    plt.imshow(x_gen[0, [2, 1, 0], :, :].detach().cpu().numpy().transpose(1, 2, 0))
    plt.title("Generated Image from x")
    plt.savefig(f"{slurm_job_id}/generated_image.png", bbox_inches="tight")
    plt.close()
