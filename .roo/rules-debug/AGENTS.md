# Debug Mode Rules

- Assume Windows unless the task explicitly names another runtime.
- Check console encoding initialization before diagnosing garbled output; scripts must configure UTF-8 before printing.
- Distinguish English runtime messages from Russian documentation when comparing expected output.
- Do not infer a cross-script failure path without evidence of a shared dependency or configuration.

