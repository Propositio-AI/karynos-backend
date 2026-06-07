from app.exceptions.exception import ConfigurationException


def ensure_value(value: str | None, field_name: str) -> str:
    if value is None or value == "":
        raise ConfigurationException(f"missing required setting: {field_name}")
    return value
