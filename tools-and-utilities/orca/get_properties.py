'''
Script Description:
This script processes ORCA quantum chemistry output files to extract various properties such as 
energy, magnetic moment, vibrational frequencies, HOMO-LUMO gap, and average interatomic distances. 
It also generates XYZ files containing atomic coordinates and appends the extracted data to a CSV file.

Functions:
- main(): Parses command-line arguments, processes the ORCA output file, and saves results to a CSV file.
- get_energy(content: str) -> float: Extracts the final single point energy value from the ORCA output file content.
- get_magnetic(content: str) -> float: Extracts the magnetic spin population value from the ORCA output file content.
- get_frequencies(content: str) -> int: Counts the number of imaginary vibrational modes in the ORCA output file content.
- get_gap(content: str) -> tuple[float, float, float]: Extracts HOMO, LUMO, and HOMO-LUMO gap from the ORCA output file content.
- write_xyz(content: str) -> None: Extracts Cartesian coordinates from the ORCA output file and writes them to a new .xyz file.
- read_xyz(path: str) -> tuple[list[str], np.ndarray]: Reads an XYZ file and returns atom types and coordinates.
- get_distances() -> float: Calculates the average interatomic distance for valid bonds in the XYZ file.

Usage:
Run the script from the command line, providing the path to an ORCA output file as an argument:
    python get_properties.py <path_to_orca_output_file>
'''

import argparse
import os
import numpy as np
import pandas as pd


def main():
    parser = argparse.ArgumentParser(description="Process ORCA output file.")
    parser.add_argument("file", type=str, help="Path to the ORCA output file")
    
    # Parse the command-line arguments
    args = parser.parse_args()

    # Get the file path from the parsed arguments
    file = args.file
    # Open the specified ORCA output file and read its content
    with open(file, "r") as f:
        content = f.read().strip()
    
    # Extract Cartesian coordinates and write them to a new .xyz file
    write_xyz(content)
    
    # Extract data
    energy = get_energy(content)
    magnetic_moment = get_magnetic(content)
    frequencies = get_frequencies(content)
    homo, lumo, gap = get_gap(content)
    avg_distance = get_distances()

    # Create a DataFrame
    data = {
        "filename": [os.path.basename(file)],
        "energy": [energy],
        "mag moment": [magnetic_moment],
        "freq": [frequencies],
        "homo": [homo],
        "lumo": [lumo],
        "gap": [gap],
        "avg dist": [avg_distance],
    }
    df = pd.DataFrame(data)

    # Save to CSV
    output_csv = "results.csv"
    if not os.path.exists(output_csv):
        df.to_csv(output_csv, index=False)
    else:
        df.to_csv(output_csv, mode='a', header=False, index=False)

def get_energy(content: str) -> float:
    """
    Extracts the final single point energy value from the given content.

    This function searches for the phrase "FINAL SINGLE POINT ENERGY" in the 
    provided content string. If found, it retrieves the energy value from the 
    corresponding line. The energy value is expected to be the last element 
    on the line containing the phrase.

    Args:
        content (str): The content of a file or string to search for the energy value,
        typically from an ORCA output file.
    Returns:
        float: The extracted energy value if the phrase is found, otherwise None.
    """

    word = "FINAL SINGLE POINT ENERGY"

    if word in content:
        lines = content.splitlines()
        for i in range(len(lines) -1, -1, -1):
            if word in lines[i]:
                energy = lines[i].split()[-1]
                return energy
    else:
        return None

def get_magnetic(content: str) -> float:
    """
    Extracts the magnetic spin population value from the given content.
    
    This function searches for the phrase "Sum of atomic spin populations" 
    in the provided content string. If found, it retrieves the last value 
    on the corresponding line, which represents the spin population.
    
    Args:
        content (str): The content string to search for the spin population,
        typically from an ORCA output file.
    Returns:
        float: The extracted spin population value if the phrase is found, 
               otherwise None.
    """
     
    word = "Sum of atomic spin populations"

    if word in content:
        lines = content.splitlines()
        for i in range(len(lines) -1, -1, -1):
            if word in lines[i]:
                spin_popluation = lines[i].split()[-1]
                return spin_popluation
    else:
        return None
     
def get_frequencies(content: str) -> int:
    """
    Analyzes the provided content to determine the number of imaginary vibrational modes.

    This function searches for the presence of the phrase "VIBRATIONAL FREQUENCIES" 
    in the given content. If found, it counts the occurrences of the phrase 
    "***imaginary mode***" to determine the number of imaginary vibrational modes.

    Args:
        content (str): The text content to analyze, typically from an ORCA output file.
    Returns:
        int: The number of imaginary vibrational modes if "VIBRATIONAL FREQUENCIES" 
             is found in the content; otherwise, None.
    """

    word = "VIBRATIONAL FREQUENCIES"

    if word in content:
        lines = content.splitlines()
        for i in range(len(lines) -1, -1, -1):
            if word in lines[i]:
                imaginary_counts = content.count("***imaginary mode***")
                return imaginary_counts
    else:
        return None
    
def get_gap(content: str) -> tuple[float, float, float]:
    """
    Extracts the HOMO (Highest Occupied Molecular Orbital) energy, 
    LUMO (Lowest Unoccupied Molecular Orbital) energy, and the 
    HOMO-LUMO gap from the given content.
    
    The function searches for the "SPIN DOWN ORBITALS" section in the 
    provided content, identifies the number of orbitals, and calculates 
    the HOMO and LUMO energies. The HOMO-LUMO gap is computed as the 
    absolute difference between the HOMO and LUMO energies.
    
    Args:
        content (str): The input string containing the molecular orbital 
                       data, typically from an ORCA output file.
    Returns:
        tuple[float, float, float]: A tuple containing:
            - HOMO (float): The energy of the highest occupied molecular orbital.
            - LUMO (float): The energy of the lowest unoccupied molecular orbital.
            - gap (float): The HOMO-LUMO gap.
    Raises:
        ValueError: If the required data is not found in the content or 
                    if the parsing fails.
    """

    word = "SPIN DOWN ORBITALS"

    if word in content:
        lines = content.splitlines()
        for i in range(len(lines) -1, -1, -1):
            if word in lines[i]:
                for line in reversed(lines):
                    if "SPIN DOWN ORBITALS" in line:
                        found_section = True
                        i = lines.index(line)
                        continue
                
                # Get the number of orbitals from the line two lines above the "SPIN DOWN ORBITALS" section
                n_orb = int(lines[i-2].split()[0])

                if found_section:
                    # Iterate over the orbitals to find the HOMO and LUMO
                    for j in range(n_orb):
                        parts = lines[i-j].split()
                        # Check if the line corresponds to an occupied orbital (HOMO)
                        if len(parts) == 4 and parts[1] == "1.0000":
                            homo = float(parts[3])
                            lumo_parts = lines[i-j+1].split()
                            # Get the energy of the next orbital (LUMO)
                            lumo = float(lumo_parts[3])
                            break
                
                # Write the HOMO, LUMO, and HOMO-LUMO gap to the log file
                gap = abs(homo) - lumo
                if homo is not None and lumo is not None:
                    return homo, lumo, gap
                else:
                    None

def write_xyz(content: str) -> None:
    """
    Extracts Cartesian coordinates from the content of a file and writes them to a new .xyz file.
    
    This function searches for a specific keyword ("CARTESIAN COORDINATES (ANGSTROEM)") 
    in the content of a file, extracts the corresponding atomic coordinates, and writes 
    them to a new .xyz file. The number of atoms is assumed to be n. Additionally, the 
    energy value is retrieved using the `get_energy` function and included in the .xyz file.
    
    Args:
        content (str): The content of the file as a string, typically from an ORCA output file.
    Returns:
        None: The function writes the output to a file and does not return any value.
    Notes:
        - The function assumes that the input directory contains files with a ".out" extension.
        - The `get_energy` function must be defined elsewhere in the codebase.
        - If the keyword is not found in the content, the function prints a message and exits.
    """

    dir = os.getcwd()
    n = 38
    for file in os.listdir(dir):
        if file.endswith(".out"):
            file_path = os.path.join(dir, file)
    
    # Search for the target string from the end of the file
    word = "CARTESIAN COORDINATES (ANGSTROEM)"
    lines = content.splitlines()
    for i in range(len(lines) - 1, -1, -1):
        if word in lines[i]:
            coordinates = lines[i+2:i+2+n]
            break
    else:
        print(f"String '{word}' not found in the file.")
        return

    # Write the coordinates to a new .xyz file
    xyz_file_path = file_path.replace('.out', '.xyz')
    with open(xyz_file_path, 'w') as xyz_file:
        xyz_file.write(f"{n}\n")
        energy = get_energy(content)
        xyz_file.write(f"{energy}\n")
        xyz_file.write('\n'.join(coordinates))

def read_xyz(path: str) -> tuple[list[str], np.ndarray]:
    """
    Read an xyz file and return atoms types and the coordinates.

    Args:
        file: path to the xyz file.
    Returns:
        A tuple containing the coordinates (np.ndarray) and atom types (list[str]).
    """
    atoms = []
    coordinates = []
    with open(path, "r") as file:
        for i, line in enumerate(file):
            if i < 2:
                continue
            atom, *xyz = line.split()
            atoms.append(atom)
            coordinates.append(xyz)
    
    return atoms, np.array(coordinates, dtype=float)

def get_distances() -> float:
    """Calculate the average interatomic distance for valid bonds in the XYZ file.
    
    A valid bond is defined as a distance between two atoms that is less than or equal to a specified threshold.

    Returns:
        float: The average distance of all valid bonds in Angstroms.
    """
    dir = os.getcwd()
    for file in os.listdir(dir):
        if file.endswith(".xyz"):
            file_path = os.path.join(dir, file)
    
    atoms, coords = read_xyz(file_path)
    
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
    
    # Calculate the average distance of all valid bonds
    average_distance = np.mean([dist for _, _, dist in valid_distances])
    return average_distance


if __name__ == "__main__":
    main()