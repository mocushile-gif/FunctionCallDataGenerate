import re

def is_valid_ip_address(ip: str) -> bool:
    """
    Checks if a string is a valid IP address (IPv4).

    Parameters:
    - ip (str): The string to check.

    Returns:
    - bool: True if the string is a valid IPv4 address, False otherwise.
    """
    # Regular expression for validating an IPv4 address
    ip_pattern = r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    
    # Match the IP address against the regular expression
    return bool(re.match(ip_pattern, ip))

# Example usage
if __name__ == "__main__":
    ip = "192.168.1.1"
    print(f"Is '{ip}' a valid IPv4 address? {is_valid_ip_address(ip)}")
