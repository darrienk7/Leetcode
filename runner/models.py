from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProjectConfig:
    root: Path
    active_problem: str
    default_language: str


@dataclass(frozen=True)
class Problem:
    root: Path
    problem_id: int
    slug: str
    class_name: str
    method_name: str
    parameter_types: tuple[str, ...]
    return_type: str
    solution_files: dict[str, str]

    @property
    def key(self) -> str:
        return f"{self.problem_id:04d}-{self.slug}"

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
        return self.root / filename


@dataclass(frozen=True)
class TestCase:
    arguments: tuple[Any, ...]


@dataclass(frozen=True)
class CaseResult:
    case: TestCase
    actual: Any = None
    error: Exception | None = None
