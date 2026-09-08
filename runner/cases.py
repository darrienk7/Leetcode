from __future__ import annotations

import json
from typing import Any

from runner.models import MISSING, Problem, TestCase


def load_cases(problem: Problem) -> list[TestCase]:
    with problem.cases_path.open(encoding="utf-8") as source:
        raw_cases: Any = json.load(source)

    if not isinstance(raw_cases, list):
        raise ValueError(f"{problem.cases_path} must contain a JSON array")

    cases: list[TestCase] = []
    for index, raw_case in enumerate(raw_cases, start=1):
        if not isinstance(raw_case, dict):
            raise ValueError(f"Case {index} must be a JSON object")

        arguments = raw_case.get("args")
        if not isinstance(arguments, list):
            raise ValueError(f"Case {index} must contain an 'args' array")
        if len(arguments) != len(problem.parameter_types):
            raise ValueError(
                f"Case {index} has {len(arguments)} arguments; "
                f"{problem.method_name} expects {len(problem.parameter_types)}"
            )

        cases.append(
            TestCase(
                name=str(raw_case.get("name", f"case {index}")),
                arguments=tuple(arguments),
                expected=raw_case.get("expected", MISSING),
            )
        )
    return cases

