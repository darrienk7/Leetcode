from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from runner.cases import load_cases
from runner.config import discover_problems, load_project, resolve_problem
from runner.languages import get_adapter
from runner.models import MISSING, CaseResult


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lc",
        description="Run LeetCode solutions through a language-neutral interface.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("list", help="list configured problems")

    for name, help_text in (
        ("prepare", "prepare generated files and compiled artifacts"),
        ("run", "run cases and print their results"),
        ("test", "run cases and compare them with expected results"),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument(
            "problem",
            nargs="?",
            help="problem id, slug, or directory name; defaults to active_problem",
        )
        language_options = command.add_mutually_exclusive_group()
        language_options.add_argument(
            "-l",
            "--language",
            help="solution language; defaults to default_language",
        )
        language_options.add_argument(
            "--all",
            action="store_true",
            dest="all_languages",
            help="run every language configured for the problem",
        )
        command.add_argument(
            "-c",
            "--case",
            type=int,
            dest="case_number",
            help="run only this one-based case number",
        )
    return parser


def _format(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _select_case(results: list, case_number: int | None) -> list:
    if case_number is None:
        return results
    if case_number < 1 or case_number > len(results):
        raise ValueError(
            f"Case number must be between 1 and {len(results)}, got {case_number}"
        )
    return [results[case_number - 1]]


def _print_run_result(index: int, result: CaseResult) -> None:
    if result.error is not None:
        print(f"ERROR {index}: {result.case.name} - {result.error}")
    else:
        print(f"RESULT {index}: {result.case.name} - {_format(result.actual)}")


def _print_test_result(index: int, result: CaseResult) -> None:
    if result.error is not None:
        print(
            f"FAIL  {index}: {result.case.name} - "
            f"{type(result.error).__name__}: {result.error}"
        )
    elif result.case.expected is MISSING:
        print(f"SKIP  {index}: {result.case.name} - no expected value")
    elif result.passed:
        print(f"PASS  {index}: {result.case.name}")
    else:
        print(
            f"FAIL  {index}: {result.case.name}\n"
            f"      expected: {_format(result.case.expected)}\n"
            f"      actual:   {_format(result.actual)}"
        )


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        project = load_project()

        if arguments.command == "list":
            for problem in discover_problems(project):
                active = "*" if problem.key == project.active_problem else " "
                languages = ", ".join(sorted(problem.solution_files))
                print(f"{active} {problem.key} [{languages}]")
            return 0

        problem = resolve_problem(project, arguments.problem)
        cases = _select_case(load_cases(problem), arguments.case_number)
        languages = (
            sorted(problem.solution_files)
            if arguments.all_languages
            else [arguments.language or project.default_language]
        )
        exit_code = 0

        for language_index, language in enumerate(languages):
            if language_index > 0:
                print()
            adapter = get_adapter(language)

            if arguments.command == "prepare":
                adapter.prepare(problem, cases)
                print(f"Prepared {problem.key} for {language}")
                continue

            results = adapter.run(problem, cases)
            print(f"{problem.key} | {language} | {len(results)} case(s)")
            if arguments.command == "run":
                for index, result in enumerate(results, start=1):
                    _print_run_result(index, result)
                exit_code |= int(
                    any(result.error is not None for result in results)
                )
                continue

            for index, result in enumerate(results, start=1):
                _print_test_result(index, result)
            failures = sum(
                result.error is not None
                or (result.case.expected is not MISSING and not result.passed)
                for result in results
            )
            skipped = sum(
                result.error is None and result.case.expected is MISSING
                for result in results
            )
            passed = sum(result.passed for result in results)
            print(
                f"\n{passed} passed, {failures} failed, {skipped} skipped"
            )
            exit_code |= int(failures > 0)
        return exit_code
    except (
        FileNotFoundError,
        ImportError,
        KeyError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
