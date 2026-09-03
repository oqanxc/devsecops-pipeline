# DevSecOps Security Pipeline

A GitHub Actions CI/CD pipeline that enforces automated security gates (SAST, SCA, DAST, and secret scanning) across a multi-language application (Python/Flask + Node.js), with supply chain security (image signing, SBOM), Kubernetes-hardened deployment manifests, and a manual approval gate before production.

Every gate below was added incrementally, tested in isolation, and debugged against real (and sometimes false-positive) findings — see the case studies at the bottom for the most instructive ones.

## Architecture


![DevSecOps Pipeline Graph](.github/assets/pipeline-graph.png)

Parallel static gates (SAST, Secrets, SCA, IaC) → DAST fuzzing → Keyless Cosign signing → Auto Staging → Manual Approval for Production.


Branch protection on `main` requires these checks to pass before merge is even possible — this isn't just a CI pipeline that reports problems, it's a gate that blocks bad code from landing.

## Tools

Bandit: Fast AST-level static analysis for Python, targeting pattern-based insecure function calls and rule violations.

CodeQL: Deep semantic SAST focused on taint analysis. Tracks unsanitized input flows from sources to vulnerable sinks across interprocedural call graphs.

TruffleHog: Scans git commit history and CI runners for high-entropy secrets and verified credentials. Enforced locally via a Docker-based pre-commit hook for a shift-left workflow.

Trivy (SCA & Image): Scans the container base image and language-level dependencies (pip/npm) for known CVEs.

Trivy (IaC / Config): Audits Kubernetes deployment and service manifests under k8s/ for privilege escalation, root execution, and missing securityContext parameters.

Trivy (SBOM - CycloneDX): Generates standardized CycloneDX 1.7 JSON specs capturing direct, transitive, and OS-level components for software supply chain visibility.

OWASP ZAP (Full Scan): Active HTTP fuzzing against live services, validating attack vectors like Open Redirects, SSRF, and injection flaws.

Cosign (Sigstore): Keyless container signing and signature verification leveraging GitHub Actions OIDC identity tokens.



## Why two SAST tools

Bandit is fast and Python-only, matching known-bad code patterns line by line. CodeQL builds a queryable model of the code and can trace a value from where it enters (e.g. a request parameter) to where it's used dangerously (e.g. a raw SQL string or a shell command), even across function calls — this catches vulnerability classes Bandit's pattern matching misses, at the cost of being slower and heavier. Running both gives pattern-based and flow-based coverage together.

## Deployment gate

Every image that reaches `Deploy to Production` has already: passed all four security gates, been signed with a verifiable, tamper-evident signature, and been deployed to staging. Production still requires a human to click "Approve" in GitHub — a deliberate policy decision, not a technical necessity, reflecting how real financial/regulated systems treat production pushes.

Note: staging/production deployment steps are currently simulated (no real cluster is connected — GitHub Actions runners can't reach a local machine behind NAT, and no cloud cluster is provisioned for this project). The approval mechanism itself is fully real and functions exactly as it would with a live deployment target.

## Local development

Secrets are checked twice: once locally, before a commit is even created, and again in CI as a backstop.


pip install pre-commit
pre-commit install


This runs Trufflehog (via Docker) on every `git commit`, blocking the commit if a verified secret is detected — catching leaks before they ever reach GitHub's commit history, where they'd persist even after being "removed" in a later commit.

## Case study 1 — CRLF Injection exposed blind spots in both SAST and DAST

An intentional CRLF Injection (unvalidated input passed to `redirect()`) was added to test whether the pipeline catches real vulnerabilities, not just runs without errors.

- **Bandit** never flagged it — Flask's `redirect()` with unvalidated input isn't in its default rule set.
- **ZAP Baseline Scan** missed it entirely — Baseline only passively scans pages discovered via spidering, and nothing links to the vulnerable route.
- Switching to **`zap-full-scan.py`** with the target explicitly pointed at the vulnerable route enabled active fuzzing, which surfaced **Open/External Redirect**, **SSRF**, and a **Format String crash (500)** — all from the same unvalidated input, none of them the exact "CRLF Injection" label, but all real, related findings.

**Takeaway:** a single unvalidated input can manifest as multiple vulnerability classes, and different tools catch different subsets — no single scanner is sufficient alone.

## Case study 2 — Trivy false positives from vendored/leftover packages

After pinning `setuptools` and `msgpack` to patched versions in the Dockerfile, Trivy kept reporting the *old*, vulnerable versions — even though a runtime check (`docker run ... python -c "import X; print(X.__version__)"`) confirmed the correct versions were actually installed and in use.

**Root cause:** Trivy's filesystem scan also matches leftover/vendored copies the application never runs — `pip`'s own internal vendored copy of `msgpack`, and a base-image system-level `setuptools` copy. Neither is ever imported by the Flask app.

**Resolution:**
1. Verified the real, in-use versions at runtime (not just trusted the static scan)
2. Located the duplicate copies with `find / -iname "*msgpack*"` inside the running container
3. Documented and suppressed the confirmed false positives in `.trivyignore`, each with a comment explaining the root cause
4. Discovered `msgpack` wasn't a real application dependency at all (`pip show flask` doesn't list it) — removed it from `requirements.txt` rather than just pinning a "safe" version of something unused

**Takeaway:** a scanner finding is a starting point for investigation, not an instruction to patch on sight. Suppressing a finding is only correct once it's proven to be a false positive, with evidence — not assumed.

## Case study 3 — SAST tools don't need to be told to fail

Trivy required an explicit `exit-code: '1'` to actually block a pipeline on findings (it defaults to reporting only). Bandit needed no such configuration — a SQL injection endpoint (raw string concatenation into a query) was enough to make Bandit exit non-zero and fail the job natively. Different tools have different default postures on "found something bad" — this has to be verified per tool rather than assumed.

## Roadmap

**Done**
-  Four independent, parallel security gates (SAST ×2, SCA, DAST, Secrets)
-  Kubernetes manifests (Deployment, Service, NetworkPolicy, RBAC) with security hardening — non-root, read-only filesystem, resource limits, restricted egress
-  `trivy config` scan of Kubernetes manifests as a CI job
-  Keyless container signing (Cosign) + verification
-  SBOM generation (CycloneDX)
-  Staging/production environments with a manual approval gate for production
-  Email notification on pipeline failure
-  Pre-commit hook for local secret scanning (Docker-based Trufflehog)
-  Dependabot for automated dependency updates

**Planned**
- Re-architect the demo application into a fintech-style microservice setup (auth service with JWT, payment/transfer endpoint, balance query service, API gateway) to demonstrate security patterns relevant to regulated financial systems (IDOR, token handling, PCI-DSS-adjacent controls)
- AI-assisted triage — LLM-based summarization and prioritization of scan findings on each PR
- Real cloud-hosted staging/production clusters to replace the current simulated deploy steps

## Running locally

```bash
docker build -t devsecops-demo-app:latest .
docker run -d --name test-app -p 5000:5000 devsecops-demo-app:latest
```
