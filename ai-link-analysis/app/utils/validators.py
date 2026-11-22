import ipaddress
import socket
from urllib.parse import urlsplit

from fastapi import HTTPException


def validate_public_url(url: str) -> str:
    """Allow only public HTTP(S) destinations; reject local/private IPs and hostnames."""
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(status_code=400, detail="Only http and https URLs are allowed.")
    if not parsed.hostname or parsed.username or parsed.password:
        raise HTTPException(status_code=400, detail="Invalid website URL.")
    if parsed.port and parsed.port not in {80, 443}:
        raise HTTPException(status_code=400, detail="Only standard HTTP/HTTPS ports are allowed.")

    hostname = parsed.hostname.rstrip(".").lower()
    if hostname in {"localhost", "localhost.localdomain"} or hostname.endswith((".local", ".internal", ".test")):
        raise HTTPException(status_code=400, detail="Local or internal hostnames are not allowed.")

    try:
        records = socket.getaddrinfo(hostname, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)
    except socket.gaierror:
        raise HTTPException(status_code=400, detail="Website hostname could not be resolved.")

    if not records:
        raise HTTPException(status_code=400, detail="Website hostname could not be resolved.")
    for record in records:
        address = ipaddress.ip_address(record[4][0])
        if not address.is_global:
            raise HTTPException(status_code=400, detail="Private, loopback, or reserved IP addresses are not allowed.")
    return url
