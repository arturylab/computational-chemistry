"""
This script connects to a remote SSH server, lists all files in a specified directory,
and searches for the keyword "FINAL SINGLE POINT ENERGY" in each file that ends with .out
and does not start with 'slurm-'. The results are logged into a specified log file.
Functions:
    get_energy(): Connects to the SSH server, lists files, searches for the keyword in each file,
                  and logs the results.
Dependencies:
    - os
    - connection (a module that provides the connect_to_ssh function)
Usage:
    Run the script to connect to the SSH server, process the files, and generate the log file.
"""

import os
from connection import connect_to_ssh

# Define the directory path where the SLURM files are located
orca_out_directory = '/LUSTRE/home/erenteria/orca/binaries/opt'
# Define the log file path
log_file = 'tools-and-utilities/slurm/energy.log'

def get_energy():
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

            # Search for "FINAL SINGLE POINT ENERGY"
            if "FINAL SINGLE POINT ENERGY " in content:
                # Find the line with "FINAL SINGLE POINT ENERGY "
                lines = content.splitlines()
                for line in reversed(lines):
                    if "FINAL SINGLE POINT ENERGY " in line:
                        file.write(f"File: {out_file}\n")
                        file.write(f"{line}\n\n")
                        break
            else:
                # If the keyword is not found
                file.write(f"File: {out_file_path}\n")
                file.write("Keyword 'FINAL SINGLE POINT ENERGY ' not found.\n\n")

    client.close()

get_energy()
