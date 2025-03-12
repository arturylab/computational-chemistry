"""
This script connects to a remote server via SSH, lists all files in a specified directory,
filters out files that end with '.out' and do not start with 'slurm-', and fetches the last
5 lines of each filtered file. The fetched output is then saved into a log file.
Functions:
    get_output(): Connects to the SSH server, lists files in the specified directory,
                  filters and fetches the last 5 lines of each relevant file, and writes
                  the output to a log file.
"""

import os
from connection import connect_to_ssh

# Define the directory path where the SLURM files are located
orca_out_directory = '/LUSTRE/home/erenteria/orca/binaries/freq'
# Define the log file path
log_file = 'tools-and-utilities/slurm/output.log'

def get_output():
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

    # Fetch the latest 5 lines of each .out file
    with open(log_file, 'w') as file:
        for out_file in out_files:
            out_file_path = os.path.join(orca_out_directory, out_file)
            
            # Execute the 'tail' command to get the last 5 lines of the .out file
            stdin, stdout, stderr = client.exec_command(f'tail -n 5 {out_file_path}')
            output = stdout.read().decode()
            error_message = stderr.read().decode()
            
            if error_message:
                file.write(f"Error fetching output for {out_file_path}: {error_message}\n")
                continue

            # Save the result into the log file
            file.write(f"Latest output for {out_file_path}:\n")
            file.write(output)
            file.write("\n\n")  # Add separation between files

    client.close()

get_output()