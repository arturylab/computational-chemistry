"""
Establishes an SSH connection using credentials from environment variables.
This function retrieves the SSH hostname, username, and password from the 
environment variables 'SSH_HOST', 'SSH_USER', and 'SSH_PASSWORD' respectively.
It then attempts to establish an SSH connection using these credentials.
Returns:
    tuple: A tuple containing the SSH client object and the username.
Raises:
    paramiko.AuthenticationException: If authentication fails.
    paramiko.SSHException: If an SSH-related error occurs.
    Exception: If any other error occurs during the connection process.
"""

import paramiko
import os

def connect_to_ssh():
    # Retrieve values from environment variables
    hostname = os.getenv('SSH_HOST')
    username = os.getenv('SSH_USER')
    password = os.getenv('SSH_PASSWORD')
        
    # SSH connection
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=hostname, username=username, password=password)
    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your credentials.")
        raise
    except paramiko.SSHException as ssh_exception:
        print(f"SSH exception occurred: {ssh_exception}")
        raise
    except Exception as e:
        print(f"An error occurred while connecting: {e}")
        raise
    
    return client, username
