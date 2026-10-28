import json
import subprocess
import sys
import urllib.request

from tests.server import ROOT, free_port, running_server, start_env


def run_module(module, **settings):
    return subprocess.run(
        [sys.executable, "-m", module],
        env=start_env(**settings),
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )


def test_server_starts_on_the_port_from_the_environment():
    with running_server(LOG_LEVEL="INFO") as server:
        status, body = server.get("/health")
    assert status == 200
    assert json.loads(body)["status"] == "ok"


def test_server_answers_the_real_endpoints():
    sample = {
        "patient_id": "P-1001",
        "age": 45,
        "blood_pressure": {"systolic": 120, "diastolic": 80},
        "glucose_level": 95.5,
    }
    with running_server() as server:
        request = urllib.request.Request(
            server.url + "/vitals",
            data=json.dumps(sample).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=3) as response:
            assert response.status == 201
        status, body = server.get("/patients/P-1001/summary")
    assert status == 200
    assert json.loads(body)["record_count"] == 1


def test_app_env_shows_up_in_the_api_description():
    with running_server(APP_ENV="staging") as server:
        _, body = server.get("/openapi.json")
    assert "Environment: staging" in json.loads(body)["info"]["description"]


def test_info_level_prints_the_startup_messages():
    with running_server(LOG_LEVEL="INFO", APP_ENV="staging") as server:
        pass
    assert "Starting Patient Vitals API (environment=staging, log level=INFO)" in server.output
    assert "Application startup complete" in server.output


def test_warning_level_hides_the_startup_messages():
    with running_server(LOG_LEVEL="WARNING") as server:
        pass
    assert "Starting Patient Vitals API" not in server.output
    assert "Application startup complete" not in server.output


def test_bad_log_level_stops_the_app_with_a_clear_message():
    result = run_module("app", LOG_LEVEL="LOUD", APP_PORT=free_port())
    assert result.returncode == 2
    assert "LOG_LEVEL" in result.stderr


def test_bad_port_stops_the_app_with_a_clear_message():
    result = run_module("app", APP_PORT="not-a-port")
    assert result.returncode == 2
    assert "APP_PORT" in result.stderr


def test_healthcheck_passes_while_the_server_is_running():
    with running_server() as server:
        result = run_module("app.healthcheck", APP_PORT=server.port)
    assert result.returncode == 0


def test_healthcheck_fails_when_nothing_is_listening():
    result = run_module("app.healthcheck", APP_PORT=free_port())
    assert result.returncode == 1
