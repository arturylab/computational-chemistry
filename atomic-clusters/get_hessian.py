# Script to compute the Hessian of an atomic structure using the Gupta potential
import argparse
from potentials.gupta import Gupta
from read_xyz import read_xyz_file

def compute_hessian(file_path):
    """Compute the Hessian Matrix of an atomic structure using the Gupta potential.
    
    Args:
        file_path (str): Path to the input XYZ file.
    
    Returns:
        None: Prints the Hessian Matrix.
    """
    atoms, coords = read_xyz_file(file_path)
    gupta = Gupta(atoms)
    hessian = gupta.hessian(coords)
    print("Hessian Matrix:")
    print(hessian)

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Compute the Hessian of an atomic structure from an XYZ file.")
        parser.add_argument("file", type=str, help="Path to the XYZ file.")
        args = parser.parse_args()
        
        if not args.file:
            raise ValueError("No file path provided. Please specify the path to an XYZ file.")
        
        compute_hessian(args.file)
    except Exception as e:
        print(f"Error: {e}")
