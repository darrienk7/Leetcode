# Active Problem Workspace

This directory is a **single reusable scratch workspace**, not a problem
archive. The checked-in Two Sum content is only a working placeholder.

For normal use, edit only the solution file for your language:

- `solutions/python/solution.py`
- `solutions/java/Solution.java`
- `solutions/cpp/Solution.cpp`

`problem.toml` describes the active method signature and `testcases.txt`
contains raw LeetCode-style inputs. Put one argument on each nonblank line; the
runner groups lines sequentially using the method's parameter count. During the
future API phase, a problem-link importer will update
those two files and may offer new starter-code files. It must not overwrite an
existing solution unless the user explicitly requests replacement.

Generated harnesses and compiled files are written to the repository's ignored
`build/` directory. Do not edit them.
