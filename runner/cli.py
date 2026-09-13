from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from runner.cases import load_cases
from runner.config import load_project, load_workspace
from runner.languages import get_adapter
from runner.models import CaseResult


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lc",
        description="Run LeetCode solutions through a language-neutral interface.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("info", help="show the active workspace")

    for name, help_text in (
        ("prepare", "prepare generated files and compiled artifacts"),
        ("run", "run testcases and print their results"),
    ):
        command = commands.add_parser(name, help=help_text)
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
        print(f"ERROR {index}: {result.error}")
    else:
        print(_format(result.actual))


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        project = load_project()

        problem = load_workspace(project)

        if arguments.command == "info":
            marker = " (placeholder)" if problem.is_placeholder else ""
            languages = ", ".join(sorted(problem.solution_files))
            print(f"Active workspace: {problem.display_name}{marker}")
            print(f"Languages: {languages}")
            if problem.source_url:
                print(f"Source: {problem.source_url}")
            return 0

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
                print(f"Prepared {problem.display_name} for {language}")
                continue

            results = adapter.run(problem, cases)
            if len(languages) > 1:
                print(f"== {language} ==")
            for index, result in enumerate(results, start=1):
                _print_run_result(index, result)
            exit_code |= int(any(result.error is not None for result in results))
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
