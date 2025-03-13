# Script to compute the gradient (force) of an atomic structure using the Gupta potential
import argparse
import numpy as np
from potentials.gupta import Gupta
from read_xyz import read_xyz_file

def compute_gradient(file_path, norm):
    """Compute the gradient (force) of an atomic structure using the Gupta potential.
    
    Args:
        file_path (str): Path to the input XYZ file.
        norm (bool): If True, prints the norm of the gradient instead of the full matrix.
    
    Returns:
        None: Prints the gradient information.
    """
    atoms, coords = read_xyz_file(file_path)
    gupta = Gupta(atoms)
    
    gradient = gupta.gradient(coords)
    
    if norm:
        grad_norm = np.linalg.norm(gradient)
        print(f"Gradient Norm: {grad_norm:.6f}")
    else:
        print("Gradient Matrix:")
        print(gradient)

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Compute the gradient (force) of an atomic structure from an XYZ file.")
        parser.add_argument("file", type=str, help="Path to the XYZ file.")
        parser.add_argument("--norm", action="store_true", help="Print only the norm of the gradient instead of the full matrix.")
        args = parser.parse_args()
        
        if not args.file:
            raise ValueError("No file path provided. Please specify the path to an XYZ file.")
        
        compute_gradient(args.file, args.norm)
    except Exception as e:
        print(f"Error: {e}")
