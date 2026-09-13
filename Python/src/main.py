import inspect
import json
from pathlib import Path

from leetcode_util.adapters import to_json_value
from solution import Solution


TESTCASE_FILE = Path(__file__).resolve().parent.parent.parent / "testcases.txt"


def get_solution_method(solution):
    methods = [
        method
        for name, method in inspect.getmembers(solution, predicate=inspect.ismethod)
        if not name.startswith("_")
    ]

    if not methods:
        raise RuntimeError("Solution has no public methods")

    return methods[0]


def stringify(value):
    value = to_json_value(value)

    if value is None:
        return "null"

    if isinstance(value, bool):
        return str(value).lower()

    if isinstance(value, str):
        return value

    return json.dumps(value)


def main():
    solution = Solution()
    method = get_solution_method(solution)
    parameter_count = len(inspect.signature(method).parameters)

    lines = [
        line.strip()
        for line in TESTCASE_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if len(lines) % parameter_count != 0:
        raise ValueError(
            f"Expected groups of {parameter_count} lines, "
            f"but found {len(lines)} lines"
        )

    for index in range(0, len(lines), parameter_count):
        arguments = [
            json.loads(line)
            for line in lines[index : index + parameter_count]
        ]

        result = method(*arguments)
        print(stringify(result))


if __name__ == "__main__":
    main()