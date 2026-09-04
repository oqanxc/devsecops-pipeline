import os
import json
import requests

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

def read_findings():
    """SARIF dosyalarından bulguları okur, basit bir metne çevirir."""
    findings = []
    for filename in ["bandit-results.sarif", "trivy-results.sarif"]:
        if os.path.exists(filename):
            with open(filename) as f:
                data = json.load(f)
                for run in data.get("runs", []):
                    for result in run.get("results", []):
                        findings.append({
                            "tool": run.get("tool", {}).get("driver", {}).get("name", "unknown"),
                            "message": result.get("message", {}).get("text", ""),
                            "rule": result.get("ruleId", "")
                        })
    return findings

def build_prompt(findings):
    findings_text = "\n".join(
        f"- [{f['tool']}] {f['rule']}: {f['message']}" for f in findings
    )
    return f"""You are a security triage assistant. Below are automated scan findings 
from a CI/CD pipeline. For each, briefly assess: (1) likely severity/priority, 
(2) whether it looks like a real risk or possible false positive, (3) one-line 
suggested next step. Keep the whole response under 300 words.

Findings:
{findings_text}
"""

def call_gemini(prompt):
    response = requests.post(
        GEMINI_URL,
        json={"contents": [{"parts": [{"text": prompt}]}]}
    )
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

def main():
    findings = read_findings()
    if not findings:
        print("No findings to triage.")
        return
    prompt = build_prompt(findings)
    summary = call_gemini(prompt)
    with open("ai_triage_summary.md", "w") as f:
        f.write("## 🤖 AI Triage Summary\n\n" + summary)

if __name__ == "__main__":
    main()