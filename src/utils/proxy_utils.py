
import re


def ensure_valid_proxy(url: str) -> bool:
    """Verify if a string has a valid proxy url format: <USERNAME>:<PASSWORD>@<IP>:<PORT>

    Returns
    -------
    bool
        True if the format is valid. Raise exception otherwise
    
    Raises
    ------
    ValueError
        If format is invalid.
    """

    try:
        if "://" in url:
            url = url.split("://")[1] # remove protocol part

        # Split by '@' to separate the credentials from the IP:PORT
        credentials, ip_port = url.split('@')
        
        # Split credentials into USERNAME and PASSWORD
        username, password = credentials.split(':')
        
        # Split ip_port into IP and PORT
        ip, port = ip_port.split(':')
        
        if not username or not password:
            raise ValueError("Invalid format: Username or password is missing.")
        
        ip_parts = ip.split('.')
        if len(ip_parts) != 4 or not all(part.isdigit() and 0 <= int(part) <= 255 for part in ip_parts):
            raise ValueError("Invalid format: IP address is invalid.")        

        if not port.isdigit() or not 1 <= int(port) <= 65535:
            raise ValueError("Invalid format: Port number is invalid.")
        
        # If all validations pass
        return True
    except ValueError as e:
        raise ValueError(f"Invalid string format: {str(e)}")
    
def is_valid_proxy(url: str):
    try:
        ensure_valid_proxy(url)
        return True
    except Exception:
        return False

def extract_ip(url: str) -> str:
    """Extract IP address from url

    Following URL formats are accepted:
        1. IP:Port
        2. Protocol://Username:Password@IP:Port
    
    
    Returns
    -------
    str
        String containing IP address.
        Empty string if the input was invalid
    """
    # Define a regex pattern for extracting IP addresses with a more open protocol
    ip_pattern = r"(?:\w+:\/\/(?:\S+@)?)?(\d{1,3}(?:\.\d{1,3}){3})"
    
    # Search for the IP in the URL
    match = re.search(ip_pattern, url)
    
    if match:
        return match.group(1)  # Return the matched IP part
    else:
        return ""  # No IP found in the URL
    
def get_proxy_from_file(path: str) -> str:
    with open(path, "r") as f:
        proxy = f.readline().strip()
        ensure_valid_proxy(proxy)
        
        return proxy

def save_proxy_to_file(path: str, proxy: str) -> bool:
    with open(path, "w") as f:
        f.write(proxy)
        return True
    
def add_socks5_protocol_if_missing(url: str) -> str:
    if "://" in url:
        return url
    
    return f"socks5://{url}"
