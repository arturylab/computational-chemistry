"""
Script Description:
This script is designed to manage and submit SLURM jobs in a computational environment. 
It monitors the current number of running and pending jobs for a given user, identifies 
jobs that have not yet been executed (based on the absence of corresponding `.out` files), 
and submits them to the SLURM workload manager while adhering to a maximum limit of pending jobs.
Functions:
- check_current_jobs(username: str) -> tuple:
    Retrieves the number of jobs in "Running" (R) and "Pending" (PD) states for the specified user 
    by querying the SLURM queue using the `squeue` command.
- find_jobs_to_submit() -> list:
    Identifies `.slurm` job files in the current directory that do not have a corresponding `.out` 
    file, indicating that they have not yet been executed.
- main():
    The main function orchestrates the job submission process. It continuously monitors the SLURM 
    queue, submits jobs from the list of pending `.slurm` files while respecting the maximum allowed 
    pending jobs, and waits for a specified polling interval before rechecking the queue.
Usage:
Run the script in a directory containing `.slurm` job files. The script will automatically detect 
and submit jobs that have not been executed, ensuring that the number of pending jobs does not 
exceed the defined limit.
"""
import os
import subprocess
import time
from collections import defaultdict

def check_current_jobs(username: str) -> tuple:
    """Gets the number of jobs in Running (R) and Pending (PD) states"""
    cmd = f"squeue -u {username} -o '%T' --noheader"
    result = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,  # Replace capture_output
        stderr=subprocess.PIPE,
        universal_newlines=True  # Equivalent to text=True in Python 3.6
    )
    
    states = defaultdict(int)
    for state in result.stdout.splitlines():
        states[state.strip()] += 1
        
    return states.get('RUNNING', 0), states.get('PENDING', 0)

def find_jobs_to_submit():
    """Finds jobs that have not been executed (missing .out file)"""
    all_files = os.listdir('.')
    slurm_files = [f for f in all_files if f.endswith('.slurm')]
    out_files = set([f for f in all_files if f.endswith('.out')])
    
    jobs_to_submit = []
    for slurm in slurm_files:
        expected_out = slurm.replace('.slurm', '.out')
        if expected_out not in out_files:
            jobs_to_submit.append(slurm)
    
    return jobs_to_submit

def main():
    username = os.getenv('USER')
    max_pending = 5
    poll_interval = 60  # seconds

    while True:
        running, pending = check_current_jobs(username)
        jobs_to_submit = find_jobs_to_submit()
        
        # Replace original prints with:
        print(f"\nCurrent state: Running={running}, Pending={pending}", flush=True)
        print(f"Remaining jobs: {len(jobs_to_submit)}", flush=True)

        if not jobs_to_submit:
            print("\nAll jobs completed!")
            break

        while pending < max_pending and jobs_to_submit:
            next_job = jobs_to_submit.pop(0)
            
            # Submit job (Python 3.6 compatible version)
            cmd = f"sbatch {next_job}"
            result = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            if result.returncode == 0:
                job_id = result.stdout.split()[-1]
                print(f"Submitted: {next_job} (ID: {job_id})")
                pending += 1
            else:
                print(f"Error submitting {next_job}: {result.stderr}")

        time.sleep(poll_interval)

if __name__ == "__main__":
    main()
