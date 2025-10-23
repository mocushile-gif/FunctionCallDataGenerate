import subprocess
import os
from dotenv import load_dotenv
load_dotenv()

def ping_host(host, count=4, timeout=2):
    """
    Ping a host and return the results.

    Parameters:
    - host (str): The host to ping.
    - count (int): The number of ping attempts. Defaults to 4.
    - timeout (int): The timeout for each ping in seconds. Defaults to 2.

    Returns:
    - A tuple containing:
        1. Success status (True/False).
        2. The ping results or error message.
    """
    command = ["ping", "-c", str(count), "-W", str(timeout), host]
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        return True, result.stdout.strip()
    else:
        return False, result.stderr.strip()

if __name__ == '__main__':
    # Example usage
    success, output = ping_host("10.121.4.11")
    print(success, output)
