import os
from dataclasses import dataclass
from typing import Mapping, Optional

LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class Settings:
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "INFO"
    app_env: str = "development"


def load_settings(env: Optional[Mapping[str, str]] = None) -> Settings:
    env = os.environ if env is None else env
    problems = []

    host = env.get("APP_HOST", "").strip() or "127.0.0.1"
    app_env = env.get("APP_ENV", "").strip() or "development"

    raw_level = env.get("LOG_LEVEL", "").strip()
    log_level = (raw_level or "INFO").upper()
    if log_level not in LOG_LEVELS:
        problems.append(f"LOG_LEVEL must be one of {', '.join(LOG_LEVELS)} (got {raw_level!r})")

    port = 8000
    raw_port = env.get("APP_PORT", "").strip()
    if raw_port:
        if raw_port.isdigit() and 1 <= int(raw_port) <= 65535:
            port = int(raw_port)
        else:
            problems.append(f"APP_PORT must be a whole number from 1 to 65535 (got {raw_port!r})")

    if problems:
        raise ConfigError("; ".join(problems))

    return Settings(host=host, port=port, log_level=log_level, app_env=app_env)
