def str_in_clause(values: list) -> str:
    escaped = [str(v).replace("'", "''") for v in values]
    return "('" + "', '".join(escaped) + "')"


def int_in_clause(values: list) -> str:
    return "(" + ", ".join(str(int(v)) for v in values) + ")"
