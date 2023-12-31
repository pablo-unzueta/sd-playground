# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_basis.ipynb.

# %% auto 0
__all__ = ['GaussianSmearing', 'bessel_features', 'GaussianRandomFourierFeatures']

# %% ../nbs/01_basis.ipynb 3
import torch

# %% ../nbs/01_basis.ipynb 4
class GaussianSmearing(torch.nn.Module):
    """
    Convert Scalar distances into Gaussian basis functions
    """
    def __init__(self, 
                 start=0.0, # Start of Gaussian basis functions
                 stop=1.0, # stop of the Gaussian basis functions
                 num_basis=8 # Number of Gaussian basis functions
                 ):
        super().__init__()
        offset = torch.linspace(start, stop, num_basis)
        self.coeff = -0.5 / torch.pow((offset[1] - offset[0]), 2)
        self.register_buffer('offset', offset) # Register offset as a buffer. This is a tensor that is not a parameter

    def forward(self, 
                distances # Tensor of distances
                ):
        distances = distances[..., None] - self.offset # This operation aligns the distances with each Gaussian center.
        return torch.exp(self.coeff * torch.pow(distances, 2))

# %% ../nbs/01_basis.ipynb 10
def bessel_features(distances, # Torch tensor of distances
                    start=0.0,
                    stop=1.0,
                    eps=1e-5,
                    num_basis=4 # Number of Bessel basis functions
                    ):
    """
    Convert Scalar distances into Bessel basis functions
    """
    distances = distances[..., None] - start + eps
    c = stop - start
    bessel_roots = torch.arange(1, num_basis + 1) * torch.pi 
    return (2/c)**0.5 * torch.sin(bessel_roots * distances / c) / distances

# %% ../nbs/01_basis.ipynb 12
class GaussianRandomFourierFeatures(torch.nn.Module):
    """Gaussian random Fourier features from the paper titled
    'Fourier Features Let Networks Learn High Frequency Functions in Low Dimensional Domains'.
    Reference: https://arxiv.org/abs/2006.10739
    """
    def __init__(self, 
                 embed_dim, # Embedding dimension. B gets cut in half because GRFF is a concat of cos and sin
                 input_dim=1, # Input dimension
                 sigma=1.0 # variance
                 ):
        super().__init__()
        # Randomly sample weights during initialization. These weights are fixed
        # during optimization and are not trainable.
        self.B = torch.nn.Parameter(torch.randn(input_dim, embed_dim//2) * sigma, requires_grad=False)
    def forward(self, v):
        v_proj =  2 * torch.pi * v * self.B
        return torch.cat([torch.cos(v_proj), torch.sin(v_proj)], dim=-1)
