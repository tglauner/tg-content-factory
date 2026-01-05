from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VideoTemplate:
    name: str
    description: str
    hook: str
    structure: str

    def render(self, idea: str) -> str:
        return (
            f"Template: {self.name}\n"
            f"Idea: {idea}\n"
            f"Hook: {self.hook}\n"
            f"Structure: {self.structure}\n"
        )


TEMPLATES = [
    VideoTemplate(
        name="Lightning Lecture",
        description="60-second recap with a striking hook and takeaway.",
        hook="Ask a surprising question about the topic.",
        structure="Hook → 3 key beats → 1 actionable takeaway",
    ),
    VideoTemplate(
        name="Deep Dive Teaser",
        description="90-second teaser that points to a longer lecture.",
        hook="Open with a surprising stat or counterintuitive insight.",
        structure="Insight → mini-demo → call to action",
    ),
]


def get_template(name: str) -> VideoTemplate:
    for template in TEMPLATES:
        if template.name == name:
            return template
    raise ValueError(f"Unknown template: {name}")
