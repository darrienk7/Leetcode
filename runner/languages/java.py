from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from runner.languages.base import LanguageAdapter
from runner.models import CaseResult, Problem, TestCase
from runner.type_system import java_expression, parse_type


PROTOCOL = re.compile(r"__LC_(RESULT|ERROR)__(\d+)\t(.*)")


class JavaAdapter(LanguageAdapter):
    name = "java"

    def prepare(self, problem: Problem, cases: list[TestCase]) -> None:
        javac = shutil.which("javac")
        if javac is None:
            raise RuntimeError("javac was not found on PATH")

        build_directory = self._build_directory(problem)
        classes_directory = build_directory / "classes"
        classes_directory.mkdir(parents=True, exist_ok=True)
        harness_path = build_directory / "Main.java"
        harness_path.write_text(self._harness(problem, cases), encoding="utf-8")

        completed = subprocess.run(
            [
                javac,
                "-g",
                "-d",
                str(classes_directory),
                str(problem.solution_path(self.name)),
                str(harness_path),
            ],
            cwd=problem.root,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            details = completed.stderr.strip() or completed.stdout.strip()
            raise RuntimeError(f"Java compilation failed:\n{details}")

    def run(self, problem: Problem, cases: list[TestCase]) -> list[CaseResult]:
        java = shutil.which("java")
        if java is None:
            raise RuntimeError("java was not found on PATH")

        self.prepare(problem, cases)
        classes_directory = self._build_directory(problem) / "classes"
        completed = subprocess.run(
            [java, "-cp", str(classes_directory), "Main"],
            cwd=problem.root,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            details = completed.stderr.strip() or completed.stdout.strip()
            raise RuntimeError(f"Java execution failed:\n{details}")
        return self._parse_results(cases, completed.stdout)

    @staticmethod
    def _build_directory(problem: Problem) -> Path:
        return problem.root.parent.parent / "build" / "current" / "java"

    @staticmethod
    def _parse_results(cases: list[TestCase], output: str) -> list[CaseResult]:
        parsed: dict[int, CaseResult] = {}
        for line in output.splitlines():
            match = PROTOCOL.search(line)
            if match is None:
                continue
            kind, raw_index, payload = match.groups()
            index = int(raw_index)
            if index >= len(cases):
                continue
            if kind == "ERROR":
                parsed[index] = CaseResult(
                    case=cases[index], error=RuntimeError(payload)
                )
            else:
                parsed[index] = CaseResult(
                    case=cases[index], actual=json.loads(payload)
                )

        return [
            parsed.get(
                index,
                CaseResult(
                    case=case,
                    error=RuntimeError("Java harness did not return a result"),
                ),
            )
            for index, case in enumerate(cases)
        ]

    @staticmethod
    def _harness(problem: Problem, cases: list[TestCase]) -> str:
        parameter_types = [parse_type(value) for value in problem.parameter_types]
        case_blocks: list[str] = []
        for index, case in enumerate(cases):
            arguments = ", ".join(
                java_expression(value, type_ref)
                for value, type_ref in zip(case.arguments, parameter_types, strict=True)
            )
            case_blocks.append(
                f"""
        try {{
            Object result = solution.{problem.method_name}({arguments});
            System.out.println("\\n__LC_RESULT__{index}\\t" + toJson(result));
        }} catch (Throwable error) {{
            System.out.println("\\n__LC_ERROR__{index}\\t"
                + error.getClass().getSimpleName() + ": " + error.getMessage());
        }}"""
            )

        return f"""import java.lang.reflect.Array;
import java.util.Iterator;

public class Main {{
    public static void main(String[] args) {{
        Solution solution = new Solution();
{"".join(case_blocks)}
    }}

    private static String toJson(Object value) {{
        if (value == null) return "null";
        if (value instanceof String || value instanceof Character) {{
            return quote(String.valueOf(value));
        }}
        if (value instanceof Number || value instanceof Boolean) {{
            return String.valueOf(value);
        }}
        if (value.getClass().isArray()) {{
            StringBuilder output = new StringBuilder("[");
            for (int index = 0; index < Array.getLength(value); index++) {{
                if (index > 0) output.append(',');
                output.append(toJson(Array.get(value, index)));
            }}
            return output.append(']').toString();
        }}
        if (value instanceof Iterable<?> iterable) {{
            StringBuilder output = new StringBuilder("[");
            Iterator<?> iterator = iterable.iterator();
            while (iterator.hasNext()) {{
                output.append(toJson(iterator.next()));
                if (iterator.hasNext()) output.append(',');
            }}
            return output.append(']').toString();
        }}
        throw new IllegalArgumentException(
            "Cannot serialize return value of type " + value.getClass().getName()
        );
    }}

    private static String quote(String value) {{
        StringBuilder output = new StringBuilder("\\\"");
        for (int index = 0; index < value.length(); index++) {{
            char character = value.charAt(index);
            switch (character) {{
                case '\\"' -> output.append("\\\\\\\"");
                case '\\\\' -> output.append("\\\\\\\\");
                case '\\b' -> output.append("\\\\b");
                case '\\f' -> output.append("\\\\f");
                case '\\n' -> output.append("\\\\n");
                case '\\r' -> output.append("\\\\r");
                case '\\t' -> output.append("\\\\t");
                default -> {{
                    if (character < 0x20) {{
                        output.append(String.format("\\\\u%04x", (int) character));
                    }} else {{
                        output.append(character);
                    }}
                }}
            }}
        }}
        return output.append('\\"').toString();
    }}
}}
"""

