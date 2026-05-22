"""Human-readable explanations for parsed cron expressions."""

from .parser import ParsedCron

ORDINAL = {
    1: "1st", 2: "2nd", 3: "3rd",
    **{n: f"{n}th" for n in range(4, 32)},
}

DAY_NAMES = {
    "0": "Sunday", "1": "Monday", "2": "Tuesday", "3": "Wednesday",
    "4": "Thursday", "5": "Friday", "6": "Saturday", "7": "Sunday",
}

MONTH_NAMES = {
    "1": "January", "2": "February", "3": "March", "4": "April",
    "5": "May", "6": "June", "7": "July", "8": "August",
    "9": "September", "10": "October", "11": "November", "12": "December",
}


def _explain_field(value: str, field_name: str) -> str:
    """Return a human-readable description of a single cron field value."""
    if value == "*":
        return f"every {field_name}"

    if value.startswith("*/"):
        step = value[2:]
        return f"every {step} {field_name}s"

    if "-" in value and "/" in value:
        range_part, step = value.split("/")
        start, end = range_part.split("-")
        return f"every {step} {field_name}s from {start} to {end}"

    if "-" in value:
        start, end = value.split("-")
        if field_name == "day-of-week":
            start = DAY_NAMES.get(start, start)
            end = DAY_NAMES.get(end, end)
        elif field_name == "month":
            start = MONTH_NAMES.get(start, start)
            end = MONTH_NAMES.get(end, end)
        return f"{field_name} from {start} to {end}"

    if "," in value:
        parts = value.split(",")
        if field_name == "day-of-week":
            parts = [DAY_NAMES.get(p, p) for p in parts]
        elif field_name == "month":
            parts = [MONTH_NAMES.get(p, p) for p in parts]
        listed = ", ".join(parts[:-1]) + f" and {parts[-1]}"
        return f"on {listed}"

    if field_name == "day-of-week":
        return f"on {DAY_NAMES.get(value, value)}"
    if field_name == "month":
        return f"in {MONTH_NAMES.get(value, value)}"
    if field_name == "day-of-month":
        try:
            return f"on the {ORDINAL[int(value)]} day"
        except (KeyError, ValueError):
            return f"on day {value}"

    return f"at {field_name} {value}"


def explain(parsed: ParsedCron) -> str:
    """Return a full human-readable explanation of a parsed cron expression."""
    parts = []

    minute = parsed.minute.raw
    hour = parsed.hour.raw

    if minute == "*" and hour == "*":
        parts.append("every minute")
    elif minute == "0" and hour == "*":
        parts.append("at the start of every hour")
    elif minute == "0" and hour == "0":
        parts.append("at midnight")
    else:
        if hour != "*":
            parts.append(_explain_field(hour, "hour"))
        parts.append(_explain_field(minute, "minute"))

    dom = parsed.day_of_month.raw
    month = parsed.month.raw
    dow = parsed.day_of_week.raw

    if dom != "*":
        parts.append(_explain_field(dom, "day-of-month"))
    if month != "*":
        parts.append(_explain_field(month, "month"))
    if dow != "*":
        parts.append(_explain_field(dow, "day-of-week"))

    return "Runs " + ", ".join(parts) + "."
