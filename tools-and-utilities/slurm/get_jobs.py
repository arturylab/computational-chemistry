"""
This script connects to an SSH server to retrieve and log the status of jobs in a SLURM workload manager.
It fetches the list of jobs in pending and running states for the current user, as well as the complete list of jobs,
and saves this information to a log file.
Functions:
    check_jobs(): Connects to the SSH server, retrieves job information, and writes it to a log file.
Usage:
    The script can be scheduled to run periodically using the `schedule` library. Uncomment the scheduling
    section to run the `check_jobs` function every hour.
Dependencies:
    - schedule
    - time
    - datetime
    - connection (custom module to handle SSH connections)
"""

import schedule
import time
import datetime
from connection import connect_to_ssh

log_file = 'tools-and-utilities/slurm/jobs.log'

def get_jobs():
    # Connect to the SSH server
    client, username = connect_to_ssh()

    # Command to get the list of jobs for the user in pending state
    stdin, stdout, stderr = client.exec_command(f'squeue -u {username} -t PD')
    jobs_user_pending = stdout.read().decode()

    # Command to get the list of jobs for the user in running state
    stdin, stdout, stderr = client.exec_command(f'squeue -u {username} -t R')
    jobs_user = stdout.read().decode()

    # Command to get the list of jobs for the user
    stdin, stdout, stderr = client.exec_command('squeue')
    jobs = stdout.read().decode()

    # Save the output to the log file (overwriting previous content)
    with open(log_file, 'w') as file:
        file.write(f"\nList of jobs pending state for {username}:\n")
        file.write(jobs_user_pending)
        file.write(f"\nList of jobs for running state for {username}:\n")
        file.write(jobs_user)
        file.write("\nList of jobs:\n")
        file.write(jobs)
        print(f"Jobs checked and saved to jobs.log at {datetime.datetime.now()}")
    
    client.close()

get_jobs()

# Schedule the task to run every 1 hour
# schedule.every(1).hour.do(check_jobs)

# # Run the scheduled task in a loop
# while True:
#     schedule.run_pending()
#     time.sleep(1)
