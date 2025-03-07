"""
This script connects to a remote server via SSH and checks the following:
1. List of jobs belonging to the user in SLURM.
2. List of jobs queued for the user in SLURM.

The results are saved in a .log file, which is overwritten every time the script runs.

It uses the 'paramiko' library to handle SSH connections and the 'schedule' library to run the task periodically.
"""

import schedule
import time
import paramiko
import os

# Retrieve values from environment variables or GitHub Secrets if necessary
hostname = os.getenv('SSH_HOST')
username = os.getenv('SSH_USER')
password = os.getenv('SSH_PASSWORD')
log_file = 'tools-and-utilities/slurm/jobs.log'

def check_jobs():
    """
    Connects to the SSH server and retrieves the list of jobs for the user, 
    as well as the jobs currently queued in SLURM. The results are saved to a log file.
    
    The function does the following:
    - Connects to the SSH server.
    - Executes 'squeue' to fetch the list of running jobs and queued jobs.
    - Writes the output to a log file, overwriting any previous content.
    """
    
    # SSH connection
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password)

    # # Command to get the list of jobs for the user in pending state
    # stdin, stdout, stderr = client.exec_command(f'squeue -u {username} -t PD')
    # jobs_user_pending = stdout.read().decode()

    # Command to get the list of jobs for the user
    stdin, stdout, stderr = client.exec_command('squeue -u ' + username)
    jobs_user = stdout.read().decode()

    # Command to get the list of jobs for the user
    stdin, stdout, stderr = client.exec_command('squeue')
    jobs = stdout.read().decode()

    # Command to get the list of queued jobs for the user
    # stdin, stdout, stderr = client.exec_command('squeue -u ' + username + ' --states=PD')
    # queued_jobs = stdout.read().decode()

    # Save the output to the log file (overwriting previous content)
    with open(log_file, 'w') as file:
        file.write(f"List of jobs for {username}:\n")
        file.write(jobs_user)
        file.write("\nList of jobs:\n")
        file.write(jobs)
        # file.write("\nList of queued jobs:\n")
        # file.write(queued_jobs)
    
    client.close()

# Schedule the task to run every 10 minutes
schedule.every(1).hour.do(check_jobs)

# Run the scheduled task in a loop
while True:
    schedule.run_pending()
    time.sleep(1)
