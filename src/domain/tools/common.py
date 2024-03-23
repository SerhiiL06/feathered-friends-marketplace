def clear_none(data: dict) -> dict | None:
    to_return = {}

    for key, value in data.items():
        if value is not None:
            to_return[key] = value

    return to_return if len(to_return) > 0 else None
