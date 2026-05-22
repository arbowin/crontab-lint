# crontab-lint

> Static analyzer and validator for crontab expressions with human-readable explanations

---

## Installation

```bash
pip install crontab-lint
```

---

## Usage

### Command Line

```bash
crontab-lint "*/5 * * * *"
# ✔ Valid expression
# Runs every 5 minutes
```

```bash
crontab-lint "0 25 * * *"
# ✖ Invalid expression
# Error: Hour field value '25' is out of range (0-23)
```

### Python API

```python
from crontab_lint import validate, explain

result = validate("0 9 * * 1-5")
print(result.is_valid)   # True
print(explain("0 9 * * 1-5"))
# "Runs at 09:00 AM, Monday through Friday"
```

### Lint a crontab file

```bash
crontab-lint --file /etc/cron.d/myjobs
```

---

## Features

- Validates all five crontab fields (minute, hour, day, month, weekday)
- Supports ranges, steps, lists, and special strings (`@daily`, `@reboot`, etc.)
- Human-readable explanations for valid expressions
- Clear, actionable error messages for invalid ones
- Works as a CLI tool or importable Python library

---

## License

This project is licensed under the [MIT License](LICENSE).