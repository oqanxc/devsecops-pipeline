"""
crlf_injection.py

Intentionally vulnerable route used to test whether the pipeline
(Bandit, ZAP) catches CRLF Injection / HTTP Response Splitting.

"""
import re
from urllib.parse import urlparse
from flask import Blueprint, Response, redirect, request

crlf_bp = Blueprint("crlf_injection", __name__)

@crlf_bp.route("/go")
def go():

    # Input Url parameter
    target_url = request.args.get("url", "/")

    # 2. Check CRLF Injection  (\r veya \n)
    if re.search(r"[\r\n]", target_url):
        return Response("Invalid redirect target", status=400)

    # 3. URL Parse ve Domain/Format check
    from urllib.parse import urlparse
    try:
        parsed = urlparse(target_url)

        # Tam domain verilmişse ve whitelist'te değilse engelle
        if parsed.netloc and parsed.netloc.split(":")[0] not in ALLOWED_HOSTS:
            return Response("Untrusted redirect target", status=400)

        # Şemasız relative path gelmişse '/' ile başlamasını zorunlu tut
        if not parsed.netloc and not target_url.startswith("/"):
            return Response("Invalid relative URL", status=400)

    except Exception:
        return Response("Malformed URL", status=400)

    return redirect(target_url)
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

