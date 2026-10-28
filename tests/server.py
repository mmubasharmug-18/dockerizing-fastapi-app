import os
import socket
import subprocess
import sys
import time
import urllib.request
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class Server:
    def __init__(self, port: int, process: subprocess.Popen, env: dict):
        self.port = port
        self.process = process
        self.env = env
        self.output = ""

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def get(self, path: str):
        with urllib.request.urlopen(self.url + path, timeout=3) as response:
            return response.status, response.read().decode()


def wait_until_up(server: Server, seconds: float = 20) -> None:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if server.process.poll() is not None:
            raise RuntimeError("server exited early:\n" + server.process.stdout.read())
        try:
            server.get("/health")
            return
        except OSError:
            time.sleep(0.2)
    raise RuntimeError("server did not start in time")


def start_env(**settings) -> dict:
    return {
        **os.environ,
        "PYTHONUNBUFFERED": "1",
        "APP_HOST": "127.0.0.1",
        **{key: str(value) for key, value in settings.items()},
    }


@contextmanager
def running_server(**settings):
    port = free_port()
    env = start_env(APP_PORT=port, **settings)
    process = subprocess.Popen(
        [sys.executable, "-m", "app"],
        env=env,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    server = Server(port, process, env)
    try:
        wait_until_up(server)
        yield server
    finally:
        process.terminate()
        try:
            server.output, _ = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            server.output, _ = process.communicate()
