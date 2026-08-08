"""AI reviewer — sends code diffs to an LLM and parses structured feedback."""

import json
import httpx

from app.config import get_settings

settings = get_settings()

SYSTEM_PROMPT = """You are a code reviewer. Analyze the diff and find real issues.
Focus on: bugs, security vulnerabilities, performance problems, and bad practices.
Skip nitpicks and style-only stuff unless it's egregious.

For each issue found, return JSON like this:
{
  "summary": "One paragraph overview of the PR quality",
  "findings": [
    {
      "file_path": "src/whatever.py",
      "line_number": 42,
      "severity": "high",
      "category": "security",
      "title": "SQL injection via string concatenation",
      "description": "User input flows directly into the query without sanitization.",
      "suggestion": "Use parameterized queries instead."
    }
  ]
}

Severity levels: critical, high, medium, low, info
Categories: bug, security, performance, style, duplication, best_practice

If the code is fine, return: {"summary": "Looks good. No issues found.", "findings": []}
Return ONLY valid JSON. No markdown, no explanation outside the JSON.
"""


class AIReviewer:
    """Handles sending diffs to the configured LLM and parsing the response."""

    def __init__(self):
        self.use_ollama = bool(settings.ollama_base_url and not settings.openai_api_key)

    async def review_diff(self, diff: str, pr_title: str = "") -> dict:
        """Send a diff to the LLM, get back structured findings."""
        prompt = f"PR: {pr_title}\n\nDiff:\n{diff}"

        if self.use_ollama:
            return await self._call_ollama(prompt)
        else:
            return await self._call_openai(prompt)

    async def _call_ollama(self, prompt: str) -> dict:
        """Call a local Ollama instance."""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    f"{settings.ollama_base_url}/api/generate",
                    json={
                        "model": settings.ollama_model,
                        "prompt": f"{SYSTEM_PROMPT}\n\n{prompt}",
                        "stream": False,
                        "format": "json",
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return self._parse_response(data.get("response", ""))
        except Exception as e:
            return {"summary": f"Ollama call failed: {e}", "findings": []}

    async def _call_openai(self, prompt: str) -> dict:
        """Call OpenAI (or Azure OpenAI) API."""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        try:
            resp = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            content = resp.choices[0].message.content
            return self._parse_response(content)
        except Exception as e:
            return {"summary": f"OpenAI call failed: {e}", "findings": []}

    def _parse_response(self, raw: str) -> dict:
        """Try to parse the LLM output as JSON. Be forgiving."""
        try:
            result = json.loads(raw)
            # Make sure the structure is what we expect
            if "summary" not in result:
                result["summary"] = "Review complete."
            if "findings" not in result:
                result["findings"] = []
            return result
        except json.JSONDecodeError:
            return {"summary": "AI returned non-JSON response.", "findings": []}
