import pytest

from app.config import ConfigError, Settings, load_settings


def test_defaults_when_nothing_is_set():
    assert load_settings({}) == Settings(host="127.0.0.1", port=8000, log_level="INFO", app_env="development")


def test_values_are_read_from_the_environment():
    env = {"APP_HOST": "0.0.0.0", "APP_PORT": "9000", "LOG_LEVEL": "DEBUG", "APP_ENV": "staging"}
    settings = load_settings(env)
    assert settings.host == "0.0.0.0"
    assert settings.port == 9000
    assert settings.log_level == "DEBUG"
    assert settings.app_env == "staging"


def test_log_level_is_not_case_sensitive():
    assert load_settings({"LOG_LEVEL": "warning"}).log_level == "WARNING"


def test_spaces_around_values_are_ignored():
    settings = load_settings({"LOG_LEVEL": " error ", "APP_PORT": " 8100 "})
    assert settings.log_level == "ERROR"
    assert settings.port == 8100


def test_empty_values_fall_back_to_defaults():
    settings = load_settings({"LOG_LEVEL": "", "APP_PORT": "", "APP_HOST": "", "APP_ENV": ""})
    assert settings == Settings()


@pytest.mark.parametrize("level", ["LOUD", "TRACE", "5", "info please"])
def test_unknown_log_level_is_rejected(level):
    with pytest.raises(ConfigError) as error:
        load_settings({"LOG_LEVEL": level})
    assert "LOG_LEVEL" in str(error.value)


@pytest.mark.parametrize("port", ["abc", "0", "65536", "-1", "80.5"])
def test_bad_port_is_rejected(port):
    with pytest.raises(ConfigError) as error:
        load_settings({"APP_PORT": port})
    assert "APP_PORT" in str(error.value)


def test_every_problem_is_reported_together():
    with pytest.raises(ConfigError) as error:
        load_settings({"LOG_LEVEL": "LOUD", "APP_PORT": "abc"})
    message = str(error.value)
    assert "LOG_LEVEL" in message
    assert "APP_PORT" in message


def test_reads_the_real_environment_when_no_mapping_is_given(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "ERROR")
    monkeypatch.setenv("APP_ENV", "ci")
    settings = load_settings()
    assert settings.log_level == "ERROR"
    assert settings.app_env == "ci"
