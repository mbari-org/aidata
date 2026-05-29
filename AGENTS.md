# AGENTS.md

## Project overview

**mbari-aidata** — CLI for ETL and dataset download on MBARI AI workflows (Tator, Redis, COCO/VOC/CIFAR export, localization crops, etc.). Python 3.10+, Poetry, semantic-release on `main`.

**Architecture map:** `graphify-out/GRAPH_REPORT.md`; refresh with `graphify update .` after code changes.

---

## File headers (required)

Add this 3-line header to **every new or substantially edited** Python module under `mbari_aidata/` and `tests/`:

```python
# mbari_aidata, Apache-2.0 license
# Filename: <path relative to mbari_aidata/ or tests/>
# Description: <one-line summary of the module>
```

Example (`generators/utils.py`):

```python
# mbari_aidata, Apache-2.0 license
# Filename: generators/utils.py
# Description: Algorithms to run on lists of localizations to combine them and crop frames
```

---

## Commits (semantic-release)

Use **Angular-style** commit messages so `python-semantic-release` can version correctly (`pyproject.toml`).

**Format:** `<type>[optional scope]: <description>`

**Allowed types:** `feat`, `fix`, `perf`, `docs`, `build`, `ci`, `chore`, `style`, `refactor`, `test`

| Type | Release impact |
|------|----------------|
| `feat` | Minor bump |
| `fix`, `perf` | Patch bump |
| Others | Typically no version bump (see changelog exclude patterns) |

**Examples:**

- `feat: add ROI crop padding option for VOC export`
- `fix(generators): clip bbox to frame bounds in build_roi_crop_filter`
- `test: cover white-fill padding in roi crop filter`

Do **not** use ad-hoc prefixes (`Update`, `WIP`, version-only messages) for changes that should ship.

---

## Pull requests

- **Max size:** 400 lines changed (additions + deletions) per PR. Split larger work into stacked or sequential PRs.
- **Labels (required):** Apply GitHub labels in this form before requesting review:

| Label | Meaning (pick one per dimension) |
|-------|----------------------------------|
| `type/feature` | New capability |
| `type/fix` | Bug fix |
| `type/docs` | Documentation only |
| `type/refactor` | Behavior-preserving restructure |
| `type/test` | Tests only |
| `type/chore` | Tooling, deps, CI |
| `scope/commands` | `mbari_aidata/commands/` |
| `scope/generators` | `mbari_aidata/generators/` |
| `scope/plugins` | `mbari_aidata/plugins/` |
| `scope/predictors` | `mbari_aidata/predictors/` |
| `scope/tests` | `tests/` |
| `scope/infra` | CI, Docker, packaging |
| `impact/low` | Small, localized risk |
| `impact/medium` | Moderate behavior or API surface |
| `impact/high` | Breaking or wide blast radius |
| `status/needs-review` | Ready for human review |

Example set: `type/feature`, `scope/generators`, `impact/medium`, `status/needs-review`

---

## Testing

Run tests from the repo root after substantive changes (see `README.md` / project docs for full setup).

---

## Graphify

Before answering architecture or “how does X connect to Y?” questions, read `graphify-out/GRAPH_REPORT.md`. After editing code in a session, run `graphify update .` (AST-only, no API cost).
