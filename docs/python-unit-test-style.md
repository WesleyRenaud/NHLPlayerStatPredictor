# Python Unit Test Style

Enforced by `tools/lint/pythonUnitTestStyle.py` (`npm run lint:py`).

## Test file names

- One test file per production module.
- Mirror the `api/` path under `tests/api/`.
- Use the `_tests.py` suffix.

| Production file | Test file |
|---|---|
| `api/season.py` | `tests/api/season_tests.py` |
| `api/skater_season_ingester.py` | `tests/api/skater_season_ingester_tests.py` |

The test file stem must match the production module stem exactly. Do not add extra suffixes, and do not create multiple test files for the same production module.

```python
# ❌ BAD — extra suffix
# tests/api/season_label_tests.py

# ✅ GOOD
# tests/api/season_tests.py
```

## Test function names

Default pattern:

`Test_[Method]_Test[Scenario]_Expect[Outcome]`

- **Method** — method or function under test, in PascalCase.
- **Scenario** — input or condition being exercised.
- **Outcome** — expected result or behavior.

```python
def Test_Label_TestCompletedSeason_ExpectHyphenatedLabel() -> None:
   ...

def Test_Pace_TestFullSeason_ExpectScaledTotals() -> None:
   ...
```

Parametrized table-driven tests may use the short form `Test_[Method]` when decorated with `@pytest.mark.parametrize`:

```python
@pytest.mark.parametrize( 'season_id, expected', [ ( 20252026, '2025-26' ) ] )
def Test_Label( season_id: int, expected: str ) -> None:
   ...
```

## Helpers and tests grouped

Keep this top-to-bottom order. Do not place helpers, constants, or fixtures between `Test_` functions.

```
imports
constants
private helpers (def _...)
module-level test data / stubs
@pytest.fixture definitions
all Test_... functions
```

## Imports

All `import` and `from ... import ...` statements must appear at the top of the file, after any `from __future__` imports and the module docstring. Never place imports inside functions, test bodies, or class bodies.
