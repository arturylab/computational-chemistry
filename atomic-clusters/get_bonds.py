import argparse
import numpy as np
from read_xyz import read_xyz_file

def compute_distances(file_path):
    """Compute the interatomic distances (links) between all pairs of atoms in the XYZ file.
    
    Args:
        file_path (str): Path to the input XYZ file.
    
    Returns:
        None: Prints the computed distances in Angstroms for all atom pairs (links).
    """
    atoms, coords = read_xyz_file(file_path)
    
    # Convert coordinates to numpy array
    coords = np.array(coords)
    
    # Number of atoms
    num_atoms = len(atoms)
    
    # Calculate the distance between two coordinates (atoms)
    def distance(coord1, coord2):
        return np.linalg.norm(np.array(coord1) - np.array(coord2))
    
    # Create the pairwise distance matrix (links) using manual calculation
    pairwise_distances = np.array([[distance(coords[i], coords[j]) for j in range(num_atoms) if i != j] for i in range(num_atoms)])
    
    valid_bond = 2.513
    # Find distances that are less than or equal to valid_bond Å
    valid_distances = [(i, j, pairwise_distances[i, j - 1]) for i in range(num_atoms) for j in range(i + 1, num_atoms)
                        if pairwise_distances[i, j - 1] <= valid_bond]
    
    # Print the distances if any valid pairs exist
    if valid_distances:
        print("Bond distances in Angstroms (Å):")
        pair_number = 1
        for i, j, dist in valid_distances:
            atom_i = atoms[i]
            atom_j = atoms[j]
            print(f"{pair_number}. {atom_i}-{atom_j}: {dist:.6f}")
            pair_number += 1

        # Compute the average distance of valid pairs
        average_distance = np.mean([dist for _, _, dist in valid_distances])
        print(f"\nAverage bond distance: {average_distance:.6f} Å")
    else:
        print("No bond distances below or equal to valid_bond Å were found.")

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Compute interatomic distances (links) from an XYZ file.")
        parser.add_argument("file", type=str, help="Path to the XYZ file.")
        args = parser.parse_args()
        
        if not args.file:
            raise ValueError("No file path provided. Please specify the path to an XYZ file.")
        
        compute_distances(args.file)
    except Exception as e:
        print(f"Error: {e}")
