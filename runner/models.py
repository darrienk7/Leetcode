from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProjectConfig:
    root: Path
    workspace: Path
    default_language: str


@dataclass(frozen=True)
class Problem:
    root: Path
    frontend_id: str
    title: str
    slug: str
    source_provider: str
    source_url: str
    is_placeholder: bool
    class_name: str
    method_name: str
    parameter_types: tuple[str, ...]
    return_type: str
    solution_files: dict[str, str]

    @property
    def display_name(self) -> str:
        identifier = f"{self.frontend_id}. " if self.frontend_id else ""
        return f"{identifier}{self.title}"

    @property
    def cases_path(self) -> Path:
        return self.root / "testcases.txt"

    def solution_path(self, language: str) -> Path:
        try:
            filename = self.solution_files[language]
        except KeyError as error:
            raise ValueError(
                f"Active problem {self.display_name!r} has no "
                f"{language!r} solution configured"
            ) from error
        workspace_root = self.root.resolve()
        candidate = (workspace_root / filename).resolve()
        try:
            candidate.relative_to(workspace_root)
        except ValueError as error:
            raise ValueError(
                f"Solution path for {language!r} leaves the workspace: {filename}"
            ) from error
        return candidate


@dataclass(frozen=True)
class TestCase:
    arguments: tuple[Any, ...]


@dataclass(frozen=True)
class CaseResult:
    case: TestCase
    actual: Any = None
    error: Exception | None = None
