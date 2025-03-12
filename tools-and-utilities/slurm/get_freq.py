"""
This script connects to a remote server via SSH, lists all files in a specified directory,
and searches for vibrational frequency information in ORCA output files. It logs the number
of imaginary frequencies found in each file to a log file.
Functions:
    get_freq(): Connects to the SSH server, lists ORCA output files, searches for vibrational
                frequency information, and logs the results.
Dependencies:
    - os: For file path manipulation.
    - connection: Custom module for establishing SSH connections.
Usage:
    Run the script to connect to the remote server, process the ORCA output files, and log
    the results to the specified log file.
"""

import os
from connection import connect_to_ssh

# Define the directory path where the SLURM files are located
orca_out_directory = '/LUSTRE/home/erenteria/orca/binaries/freq'
# Define the log file path
log_file = 'tools-and-utilities/slurm/freq.log'

def get_freq():
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

            # Search for "VIBRATIONAL FREQUENCIES"
            if "VIBRATIONAL FREQUENCIES" in content:
                # Count occurrences of "***imaginary mode***"
                imaginary_count = content.count("***imaginary mode***")
                
                # Log the result
                file.write(f"File: {out_file_path}\n")
                file.write(f"Number of imaginary frequencies: {imaginary_count}\n\n")
            else:
                # If the keyword is not found
                file.write(f"File: {out_file_path}\n")
                file.write("Keyword 'VIBRATIONAL FREQUENCIES' not found.\n\n")

    client.close()

get_freq()
