from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from runner.models import Problem, ProjectConfig


PROJECT_FILE = "leetcode.toml"
PROBLEMS_DIRECTORY = "problems"
PROBLEM_FILE = "problem.toml"


def repository_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _read_toml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with path.open("rb") as source:
        return tomllib.load(source)


def load_project() -> ProjectConfig:
    root = repository_root()
    raw = _read_toml(root / PROJECT_FILE)
    return ProjectConfig(
        root=root,
        active_problem=str(raw["active_problem"]),
        default_language=str(raw.get("default_language", "python")),
    )


def load_problem(path: Path) -> Problem:
    raw = _read_toml(path / PROBLEM_FILE)
    problem = raw["problem"]
    solution = raw["solution"]
    files = raw.get("files", {})

    return Problem(
        root=path,
        problem_id=int(problem["id"]),
        slug=str(problem["slug"]),
        class_name=str(solution.get("class_name", "Solution")),
        method_name=str(solution["method"]),
        parameter_types=tuple(str(value) for value in solution["parameters"]),
        return_type=str(solution["return_type"]),
        solution_files={str(key): str(value) for key, value in files.items()},
    )


def discover_problems(project: ProjectConfig) -> list[Problem]:
    problem_root = project.root / PROBLEMS_DIRECTORY
    if not problem_root.is_dir():
        return []

    return [
        load_problem(directory)
        for directory in sorted(problem_root.iterdir())
        if directory.is_dir() and (directory / PROBLEM_FILE).is_file()
    ]


def resolve_problem(project: ProjectConfig, reference: str | None) -> Problem:
    requested = reference or project.active_problem
    requested_lower = requested.lower()
    matches = [
        problem
        for problem in discover_problems(project)
        if requested_lower
        in {
            str(problem.problem_id),
            f"{problem.problem_id:04d}",
            problem.slug.lower(),
            problem.key.lower(),
        }
    ]

    if not matches:
        raise ValueError(f"No problem matches {requested!r}")
    if len(matches) > 1:
        choices = ", ".join(problem.key for problem in matches)
        raise ValueError(f"Problem reference {requested!r} is ambiguous: {choices}")
    return matches[0]

