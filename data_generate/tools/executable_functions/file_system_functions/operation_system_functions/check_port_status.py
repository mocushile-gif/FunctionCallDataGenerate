import os
import socket
from dotenv import load_dotenv
load_dotenv()
def check_port_status(host, port):
    """
    Check if a specific port is open on a host.

    Parameters:
    - host (str): The host to check.
    - port (int): The port to check.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. A success message or error message.
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(5)
        try:
            sock.connect((host, port))
            return True, f"Port {port} on {host} is open."
        except Exception as e:
            return False, f"Port {port} on {host} is not open. Error: {str(e)}"

if __name__ == '__main__':
    # Example usage
    success, output = check_port_status("10.121.4.11", 8000)
    print(success, output)
