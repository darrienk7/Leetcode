# LeetCode Workbench

A reusable, single-problem coding workspace. Python is the orchestration layer;
solutions can be written and debugged in Python, Java, or C++ against the same
metadata and test cases.

This repository is **not a solution archive**. The content under `workspace/`
represents only the problem currently being worked on. The checked-in Two Sum
files are labeled placeholders so a fresh clone can be tested immediately.

## Files you edit

Choose one solution file and replace its placeholder method:

- Python: `workspace/solutions/python/solution.py`
- Java: `workspace/solutions/java/Solution.java`
- C++: `workspace/solutions/cpp/Solution.cpp`

For manual problem changes, also update `workspace/problem.toml` and
`workspace/cases.json`. Generated harnesses and binaries live under ignored
`build/`; never edit them.

## Commands

Run commands from the repository root:

```powershell
python -m runner info
python -m runner run
python -m runner test
python -m runner test --case 2
python -m runner test --language java
python -m runner test --language cpp
python -m runner test --all
```

`leetcode.toml` selects the workspace directory and default language. You can
change `default_language` while keeping all three solution files available.

## Debugging and IDEs

In VS Code, select **LeetCode: Debug Python**, **LeetCode: Debug Java**, or
**LeetCode: Debug C++**, then press F5. Compiled-language configurations ask the
Python runner to prepare a native harness before their native debugger starts.

For IntelliJ IDEA, open this repository as the project and edit only
`workspace/solutions/java/Solution.java`. Run tests from IntelliJ's terminal
with `python -m runner test --language java`. The runner supplies `Main`
automatically; do not create or maintain a separate Java entry point.

## Future problem-link import

The planned API phase is documented in `docs/API_PHASE.md`. No network client or
LeetCode integration is currently implemented. The design treats solution files
as user-owned and prevents a future importer from overwriting them silently.

