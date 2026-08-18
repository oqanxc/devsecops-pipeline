"""
xss.py

Deliberately vulnerable route used to verify that OWASP ZAP (DAST) catches
classic Reflected XSS via unescaped user input in HTML output.

"""

from flask import Blueprint, request

xss_bp = Blueprint("xss", __name__)


@xss_bp.route("/greet")
def greet():
    """
    VULNERABLE ENDPOINT.
    The 'name' query param is inserted directly into an HTML response
    without escaping. 

    Test request:
        http://localhost:5000/greet?name=<script>alert(1)</script>
    """
    name = request.args.get("name", "friend")

    # --- VULNERABLE LINE: unescaped user input rendered as raw HTML ---
    return f"<html><body><h1>Hello, {name}!</h1></body></html>"

    # SAFE ALTERNATIVE (for comparison) 
    # from markupsafe import escape
    # return f"<html><body><h1>Hello, {escape(name)}!</h1></body></html>"