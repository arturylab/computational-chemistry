
'''This script connects to a remote server via SSH using the Paramiko library to search for "VIBRATIONAL FREQUENCIES" 
sections in Orca .out files located in a specified directory. It counts the occurrences of "imaginary mode" 
within these sections and logs the results to a specified log file.
Functions:
    get_output_freq(): Searches for the "VIBRATIONAL FREQUENCIES" section in Orca .out files, counts the occurrences 
                       of "imaginary mode", and logs the results.
Environment Variables:
    hostname (str): The hostname of the remote server.
    username (str): The username for SSH authentication.
    password (str): The password for SSH authentication (or use a private key file for more security).
Directory Paths:
    orca_out_directory (str): The directory path where the Orca .out files are located.
    log_file (str): The path to the log file where results will be written.
Usage:
    Ensure that the hostname, username, password, orca_out_directory, and log_file variables are correctly set.
    Run the script to establish an SSH connection, search for the specified keywords in the Orca .out files, 
    and log the results.'
'''

import paramiko
import os

# Retrieve values from environment variables or GitHub Secrets if necessary
hostname = 'hostname'
username = 'username'
password = 'password'  # Or use a private key file for more security

# Define the directory path where the SLURM files are located
orca_out_directory = 'path_to_orca_out_files'  # Define your path here

log_file = 'tools-and-utilities/slurm/get_output_freq.log' # Define your log file path here

# Establish SSH connection using the private key or password
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

client.connect(hostname, username=username, password=password)

def get_output_freq():
    """
    Searches for the "VIBRATIONAL FREQUENCIES" section in Orca .out files located in the specified directory.
    If found, it counts the occurrences of "imaginary mode" and logs the result.
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


get_output_freq()
