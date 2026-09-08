from __future__ import annotations

import copy
import importlib.util
import inspect
import sys
from pathlib import Path
from types import ModuleType

from runner.languages.base import LanguageAdapter
from runner.models import CaseResult, Problem, TestCase
from runner.serialization import to_json_value


class PythonAdapter(LanguageAdapter):
    name = "python"

    def run(self, problem: Problem, cases: list[TestCase]) -> list[CaseResult]:
        module = self._load_module(problem.solution_path(self.name), problem)
        solution_type = getattr(module, problem.class_name, None)
        if solution_type is None:
            raise ValueError(
                f"{problem.solution_path(self.name)} does not define "
                f"{problem.class_name}"
            )

        solution = solution_type()
        method = getattr(solution, problem.method_name, None)
        if method is None or not callable(method):
            raise ValueError(
                f"{problem.class_name} does not define callable method "
                f"{problem.method_name}"
            )

        signature = inspect.signature(method)
        results: list[CaseResult] = []
        for case in cases:
            try:
                arguments = copy.deepcopy(case.arguments)
                signature.bind(*arguments)
                actual = to_json_value(method(*arguments))
                results.append(CaseResult(case=case, actual=actual))
            except Exception as error:
                results.append(CaseResult(case=case, error=error))
        return results

    @staticmethod
    def _load_module(path: Path, problem: Problem) -> ModuleType:
        if not path.is_file():
            raise FileNotFoundError(f"Python solution not found: {path}")

        module_name = f"leetcode_workspace_{problem.slug.replace('-', '_')}"
        specification = importlib.util.spec_from_file_location(module_name, path)
        if specification is None or specification.loader is None:
            raise ImportError(f"Could not load Python solution: {path}")

        module = importlib.util.module_from_spec(specification)
        sys.modules[module_name] = module
        specification.loader.exec_module(module)
        return module
