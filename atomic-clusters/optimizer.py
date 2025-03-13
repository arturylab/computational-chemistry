# Script to optimize atomic structures from an XYZ file using the Gupta potential
import argparse
import scipy.optimize as spo
from autograd import elementwise_grad as egrad
from potentials.gupta import Gupta
from read_xyz import read_xyz_file
from write_xyz import write_xyz_file

def optimize_structure(file_path):
    """Optimize the atomic structure from an XYZ file using the Gupta potential.
    
    Args:
        file_path (str): Path to the input XYZ file.
    
    Returns:
        None: Saves the optimized structure to a new XYZ file.
    """
    atoms, coords = read_xyz_file(file_path)
    
    gupta = Gupta(atoms)
    potential = lambda x: gupta.potential(x.reshape(len(coords), 3))
    
    sol = spo.minimize(
        potential,
        coords.flatten(),
        method='L-BFGS-B',
        jac=egrad(potential),
        options={
            "gtol": 1e-8,
            "maxiter": 1000,
            "disp": False,
        })
    
    new_coords = sol.x.reshape(-1, 3)
    energy = sol.fun
    
    output_file = f"opt-{file_path.split('/')[-1]}"
    write_xyz_file(output_file, atoms, new_coords, energy)
    
    print(f"Optimization complete. Output saved to {output_file}")

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Optimize atomic structure from an XYZ file.")
        parser.add_argument("file", type=str, help="Path to the XYZ file.")
        args = parser.parse_args()
        
        if not args.file:
            raise ValueError("No file path provided. Please specify the path to an XYZ file.")
        
        optimize_structure(args.file)
    except Exception as e:
        print(f"Error: {e}")
