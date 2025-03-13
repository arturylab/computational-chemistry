"""
This script connects to a remote SSH server, lists files in a specified directory, 
and searches for Cartesian coordinates in ORCA output files. The coordinates are 
then written to a log file.
Functions:
    get_coords(): Connects to the SSH server, lists .out files in the specified 
    directory, searches for Cartesian coordinates in each file, and writes the 
    coordinates to a log file. If any errors occur during file listing or reading, 
    they are logged as well.
"""

import os
from connection import connect_to_ssh

# Define the directory path where the SLURM files are located
orca_out_directory = '/LUSTRE/home/erenteria/orca/binaries/freq/completed'
# Define the log file path
log_file = 'tools-and-utilities/slurm/coords.log'

def get_coords():
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
        for out_file in out_files:
            out_file_path = os.path.join(orca_out_directory, out_file)

            # Read the content of the .out file
            stdin, stdout, stderr = client.exec_command(f'cat {out_file_path}')
            content = stdout.read().decode()
            error_message = stderr.read().decode()
            
            if error_message:
                file.write(f"Error reading file {out_file_path}: {error_message}\n")
                continue
            
            n = 38 # Number of atoms

            # Check if the keyword "CARTESIAN COORDINATES (ANGSTROEM)" is in the file content
            if "CARTESIAN COORDINATES (ANGSTROEM)" in content:
                # Split the content into lines
                lines = content.splitlines()
                # Iterate over the lines in reverse order to find the keyword
                for i in range(len(lines) - 1, -1, -1):
                    if "CARTESIAN COORDINATES (ANGSTROEM)" in lines[i]:
                        # Extract the coordinates lines following the keyword
                        coordinates = lines[i+2:i+2+n]
                        # Write the number of atoms and file name to the log file
                        file.write(f"\n{n}\n")
                        file.write(f"File: {out_file}\n")
                        # Write each coordinate line to the log file
                        for coord_line in coordinates:
                            file.write(f"{coord_line}\n")
                        break
            else:
                # If the keyword is not found, log the information
                # If the keyword is not found
                file.write(f"File: {out_file_path}\n")
                file.write("Keyword 'CARTESIAN COORDINATES (ANGSTROEM)' not found.\n\n")

    client.close()

get_coords()
