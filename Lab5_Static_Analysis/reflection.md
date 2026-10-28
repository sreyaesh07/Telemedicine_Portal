\# Reflection



\## 1. Which issues were the easiest to fix, and which were the hardest?



The easiest were the Flake8 and naming issues: adding blank lines, removing the

unused `logging` import and renaming `printAlerts` to `print\_alerts`. The tool

reports the exact line and the fix is mechanical. The hardest were the issues

that needed a design decision, such as the mutable default argument and the

global `SERVICE\_INTERVAL\_DAYS`, because I had to understand why they were

problems and choose a fix that did not change what the program does.



\## 2. Did the tools report any false positives, or miss anything?



Mostly the reports were accurate, but some warnings are judgement calls. For

example, Pylint's `global-statement` warning (W0603) is a style preference, and

the Bandit `assert` finding (B101) is low severity because it was not really

user-facing validation. More importantly, the tools missed several real bugs:

duplicate asset IDs overwriting each other, an empty ID being accepted, a

negative service interval making every asset overdue, and no validation of the

date typed by the user. I only found these by running the program and reading

its output carefully. This shows static analysis cannot replace testing and

code review.



\## 3. How would you integrate static analysis into your development workflow?



I would run Flake8 and Pylint automatically on every commit with a pre-commit

hook, and run all three tools (including Bandit) in a CI pipeline such as

GitHub Actions so that a pull request fails if the score drops below a

threshold or a security issue appears. I would also use editor plugins so

problems are shown while writing code, and fix issues in small commits instead

of letting them build up.



\## 4. What tangible improvements did you see after the fixes?



The Pylint score rose from 6.55/10 to X.XX/10, Bandit went from 2 issues to 0,

and Flake8 went from 12 issues to 0. Beyond the numbers, the code is safer

(secure temp file creation and proper validation), more reliable (no shared

mutable default, files are always closed, bad input is rejected with clear

errors), and easier to read and maintain (docstrings, consistent naming and

formatting).

