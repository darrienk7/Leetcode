# LeetCode Workbench

A problem-first LeetCode environment with Python as the orchestration layer.
Solutions may be written in multiple languages while sharing the same problem
metadata and test cases.

## Current commands

Run these commands from the repository root:

```powershell
python -m runner list
python -m runner run
python -m runner test
python -m runner test 1 --case 2
python -m runner test --language java
python -m runner test --language cpp
python -m runner test --all
```

`leetcode.toml` selects the active problem and default language. Each directory
under `problems/` contains a `problem.toml`, a `cases.json`, and one or more
solution files.

## Debugging

Select **LeetCode: Debug Python**, **LeetCode: Debug Java**, or
**LeetCode: Debug C++** in VS Code and press F5. Compiled-language debug
configurations first ask the Python runner to generate and compile their harness.

## Migration status

- Python runner and adapter: integrated
- Java adapter and debugger: integrated
- C++ adapter and debugger: integrated (MSVC on Windows; GCC/Clang fallback)

The original `Python/`, `Java/`, and `cpp/` directories remain temporarily as
migration references.

