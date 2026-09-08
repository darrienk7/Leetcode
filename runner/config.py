from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from runner.models import Problem, ProjectConfig
from runner.type_system import parse_type


PROJECT_FILE = "leetcode.toml"
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
    workspace_name = Path(str(raw.get("workspace_directory", "workspace")))
    if workspace_name.is_absolute():
        raise ValueError("workspace_directory must be relative to the repository")
    workspace = (root / workspace_name).resolve()
    try:
        workspace.relative_to(root.resolve())
    except ValueError as error:
        raise ValueError(
            "workspace_directory must stay inside the repository"
        ) from error
    return ProjectConfig(
        root=root,
        workspace=workspace,
        default_language=str(raw.get("default_language", "python")),
    )


def load_problem(path: Path) -> Problem:
    raw = _read_toml(path / PROBLEM_FILE)
    problem = raw["problem"]
    source = raw.get("source", {})
    solution = raw["solution"]
    files = raw.get("files", {})
    parameter_types = tuple(str(value) for value in solution["parameters"])
    return_type = str(solution["return_type"])
    for type_expression in (*parameter_types, return_type):
        parse_type(type_expression)

    return Problem(
        root=path,
        frontend_id=str(problem.get("frontend_id", "")),
        title=str(problem["title"]),
        slug=str(problem["slug"]),
        source_provider=str(source.get("provider", "manual")),
        source_url=str(source.get("url", "")),
        is_placeholder=bool(source.get("placeholder", False)),
        class_name=str(solution.get("class_name", "Solution")),
        method_name=str(solution["method"]),
        parameter_types=parameter_types,
        return_type=return_type,
        solution_files={str(key): str(value) for key, value in files.items()},
    )


def load_workspace(project: ProjectConfig) -> Problem:
    if not project.workspace.is_dir():
        raise FileNotFoundError(f"Workspace directory not found: {project.workspace}")
    return load_problem(project.workspace)
