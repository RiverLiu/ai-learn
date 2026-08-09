from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


SKILLS_DIR = Path(__file__).parent / "sample_skills"


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    body: str
    path: Path


def parse_skill(path: Path) -> Skill:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path} missing YAML frontmatter")

    _, frontmatter, body = text.split("---\n", 2)
    fields: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()

    name = fields.get("name")
    description = fields.get("description")
    if not name or not description:
        raise ValueError(f"{path} must contain name and description")

    return Skill(name=name, description=description, body=body.strip(), path=path)


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]+", text.lower()))


def score(query: str, skill: Skill) -> int:
    query_terms = tokenize(query)
    metadata_terms = tokenize(f"{skill.name} {skill.description}")
    return len(query_terms & metadata_terms)


def load_skills() -> list[Skill]:
    return [parse_skill(path) for path in sorted(SKILLS_DIR.glob("*/SKILL.md"))]


def select_skill(query: str, skills: list[Skill]) -> Skill | None:
    ranked = sorted(
        ((score(query, skill), skill) for skill in skills),
        key=lambda item: item[0],
        reverse=True,
    )
    best_score, best_skill = ranked[0]
    return best_skill if best_score > 0 else None


def preview_body(skill: Skill, max_lines: int = 6) -> str:
    lines = skill.body.splitlines()
    return "\n".join(lines[:max_lines])


def main() -> None:
    skills = load_skills()
    queries = [
        "帮我清理这个 sales.csv，检查缺失值并规范列名",
        "Review this FastAPI pull request for security and missing tests",
        "把这份产品实验数据整理成 CEO 能看的 weekly product report",
    ]

    print(f"Loaded metadata for {len(skills)} skills.\n")

    for query in queries:
        skill = select_skill(query, skills)
        print(f"User request: {query}")
        if skill is None:
            print("Matched skill: <none>\n")
            continue

        print(f"Matched skill: {skill.name}")
        print("Loaded SKILL.md body preview:")
        print(preview_body(skill))
        print("-" * 60)


if __name__ == "__main__":
    main()
