"""
This script connects to a remote server via SSH, lists all .out files in a specified directory,
and extracts the HOMO-LUMO gap from each file. The results are logged into a specified log file.
Functions:
    get_gap(): Connects to the SSH server, lists .out files, reads their content, searches for
               the "SPIN DOWN ORBITALS" section, extracts the HOMO and LUMO energies, calculates
               the HOMO-LUMO gap, and writes the results to a log file.
Dependencies:
    - os
    - connection (connect_to_ssh function)
Usage:
    Call the get_gap() function to execute the script.
"""

import os
from connection import connect_to_ssh

# Define the directory path where the SLURM files are located
orca_out_directory = '/LUSTRE/home/erenteria/orca/binaries/freq/completed'
# Define the log file path
log_file = 'tools-and-utilities/slurm/gap.log'

def get_gap():
    # Connect to the SSH server
    client, username = connect_to_ssh()
    
    # List all files in the Orca output directory
    stdin, stdout, stderr = client.exec_command(f'ls {orca_out_directory}')
    files = stdout.read().decode()
    error_message = stderr.read().decode()
    
    if error_message:
        print(f"Error listing files: {error_message}")
        return

    # Filter files that end with .out and do not start with 'slurm-'
    out_files = [f for f in files.splitlines() if f.endswith('.out') and not f.startswith('slurm-')]

    # Search for the keywords in each .out file
    with open(log_file, 'w') as file:
        file.write("***HOMO-LUMO Gaps:***\n")
        for out_file in out_files:
            out_file_path = os.path.join(orca_out_directory, out_file)

            # Read the content of the .out file
            stdin, stdout, stderr = client.exec_command(f'cat {out_file_path}')
            content = stdout.read().decode()
            error_message = stderr.read().decode()
            
            if error_message:
                file.write(f"Error reading file {out_file_path}: {error_message}\n")
                continue

            lines = content.splitlines()
            found_section = False
            homo, lumo = None, None
            
            # Search for the section "SPIN DOWN ORBITALS"
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
            
            # Write the file path to the log file
            file.write(f"\nFile: {out_file}\n")
            
            # Write the HOMO, LUMO, and HOMO-LUMO gap to the log file
            if homo is not None and lumo is not None:
                file.write(f"HOMO: {homo:.6f}\n")
                file.write(f"LUMO: {lumo:.6f}\n")
                file.write(f"HOMO-LUMO Gap: {abs(homo) - lumo:.6f}\n")
            else:
                file.write("HOMO and/or LUMO not found.\n")

    client.close()

get_gap()
