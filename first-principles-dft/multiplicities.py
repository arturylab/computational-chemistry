import re
import sys

def parse_input(cluster):
    """
    Parses the input atomic cluster and returns a dictionary with the elements and their quantities.
    """
    elements = re.findall(r'([A-Z][a-z]*)(\d*)', cluster)
    parsed = {}
    for element, count in elements:
        parsed[element] = int(count) if count else 1  # If no number is provided, assume 1
    return parsed

def calculate_multiplicities(atom_counts):
    """
    Calculates all possible multiplicities for a given atomic cluster.
    """
    # Number of unpaired electrons per element according to Hund's rule
    unpaired_electrons = {
        'Fe': 4,  # Electronic configuration: [Ar] 3d6 4s2 -> 4 unpaired electrons
        'Co': 3,  # Electronic configuration: [Ar] 3d7 4s2 -> 3 unpaired electrons
        'Ni': 2   # Electronic configuration: [Ar] 3d8 4s2 -> 2 unpaired electrons
    }

    total_unpaired = 0
    for element, count in atom_counts.items():
        if element in unpaired_electrons:
            total_unpaired += unpaired_electrons[element] * count
        else:
            print(f"Warning: The element {element} is not supported.")
    
    # Possible multiplicities are 2S + 1, where S is the total spin (S = total_unpaired / 2)
    multiplicities = list(range(1, total_unpaired + 2, 2))  # Generates 1, 3, 5, ..., 2S+1
    return multiplicities

def main():
    if len(sys.argv) != 2:
        print("Usage: python multiplicities.py <cluster>")
        print("Example: python multiplicities.py Fe2Co4Ni")
        sys.exit(1)
    
    cluster = sys.argv[1]
    atom_counts = parse_input(cluster)
    multiplicities = calculate_multiplicities(atom_counts)
    
    print(f"For the cluster {cluster}, the possible multiplicities are: {multiplicities}")

if __name__ == "__main__":
    main()