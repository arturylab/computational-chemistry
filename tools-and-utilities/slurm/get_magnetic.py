"""
This script connects to a remote server via SSH, lists all ORCA output files in a specified directory,
and extracts magnetic properties from these files. The results are logged into a specified log file.
Functions:
    get_magnetic(): Connects to the SSH server, lists ORCA output files, extracts magnetic properties,
                    and writes the results to a log file.
Details:
- Connects to the SSH server using the `connect_to_ssh` function from the `connection` module.
- Lists all files in the specified ORCA output directory.
- Filters files that end with '.out' and do not start with 'slurm-'.
- Reads the content of each filtered file and searches for the section "Sum of atomic charges".
- Calculates the sum of atomic spin populations for each element.
- Writes the results to the specified log file, including the sum of spins per element and the line
  "Sum of atomic spin populations" if found.
"""

import os
from collections import defaultdict
from connection import connect_to_ssh

# Define the directory path where the SLURM files are located
orca_out_directory = '/LUSTRE/home/erenteria/orca/binaries/freq/completed'
# Define the log file path
log_file = 'tools-and-utilities/slurm/magnetic.log'

def get_magnetic():
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
        file.write("***MULLIKEN ATOMIC SPIN POPULATIONS:***\n")
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
            spin_sums = defaultdict(float)
            found_section = False
            
            # Search for the section "Sum of atomic charges"
            for line in reversed(lines):
                if "Sum of atomic charges" in line:
                    found_section = True
                    continue
                
                if found_section:
                    # Split the line into parts
                    parts = line.split()
                    # Check if the line has 4 parts and the first part is a digit
                    if len(parts) == 4 and parts[0].isdigit():
                        element = parts[1]
                        spin_population = float(parts[3])
                        # Add the spin population to the corresponding element in the dictionary
                        spin_sums[element] += spin_population
                    # Break the loop if the line does not have 4 parts or the first part is not a digit
                    elif not parts or not parts[0].isdigit():
                        break

            file.write(f"\nFile: {out_file}\n")
            
            # Write the sum of spins per element
            for element, total_spin in spin_sums.items():
                file.write(f"{element} {total_spin:.6f} ")
            
            # Search and write the line "Sum of atomic spin populations"
            for line in reversed(lines):
                if "Sum of atomic spin populations" in line:
                    file.write(f"\n{line}")
                    file.write(f"\nAvg: {(float(line.split()[5]) / 38):.6f}\n")
                    break
            else:
                file.write("\nKeyword 'Sum of atomic spin populations' not found.\n")
    
    client.close()

get_magnetic()
