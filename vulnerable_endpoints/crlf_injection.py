"""
crlf_injection.py

Intentionally vulnerable route used to test whether the pipeline
(Bandit, ZAP) catches CRLF Injection / HTTP Response Splitting.

"""
import re
from urllib.parse import unquote, urlparse
from flask import Blueprint, Response, redirect, request

crlf_bp = Blueprint("crlf_injection", __name__)

ALLOWED_PATHS = {"/", "/dashboard", "/login", "/home"}
ALLOWED_HOSTS = {"example.com", "my-domain.com"}

def go():
    target_url = request.args.get("url", "/")

    # 1. URL Decode & CRLF / Traversal checks
    decoded_url = unquote(target_url)
    if re.search(r"[\r\n]", decoded_url):
        return Response("Invalid redirect target: CRLF detected", status=400)

    # Deny Path traversal chars within input('..' or '.') 
    if ".." in decoded_url or "/." in decoded_url or "\\." in decoded_url:
        return Response("Invalid path: Traversal sequence detected", status=400)

    try:
        parsed = urlparse(decoded_url)

        #Domain Check (SSRF & Open Redirect block)
        if parsed.netloc:
            host = parsed.netloc.split(":")[0]
            if host not in ALLOWED_HOSTS:
                return Response("Untrusted redirect host", status=400)
            return redirect(target_url)

        # 3. Path Kontrolü (Block random paths apart from Allow-list)
        path = parsed.path if parsed.path else "/"
        if path not in ALLOWED_PATHS:
            return Response("Untrusted redirect path", status=400)

    except Exception:
        return Response("Malformed URL", status=400)

    return redirect(path)
    """
    VULNERABLE ENDPOINT.

    The 'url' parameter is passed straight into redirect with no
    validation. If it contains \r\n, an attacker can inject a
    malicious header/cookie into the response.

    Test request:
        http://localhost:5000/go?url=http://example.com%0d%0aSet-Cookie:%20injected=true
    """
    """  target_url = request.args.get("url", "/")

    #  no validation before redirectt
    return redirect(target_url)"""

