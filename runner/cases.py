from __future__ import annotations

import json

from runner.models import Problem, TestCase


def load_cases(problem: Problem) -> list[TestCase]:
    lines = [
        line.strip()
        for line in problem.cases_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    parameter_count = len(problem.parameter_types)
    if parameter_count == 0:
        if lines:
            raise ValueError("A zero-parameter method cannot consume testcase lines")
        return [TestCase(arguments=())]
    if len(lines) % parameter_count != 0:
        raise ValueError(
            f"Found {len(lines)} nonblank testcase lines, but "
            f"{problem.method_name} requires groups of {parameter_count}"
        )

    cases: list[TestCase] = []
    for start in range(0, len(lines), parameter_count):
        arguments = []
        for line_number, line in enumerate(
            lines[start : start + parameter_count], start=start + 1
        ):
            try:
                arguments.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid testcase value on nonblank line {line_number}: {line}"
                ) from error
        cases.append(TestCase(arguments=tuple(arguments)))
    return cases
