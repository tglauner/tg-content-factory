from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class OpenAIClient:
    api_key: str
    model: str = "gpt-5.2"
    base_url: str = "https://api.openai.com/v1"

    @classmethod
    def from_env(cls) -> "OpenAIClient":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required.")
        model = os.getenv("OPENAI_MODEL", "gpt-5.2")
        return cls(api_key=api_key, model=model)

    def generate_ideas(self, count: int) -> List[str]:
        if os.getenv("TG_OPENAI_MOCK"):
            return [f"Mock idea {idx + 1}" for idx in range(count)]
        prompt = (
            "Generate course marketing video ideas. "
            f"Return exactly {count} short idea prompts as a JSON array of strings."
        )
        data = self._responses_call(prompt)
        return _ensure_list(data, count, label="idea prompts")

    def generate_script(self, idea_prompt: str, template: str) -> str:
        if os.getenv("TG_OPENAI_MOCK"):
            return f"Hook: {idea_prompt}\nBeats: 1, 2, 3\nCTA: Learn more."
        prompt = (
            "Write a short vertical-video script for this idea. "
            "Include a hook, 3 beats, and a CTA. "
            f"Idea: {idea_prompt}\nTemplate: {template}\n"
            "Return plain text."
        )
        data = self._responses_call(prompt)
        if not isinstance(data, str):
            raise ValueError("Expected script text response.")
        return data.strip()

    def _responses_call(self, prompt: str) -> Any:
        payload = {
            "model": self.model,
            "input": prompt,
        }
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/responses",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = json.loads(response.read().decode("utf-8"))
        return _extract_output_text(raw)


def _extract_output_text(response: Dict[str, Any]) -> Any:
    outputs = response.get("output", [])
    text_chunks: List[str] = []
    for output in outputs:
        for part in output.get("content", []):
            if part.get("type") == "output_text":
                text_chunks.append(part.get("text", ""))
    text = "".join(text_chunks).strip()
    if text.startswith("[") or text.startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text
    return text


def _ensure_list(value: Any, count: int, label: str) -> List[str]:
    if not isinstance(value, list):
        raise ValueError(f"Expected list for {label}.")
    if len(value) != count:
        raise ValueError(f"Expected {count} items for {label}, got {len(value)}.")
    return [str(item).strip() for item in value]
