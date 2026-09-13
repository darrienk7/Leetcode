# Leetcode

Leetcode environment to test and debug solutions, custom runner so typing solution into specified class works seamlessly.


<<<<<<< HEAD
<<<<<<< HEAD
## Files you edit

Choose one solution file and replace its placeholder method:

- Python: `workspace/solutions/python/solution.py`
- Java: `workspace/solutions/java/Solution.java`
- C++: `workspace/solutions/cpp/Solution.cpp`

For manual problem changes, also update `workspace/problem.toml` and paste the
raw testcase values into `workspace/testcases.txt`. Use one argument per
nonblank line. The runner groups them sequentially according to the method
signature and prints each result; expected outputs are not required. Generated
harnesses and binaries live under ignored
`build/`; never edit them.

## Commands

Run commands from the repository root:
=======
Run these commands from the repository root:
>>>>>>> parent of 82822b9 (remove unused files, refactor system usage)

```powershell
python -m runner list
python -m runner run
<<<<<<< HEAD
python -m runner run --case 2
python -m runner run --language java
python -m runner run --language cpp
python -m runner run --all
=======
python -m runner test
python -m runner test 1 --case 2
python -m runner test --language java
python -m runner test --language cpp
python -m runner test --all
>>>>>>> parent of 82822b9 (remove unused files, refactor system usage)
```

`leetcode.toml` selects the active problem and default language. Each directory
under `problems/` contains a `problem.toml`, a `cases.json`, and one or more
solution files.

## Debugging

Select **LeetCode: Debug Python**, **LeetCode: Debug Java**, or
**LeetCode: Debug C++** in VS Code and press F5. Compiled-language debug
configurations first ask the Python runner to generate and compile their harness.

<<<<<<< HEAD
For IntelliJ IDEA, open this repository as the project and edit only
`workspace/solutions/java/Solution.java`. Run tests from IntelliJ's terminal
with `python -m runner run --language java`. The runner supplies `Main`
automatically; do not create or maintain a separate Java entry point.
=======
## Migration status
>>>>>>> parent of 82822b9 (remove unused files, refactor system usage)

- Python runner and adapter: integrated
- Java adapter and debugger: integrated
- C++ adapter and debugger: integrated (MSVC on Windows; GCC/Clang fallback)

The original `Python/`, `Java/`, and `cpp/` directories remain temporarily as
migration references.
=======
Copy and paste the test cases into testcase.txt
>>>>>>> parent of 68fefbd (first test migration to python based runner)

