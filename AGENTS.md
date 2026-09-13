# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Repository scope

- This repository is a collection of independent Python utilities for AI-assisted data processing; do not assume that scripts share dependencies, configuration, or runtime state unless their documentation says so.
- Script descriptions, usage instructions, and user-facing behavior belong in the Russian [`README.md`](README.md).
- The repository currently has no build system, dependency manifest, linter configuration, or test runner. Do not invent project commands; document commands only after the corresponding tooling is added.

## Required conventions

- Python scripts and agent instructions must be saved as UTF-8 without a BOM.
- Unless a task explicitly specifies another platform, target Windows execution.
- At the beginning of each script, configure the console for UTF-8 before emitting output.
- All informational console messages and error messages must be in English. [`README.md`](README.md) is written in Russian and UTF-8.

