# Contributing to Stock Simulator

Thanks for your interest in contributing! Contributions of all kinds are
welcome, such as bug fixes, new features, documentation improvements
and tests.

## Getting Started

1. Fork the repository and clone your fork
   ```
   git clone https://github.com/<your-username>/stock-sim.git
   cd stock-sim
   ```
2. Follow the setup steps in the [README](README.md) to install
   dependencies and initialise the database.
3. Create a new branch for your change
   ```
   git checkout -b feature/short-description
   ```

## Making Changes

- Keep changes focused - one feature or fix per pull request.
- Follow the existing code style.
- Add or update tests in `tests/` for any new feature or bug fixes.
- Update the README if your change affects setup, usage, or
  features.

## Running Tests

Make sure the test suite passes before submitting:

```
pytest
```

## Commit Messages

Write concise, descriptive commit messages, e.g.:

```
Fix incorrect profit/loss calculation on partial sells
```

rather than:

```
fix bug
```

## Submitting a Pull Request

1. Push your branch to your fork
   ```
   git push origin feature/short-description
   ```
2. Open a pull request against the `main` branch of this repository.
3. In the PR description, explain:
   - What the change does
   - Why it's needed
   - How it was tested
4. Link any related issues (e.g. `Closes #12`).

## Reporting Bugs

Open a GitHub issue and include:

- Steps to reproduce
- Expected vs. actual behavior
- Python version and OS
- Any relevant error messages or logs

## Reporting Security Issues

Please **do not** open a public issue for security vulnerabilities — see
[SECURITY.md](SECURITY.md) for how to report these privately.

## Code of Conduct

Since this is a personal educational project, keep all feedback and
criticism constructive and friendly.
