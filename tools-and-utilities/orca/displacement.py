"""
This script processes ORCA output files (.out) to extract atomic coordinates and
vibrational displacement data. It specifically looks for the initial Cartesian
coordinates (in Angstroms) and the displacement vectors corresponding to a
predefined set of normal modes (starting from mode 6).

The script performs the following steps:
1.  Searches for .out files in a specified 'out' subdirectory.
2.  For each .out file:
    a.  Parses the original Cartesian coordinates of the atoms.
    b.  Finds a specific marker line ("                  6          7          8          9         10         11    ")
        that precedes the normal mode displacement data.
    c.  Reads the subsequent 114 lines (38 atoms * 3 coordinates: dx, dy, dz)
        to extract the displacement values from the second column (corresponding to mode 6, 12, etc.).
    d.  Calculates new atomic coordinates by adding the extracted dx, dy, and dz
        displacements (and an optional small step_size) to the original coordinates.
    e.  Writes the new coordinates into a .xyz file, saved in a 'disp' subdirectory.

The script requires the ORCA output files to have a consistent format for the
coordinate and displacement sections. Constants like NUM_ATOMS,
CARTESIAN_COORDS_HEADER, and DISPLACEMENT_MARKER_LINE define how the script
identifies and processes these sections.
"""

import os

# Constants
NUM_ATOMS = 38
CARTESIAN_COORDS_HEADER = "CARTESIAN COORDINATES (ANGSTROEM)"
# The exact line that precedes the displacement data blocks of the normal modes.
# The user specified to look for this line:
DISPLACEMENT_MARKER_LINE = "                  6          7          8          9         10         11    "

# Paths
# The script assumes it is executed from tools-and-utilities/orca/
# and that 'out' and 'disp' are subdirectories of this location.
base_dir = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(base_dir, "out")
disp_dir = os.path.join(base_dir, "disp")

# Create output directory if it does not exist
if not os.path.exists(disp_dir):
    os.makedirs(disp_dir)
    print(f"Directory created: {disp_dir}")

def parse_cartesian_coords(lines_iterator):
    """
    Parses the original cartesian coordinates.
    It is assumed that the iterator is positioned on the line *after* the one containing
    CARTESIAN_COORDS_HEADER.
    The expected structure is:
    ---------------------------------  (this line is the first read by next() here)
    Atom1 X Y Z
    Atom2 X Y Z
    ... (NUM_ATOMS times)
    """
    atom_symbols = []
    original_coords = []
    
    try:
        # Skip the line of dashes "---------------------------------" that follows the header.
        # The iterator was passed to this function after the header line was consumed.
        # The first next() here consumes the dashes line.
        header_separator_line = next(lines_iterator).strip()
        if not header_separator_line.startswith("---"):
            print(f"Warning: A line of dashes ('---') was expected after the coordinates header, but got: '{header_separator_line}'")
            print("         This may indicate a formatting issue in the input file or a script error.")
            return None, None

        # Now the iterator should be positioned to read the first atom line.
        for i in range(NUM_ATOMS):
            line_content = ""
            try:
                line_content = next(lines_iterator)
            except StopIteration:
                print(f"Warning: Unexpected end of file while trying to read atom {i+1}/{NUM_ATOMS} of the original coordinates.")
                return None, None

            line = line_content.strip()
            
            if not line: # If the line is empty after strip
                print(f"Warning: An empty line was found while trying to read atom {i+1}/{NUM_ATOMS} of the original coordinates.")
                print(f"         Original line content: '{line_content.rstrip()}'")
                return None, None

            parts = line.split()
            if len(parts) >= 4: 
                atom_symbols.append(parts[0])
                try:
                    original_coords.append(tuple(map(float, parts[1:4])))
                except ValueError:
                    print(f"Warning: Error converting coordinates to float for atom {i+1}/{NUM_ATOMS} (original).")
                    print(f"         Line: '{line}'")
                    print(f"         Numeric parts attempted: {parts[1:4]}")
                    return None, None
            else:
                print(f"Warning: Unexpected format in original coordinate line for atom {i+1}/{NUM_ATOMS}: '{line}'")
                print(f"         Number of parts: {len(parts)}. Parts: {parts}")
                print(f"         Original line content: '{line_content.rstrip()}'")
                return None, None
                
    except StopIteration: 
        print("Warning: Unexpected end of file while skipping the dashes line of the original coordinates.")
        return None, None
        
    if len(original_coords) == NUM_ATOMS and len(atom_symbols) == NUM_ATOMS:
        return atom_symbols, original_coords
    else:
        print(f"Warning: The expected {NUM_ATOMS} original coordinates were not read. Read: {len(original_coords)}")
        return None, None

def parse_displacements(lines_iterator):
    """
    Parses the displacement values.
    114 lines are expected after the marker line.
    Each relevant line contains an index and 6 displacement values.
    The first displacement value is taken (corresponding to the column of mode 6, 12, etc.).
    """
    displacement_values = []
    lines_to_read_for_displacements = NUM_ATOMS * 3 # 114 lines

    try:
        for i in range(lines_to_read_for_displacements):
            line = next(lines_iterator).strip()
            parts = line.split()
            if len(parts) >= 2:
                displacement_values.append(float(parts[1]))
            else:
                print(f"Warning: Unexpected format in displacement line: {line}")
                return None 
    except StopIteration:
        print("Warning: Unexpected end of file while reading displacements.")
        return None
    except ValueError:
        print(f"Warning: Error converting displacement to float in line: {line}")
        return None

    if len(displacement_values) == lines_to_read_for_displacements:
        return displacement_values
    else:
        print(f"Warning: The expected {lines_to_read_for_displacements} displacement values were not read.")
        return None

def process_out_file(filepath):
    atom_symbols = None
    original_coords = None
    displacement_values = None
    coords_parsed_successfully = False

    with open(filepath, 'r') as f:
        lines_iterator = iter(f)
        for line_content in lines_iterator: 
            line_stripped = line_content.strip() 
            
            if CARTESIAN_COORDS_HEADER in line_content and not coords_parsed_successfully:
                current_atom_symbols, current_original_coords = parse_cartesian_coords(lines_iterator)
                
                if current_atom_symbols is None: 
                    print(f"Error parsing coordinates in {filepath}. Skipping file.")
                    return
                
                atom_symbols = current_atom_symbols
                original_coords = current_original_coords
                coords_parsed_successfully = True

            elif line_stripped == DISPLACEMENT_MARKER_LINE.strip(): 
                if not coords_parsed_successfully:
                    print(f"Error: Displacement data found before cartesian coordinates in {filepath}. Skipping file.")
                    return

                displacement_values = parse_displacements(lines_iterator)
                if displacement_values is None: 
                    print(f"Error parsing displacements in {filepath}. Skipping file.")
                    return
                break 

    if not atom_symbols or not original_coords:
        print(f"No valid original coordinates found in {filepath}")
        return
    if not displacement_values:
        print(f"No valid displacement values found in {filepath} after the marker line.")
        return

    if len(original_coords) != NUM_ATOMS or len(atom_symbols) != NUM_ATOMS:
        print(f"Error: Incorrect number of atoms read for original coordinates in {filepath}. Expected: {NUM_ATOMS}, Read: {len(original_coords)}")
        return
    if len(displacement_values) != NUM_ATOMS * 3:
        print(f"Error: Incorrect number of displacement values read in {filepath}. Expected: {NUM_ATOMS * 3}, Read: {len(displacement_values)}")
        return

    dx = displacement_values[0:NUM_ATOMS]
    dy = displacement_values[NUM_ATOMS:2*NUM_ATOMS]
    dz = displacement_values[2*NUM_ATOMS:3*NUM_ATOMS]

    step_size = 0.1

    xyz_content = [f"{NUM_ATOMS}", f"Generated from {os.path.basename(filepath)}"]
    for i in range(NUM_ATOMS):
        new_x = original_coords[i][0] + dx[i] + step_size
        new_y = original_coords[i][1] + dy[i] + step_size
        new_z = original_coords[i][2] + dz[i] + step_size
        xyz_content.append(f"{atom_symbols[i]:<2s} {new_x:>15.6f} {new_y:>15.6f} {new_z:>15.6f}")

    out_filename_base = os.path.splitext(os.path.basename(filepath))[0]
    xyz_filepath = os.path.join(disp_dir, f"{out_filename_base}.xyz")
    try:
        with open(xyz_filepath, 'w') as f_xyz:
            for xyz_line in xyz_content:
                f_xyz.write(xyz_line + "\n")
        print(f"XYZ file generated: {xyz_filepath}")
    except IOError:
        print(f"Error: Could not write the XYZ file to {xyz_filepath}")

# --- Main loop ---
if not os.path.exists(out_dir):
    print(f"Error: The directory '{out_dir}' does not exist.")
else:
    print(f"Searching for .out files in: {out_dir}")
    processed_files = 0
    for filename in os.listdir(out_dir):
        if filename.endswith(".out"):
            full_filepath = os.path.join(out_dir, filename)
            print(f"Processing file: {full_filepath}")
            process_out_file(full_filepath)
            processed_files +=1
    if processed_files == 0:
        print("No .out files found to process.")

print("Process completed.")