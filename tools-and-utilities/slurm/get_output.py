'''
This script connects to a remote server via SSH to retrieve the latest 5 lines from Orca-generated .out files located in a specified directory. It excludes files that begin with 'slurm-' and logs the output into a specified log file.
Modules:
    paramiko: A module to handle SSH connections.
    os: A module to interact with the operating system.
Environment Variables:
    hostname: The hostname of the remote server.
    username: The username for the SSH connection.
    password: The password for the SSH connection (or use a private key file for more security).
Functions:
    get_output(): Retrieves the latest 5 lines from the Orca-generated .out files and logs the output into a log file.
Usage:
    Ensure that the hostname, username, password, orca_out_directory, and log_file variables are correctly set before running the script. The script will establish an SSH connection to the remote server, list the .out files in the specified directory, fetch the latest 5 lines from each file, and log the results into the specified log file.
'''

import paramiko
import os

# Retrieve values from environment variables or GitHub Secrets if necessary
hostname = 'hostname'
username = 'username'
password = 'password'  # Or use a private key file for more security

# Define the directory path where the SLURM files are located
orca_out_directory = 'path_to_orca_out_files'  # Define your path here

log_file = 'tools-and-utilities/slurm/get_output_freq.log'  # Define your log file path here

# Establish SSH connection using the private key or password
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

client.connect(hostname, username=username, password=password)

def get_output():
    """
    Retrieves the latest 5 lines from the Orca-generated .out files located in the specified directory,
    excluding files that begin with 'slurm-', and logs the output into a log file.
    """
    
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