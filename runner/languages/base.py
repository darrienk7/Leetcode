from __future__ import annotations

from abc import ABC, abstractmethod

from runner.models import CaseResult, Problem, TestCase


class LanguageAdapter(ABC):
    name: str

    def prepare(self, problem: Problem, cases: list[TestCase]) -> None:
        """Prepare generated files or compiled artifacts for a run."""

    @abstractmethod
    def run(self, problem: Problem, cases: list[TestCase]) -> list[CaseResult]:
        """Run cases against one solution implementation."""
