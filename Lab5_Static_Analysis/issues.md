# Lab 5: Static Code Analysis - Issue Report

**File analysed:** `maintenance_system.py` (Warehouse Asset Maintenance Registry)

**Scores:** Pylint 6.55/10 before, X.XX/10 after | Bandit 2 issues before, 0 after | Flake8 12 issues before, 0 after

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Insecure temp file (`mktemp`, Bandit B306, Medium) | Security | 40 | `tempfile.mktemp()` only returns a name, so another process could create a file with that name before it is opened (race condition) | Used `tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")` in a `with` block |
| `assert` used for validation (Bandit B101, Low) | Security | 61 | `assert` is removed when Python runs with `-O`, so the check can silently disappear | Replaced with an explicit `if not assets:` check that raises `ValueError` |
| Mutable default argument (Pylint W0102) | Bug | 10-13 | `logs=[]` is created once and shared across calls, so the registration count keeps growing (it showed 4 for 3 distinct assets) | Changed the default to `None` and create a new list inside the function |
| Bare `except` (Pylint W0702, Flake8 E722) | Bug | 18 | Catches every exception (including typos and KeyboardInterrupt) and hides the real cause | Catch only `KeyError` and print which asset was not found |
| Files opened without `with` or encoding (Pylint R1732, W1514) | Quality | 34-36, 41-43 | File may stay open if `write` fails, and the encoding depends on the OS | Used `with open(..., encoding="utf-8")` and `json.dump` |
| Duplicate asset IDs silently overwrite data | Bug | 51, 54 | Registering `FL-01` as a Crane replaced the existing Forklift with no warning | Reject IDs that already exist and report an error |
| Empty asset ID accepted | Bug | 53 | `""` was registered as a valid asset and appeared in the alerts | Validate that the ID is a non-empty string |
| Negative service interval accepted | Bug | 29-31, 57 | `change_interval(-30)` made every asset "overdue" | Reject intervals of 0 or less with `ValueError` |
| Unvalidated date input | Bug | 15-19, 58-60 | A bad date such as `abc` is stored and later crashes `strptime` in `due_for_inspection` | Validate with `datetime.strptime` in a `try/except ValueError` before saving |
| Unused import (Pylint W0611, Flake8 F401) | Quality | 2 | `logging` is imported but never used | Removed the import |
| Function naming (Pylint C0103) | Style | 46 | `printAlerts` is not snake_case | Renamed to `print_alerts` and updated the call in `main()` |
| Missing docstrings (Pylint C0114, C0116) | Quality | 1, 10, 15, 21, 29, 33, 39, 46, 50 | Module and all functions are undocumented | Added a module docstring and a short docstring per function |
| Dict iteration (Pylint C0206) | Quality | 23 | Loops over keys, then looks up each value | Used `for asset_id, info in assets.items():` |
| Global statement (Pylint W0603) | Design | 30 | Function modifies module-level state | Kept for simplicity / replaced with a constant parameter (state which you chose) |
| Missing blank lines (Flake8 E302, E305) | Style | 10, 15, 21, 29, 33, 39, 46, 50, 66 | PEP 8 requires 2 blank lines around top-level definitions | Added the blank lines |
| Line too long (Flake8 E501) | Style | 11 | 98 characters (limit 79) | Split the dictionary across several lines |
| `main()` runs on import | Design | 66 | Importing the module executes the program | Wrapped the call in `if __name__ == "__main__":` |