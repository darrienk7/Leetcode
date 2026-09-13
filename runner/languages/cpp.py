from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from runner.languages.base import LanguageAdapter
from runner.models import CaseResult, Problem, TestCase
from runner.type_system import cpp_expression, parse_type


PROTOCOL = re.compile(r"__LC_(RESULT|ERROR)__(\d+)\t(.*)")


class CppAdapter(LanguageAdapter):
    name = "cpp"

    def prepare(self, problem: Problem, cases: list[TestCase]) -> None:
        build_directory = self._build_directory(problem)
        build_directory.mkdir(parents=True, exist_ok=True)
        harness_path = build_directory / "main.cpp"
        harness_path.write_text(self._harness(problem, cases), encoding="utf-8")

        compiler, environment, family = self._compiler()
        executable = self._executable(problem)
        if family == "msvc":
            command = [
                compiler,
                "/nologo",
                "/std:c++20",
                "/EHsc",
                "/utf-8",
                "/Zi",
                "/Od",
                f"/Fe:{executable}",
                f"/Fd:{build_directory / 'leetcode.pdb'}",
                f"/Fo:{build_directory / 'leetcode.obj'}",
                str(harness_path),
            ]
        else:
            command = [
                compiler,
                "-std=c++20",
                "-g",
                "-O0",
                str(harness_path),
                "-o",
                str(executable),
            ]

        completed = subprocess.run(
            command,
            cwd=problem.root.parent.parent,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            details = completed.stderr.strip() or completed.stdout.strip()
            raise RuntimeError(f"C++ compilation failed:\n{details}")

    def run(self, problem: Problem, cases: list[TestCase]) -> list[CaseResult]:
        self.prepare(problem, cases)
        completed = subprocess.run(
            [str(self._executable(problem))],
            cwd=problem.root,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            details = completed.stderr.strip() or completed.stdout.strip()
            raise RuntimeError(f"C++ execution failed:\n{details}")
        return self._parse_results(cases, completed.stdout)

    @staticmethod
    def _build_directory(problem: Problem) -> Path:
        return problem.root.parent.parent / "build" / "current" / "cpp"

    @classmethod
    def _executable(cls, problem: Problem) -> Path:
        suffix = ".exe" if os.name == "nt" else ""
        return cls._build_directory(problem) / f"leetcode{suffix}"

    @staticmethod
    def _compiler() -> tuple[str, dict[str, str] | None, str]:
        if os.name == "nt":
            msvc = CppAdapter._find_msvc()
            if msvc is not None:
                return msvc

        for executable in ("g++", "clang++"):
            compiler = shutil.which(executable)
            if compiler is not None:
                return compiler, None, executable
        raise RuntimeError("No supported C++ compiler was found")

    @staticmethod
    def _find_msvc() -> tuple[str, dict[str, str], str] | None:
        direct = shutil.which("cl")
        if direct is not None:
            return direct, dict(os.environ), "msvc"

        vswhere = Path(
            os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        ) / "Microsoft Visual Studio" / "Installer" / "vswhere.exe"
        if not vswhere.is_file():
            return None

        located = subprocess.run(
            [
                str(vswhere),
                "-latest",
                "-products",
                "*",
                "-requires",
                "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
                "-property",
                "installationPath",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if located.returncode != 0 or not located.stdout.strip():
            return None

        installation = Path(located.stdout.strip().splitlines()[-1])
        candidates = sorted(
            (installation / "VC" / "Tools" / "MSVC").glob(
                "*/bin/Hostx64/x64/cl.exe"
            ),
            reverse=True,
        )
        environment_script = installation / "Common7" / "Tools" / "VsDevCmd.bat"
        if not candidates or not environment_script.is_file():
            return None

        initialized = subprocess.run(
            (
                f'cmd.exe /d /c call "{environment_script}" '
                "-no_logo -arch=x64 >nul && set"
            ),
            capture_output=True,
            text=True,
            check=False,
        )
        if initialized.returncode != 0:
            return None

        environment = dict(os.environ)
        for line in initialized.stdout.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                environment[key] = value
        return str(candidates[0]), environment, "msvc"

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
                    error=RuntimeError("C++ harness did not return a result"),
                ),
            )
            for index, case in enumerate(cases)
        ]

    @staticmethod
    def _harness(problem: Problem, cases: list[TestCase]) -> str:
        parameter_types = [parse_type(value) for value in problem.parameter_types]
        solution_path = problem.solution_path("cpp").resolve().as_posix()
        case_blocks: list[str] = []
        for index, case in enumerate(cases):
            declarations: list[str] = []
            argument_names: list[str] = []
            for argument_index, (value, type_ref) in enumerate(
                zip(case.arguments, parameter_types, strict=True)
            ):
                name = f"argument_{index}_{argument_index}"
                declarations.append(
                    f"        auto {name} = {cpp_expression(value, type_ref)};"
                )
                argument_names.append(name)
            arguments = ", ".join(argument_names)
            declaration_block = "\n".join(declarations)
            case_blocks.append(
                f"""
    try {{
{declaration_block}
        auto result = solution.{problem.method_name}({arguments});
        std::cout << "\\n__LC_RESULT__{index}\\t";
        write_json(result);
        std::cout << '\\n';
    }} catch (const std::exception& error) {{
        std::cout << "\\n__LC_ERROR__{index}\\t" << error.what() << '\\n';
    }}"""
            )

        return f"""#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <unordered_map>
#include <vector>

using namespace std;

#include \"{solution_path}\"

void write_json(std::nullptr_t) {{ std::cout << "null"; }}
void write_json(bool value) {{ std::cout << (value ? "true" : "false"); }}

template <typename Number>
requires std::is_arithmetic_v<Number> && (!std::is_same_v<Number, bool>)
void write_json(Number value) {{ std::cout << value; }}

void write_json(const std::string& value) {{
    std::cout << '"';
    for (char character : value) {{
        switch (character) {{
            case '"': std::cout << "\\\\\\\""; break;
            case '\\\\': std::cout << "\\\\\\\\"; break;
            case '\\b': std::cout << "\\\\b"; break;
            case '\\f': std::cout << "\\\\f"; break;
            case '\\n': std::cout << "\\\\n"; break;
            case '\\r': std::cout << "\\\\r"; break;
            case '\\t': std::cout << "\\\\t"; break;
            default:
                if (static_cast<unsigned char>(character) < 0x20) {{
                    std::cout << "\\\\u"
                              << std::hex << std::setw(4) << std::setfill('0')
                              << static_cast<int>(static_cast<unsigned char>(character))
                              << std::dec << std::setfill(' ');
                }} else {{
                    std::cout << character;
                }}
        }}
    }}
    std::cout << '"';
}}

template <typename Item>
void write_json(const std::vector<Item>& values) {{
    std::cout << '[';
    for (std::size_t index = 0; index < values.size(); ++index) {{
        if (index > 0) std::cout << ',';
        write_json(values[index]);
    }}
    std::cout << ']';
}}

int main() {{
    Solution solution;
{"".join(case_blocks)}
    return 0;
}}
"""
