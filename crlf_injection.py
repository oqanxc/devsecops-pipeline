"""
crlf_injection.py

Intentionally vulnerable route used to test whether the pipeline
(Bandit, ZAP) catches CRLF Injection / HTTP Response Splitting.

"""

from flask import Blueprint, request, redirect, Response

crlf_bp = Blueprint("crlf_injection", __name__)


@crlf_bp.route("/go")
def go():
    """
    VULNERABLE ENDPOINT.

    The 'url' parameter is passed straight into redirect with no
    validation. If it contains \r\n, an attacker can inject a
    malicious header/cookie into the response.

    Test request:
        http://localhost:5000/go?url=http://example.com%0d%0aSet-Cookie:%20injected=true
    """
    target_url = request.args.get("url", "/")

    #  no validation before redirectt
    return redirect(target_url)

    # --- SAFE ALTERNATIVE (for comparison) ---
    # import re
    # ALLOWED_HOSTS = {"example.com", "my-domain.com"}
    # if re.search(r"[\r\n]", target_url):
    #     return Response("Invalid redirect target", status=400)
    # parsed = urlparse(target_url)
    # if parsed.netloc and parsed.netloc not in ALLOWED_HOSTS:
    #     return Response("Untrusted redirect target", status=400)
    # return redirect(target_url)