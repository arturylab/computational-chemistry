"""
This script attempts to establish an SSH connection using the `connect_to_ssh` function
from the `connection` module. If the connection is successful, it prints a success message.
If the connection fails, it catches the exception and prints an error message with the 
exception details.

Modules:
    connection: Contains the `connect_to_ssh` function to establish an SSH connection.

Functions:
    connect_to_ssh: Establishes an SSH connection.

Exceptions:
    Exception: Catches any exception that occurs during the SSH connection attempt and 
    prints an error message.
"""

from connection import connect_to_ssh

try:
    connect_to_ssh()
    print(f"SSH connection established successfully.")
except Exception as e:
    print(f"Failed to establish SSH connection: {str(e)}")
