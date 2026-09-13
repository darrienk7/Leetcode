from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from runner.cases import load_cases
from runner.config import load_project, load_workspace
from runner.models import Problem
from runner.type_system import parse_type


class WorkspaceTests(unittest.TestCase):
    def test_workspace_manifest_and_solution_files_are_loadable(self) -> None:
        project = load_project()
        problem = load_workspace(project)

        self.assertTrue(problem.title)
        self.assertTrue(problem.method_name)
        cases = load_cases(problem)
        self.assertTrue(cases)
        self.assertEqual(len(problem.parameter_types), len(cases[0].arguments))
        self.assertTrue(problem.solution_files)
        for language in problem.solution_files:
            self.assertTrue(problem.solution_path(language).is_file())

    def test_solution_paths_cannot_leave_workspace(self) -> None:
        workspace = Path(__file__).resolve().parent.parent / "workspace"
        problem = Problem(
            root=workspace,
            frontend_id="",
            title="Path safety test",
            slug="path-safety-test",
            source_provider="test",
            source_url="",
            is_placeholder=True,
            class_name="Solution",
            method_name="solve",
            parameter_types=(),
            return_type="int",
            solution_files={"python": "../outside.py"},
        )

        with self.assertRaisesRegex(ValueError, "leaves the workspace"):
            problem.solution_path("python")

        with self.assertRaisesRegex(
            ValueError,
            "Active problem 'Path safety test' has no 'java' solution configured",
        ):
            problem.solution_path("java")

    def test_nested_canonical_types_are_supported(self) -> None:
        parsed = parse_type("list[list[int]]")

        self.assertEqual("list", parsed.name)
        self.assertEqual("list", parsed.item.name)
        self.assertEqual("int", parsed.item.item.name)

    def test_single_parameter_values_are_sequential_cases(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            (workspace / "testcases.txt").write_text(
                "1002\n\n998\n", encoding="utf-8"
            )
            problem = Problem(
                root=workspace,
                frontend_id="",
                title="Sequential testcase test",
                slug="sequential-testcase-test",
                source_provider="test",
                source_url="",
                is_placeholder=True,
                class_name="Solution",
                method_name="solve",
                parameter_types=("int",),
                return_type="int",
                solution_files={},
            )

            cases = load_cases(problem)

        self.assertEqual([(1002,), (998,)], [case.arguments for case in cases])


if __name__ == "__main__":
    unittest.main()
