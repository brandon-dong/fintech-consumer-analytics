"""SQL formatting helpers for Snowflake IN-clause injection.

Values must be sourced from the database (e.g., sidebar multiselect
populated by a SELECT DISTINCT query). These functions are NOT safe
for arbitrary user-typed text.
"""


def str_in_clause(values: list) -> str:
    """Return a Snowflake-safe SQL IN-clause string for string values.

    Single quotes are doubled per SQL standard. Example:
        ["Credit card", "it's"] -> "('Credit card', 'it''s')"
    """
    if not values:
        raise ValueError("values must contain at least one element")
    escaped = [str(v).replace("'", "''") for v in values]
    return "('" + "', '".join(escaped) + "')"


def int_in_clause(values: list) -> str:
    """Return a SQL IN-clause string for integer values.

    Each element is cast with int() to prevent non-integer injection.
    Example: [2023, 2024] -> "(2023, 2024)"
    """
    if not values:
        raise ValueError("values must contain at least one element")
    return "(" + ", ".join(str(int(v)) for v in values) + ")"
