# API Phase Plan

## Goal

Accept one LeetCode problem URL and safely refresh the single active
`workspace/` with its metadata, signature, starter code, and example cases.
This phase is planned but **not implemented**.

The intended command is:

```powershell
python -m runner load https://leetcode.com/problems/two-sum/
```

`load` will update active workspace state; it will not create an archive.

## Feasibility checkpoint

Before implementing a network provider, verify that LeetCode offers an
authorized, documented access route for the required fields. LeetCode's current
Terms of Service explicitly prohibit crawling, scraping, and spidering the
service: <https://leetcode.com/terms/>. Its website uses internal endpoints,
but an undocumented internal endpoint must not be treated as a stable public
API.

If no permitted public interface exists, the first provider should accept a
user-supplied export or pasted payload instead of automating page extraction.
The rest of this design remains the same because providers are isolated from
workspace updates.

## Proposed boundaries

```text
problem URL or user export
          |
          v
ProblemProvider.fetch()
          |
          v
validated ProblemPayload
          |
          v
WorkspaceUpdatePlan.preview()
          |
      user approval when a solution would be replaced
          |
          v
atomic workspace update
```

### Provider

The provider obtains raw data only. Its output must not contain filesystem
paths or commands. A normalized payload should include:

- frontend id, title, slug, and canonical URL;
- class and method names;
- ordered canonical parameter types and return type;
- starter code keyed by language;
- structured example inputs and expected outputs when reliably available;
- provider name and retrieval timestamp.

### Normalizer

The normalizer converts provider-specific types into the runner's canonical
type vocabulary. Initial support should remain deliberately small:

- `bool`, `int`, `long`, `float`, and `string`;
- nested `list[T]` values;
- later: `listnode[T]`, `treenode[T]`, tuples, and in-place/void methods.

Unknown or ambiguous types must stop the import with a clear message rather
than generating code that merely looks plausible.

### Workspace updater

The updater builds a change plan before writing anything. It owns only:

- `workspace/problem.toml`;
- `workspace/cases.json`;
- starter-code suggestions staged outside the editable solution paths.

Existing files under `workspace/solutions/` are user work. Default behavior:

1. Never overwrite them silently.
2. Place fetched starter code in a temporary preview area.
3. Replace a solution only after explicit user confirmation or a dedicated
   `--replace-solutions` option.
4. Write metadata and cases to temporary sibling files, validate them, and use
   atomic replacement only after every file is ready.

## URL and network safety

- Accept HTTPS URLs only.
- Allowlist exact supported hostnames and validate the `/problems/<slug>/`
  shape.
- Reject redirects to a different hostname.
- Set short connection/read timeouts and a small response-size limit.
- Use a descriptive user agent and conservative request rate.
- Do not store session cookies, CSRF tokens, passwords, or API secrets in the
  repository, manifest, generated files, logs, or command history.
- Keep authentication optional and isolated behind the provider boundary.

## Delivery stages

1. Define immutable `ProblemPayload` and `WorkspaceUpdatePlan` models.
2. Implement a local JSON fixture provider and exhaustive validation tests.
3. Implement preview/diff output and atomic workspace updates.
4. Add solution-file overwrite protection tests.
5. Re-check LeetCode's supported interfaces and Terms of Service.
6. Implement an authorized URL provider, or retain user-export import if no
   supported endpoint exists.
7. Add `runner load URL`, dry-run mode, timeouts, and actionable errors.

The local fixture provider comes first so the entire import pipeline can be
tested without network access, credentials, endpoint instability, or load on an
external service.

