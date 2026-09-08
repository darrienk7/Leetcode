from __future__ import annotations

import unittest
from pathlib import Path

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
        self.assertTrue(load_cases(problem))
        self.assertEqual({"cpp", "java", "python"}, set(problem.solution_files))
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

    def test_nested_canonical_types_are_supported(self) -> None:
        parsed = parse_type("list[list[int]]")

        self.assertEqual("list", parsed.name)
        self.assertEqual("list", parsed.item.name)
        self.assertEqual("int", parsed.item.item.name)


if __name__ == "__main__":
    unittest.main()

