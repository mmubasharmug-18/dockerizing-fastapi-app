# Patient Vitals API in Docker

This is the Week 14 Patient Vitals API packaged in a Docker image. The container runs on a port mapped to my computer, and settings like the log level come from environment variables, so nothing is hard-coded in the image.

All data is made up. Records are kept in memory, so they are gone when the container stops.

## Folder structure

```
patient_vitals_docker/
  app/
    main.py            creates the app and logs startup
    config.py          reads the environment variables
    logs.py            sets the log level
    __main__.py        starts the server (python -m app)
    healthcheck.py     used by Docker to check the app is alive
    models.py          request and response models
    errors.py          readable validation messages
    handlers.py        validation errors return 400
    storage.py         in-memory storage
    summary.py         average calculation
    routes/            health.py and vitals.py
  tests/
    unit/              config, logging, models, storage, summary
    integration/       endpoints, logging, starting the real server
    helpers.py
    server.py          starts the app in a subprocess for tests
  samples/             JSON bodies for curl
  requests.http        ready-made requests for VS Code
  Dockerfile
  .dockerignore
  .env.example         example settings for --env-file
  requirements.txt     what the image needs
  requirements-dev.txt adds pytest and httpx for tests
  pytest.ini
```

## Endpoints

Same as Week 14.

| Method | Path | What it does |
| --- | --- | --- |
| GET | `/health` | `{"status": "ok", "timestamp": ...}` |
| POST | `/vitals` | Validates and saves one record, returns 201. Bad input gets 400 |
| GET | `/patients/{patient_id}/vitals` | Records for a patient, newest first. Optional `?limit=N` |
| GET | `/patients/{patient_id}/summary` | Average systolic, diastolic, glucose and the record count |

## Settings

| Variable | Default in the image | Meaning |
| --- | --- | --- |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL` |
| `APP_ENV` | `production` | A label. It is printed at startup and shown in the Swagger page |
| `APP_PORT` | `8000` | Port the app listens on inside the container |
| `APP_HOST` | `0.0.0.0` | Address the app listens on inside the container |

If a value is wrong, the app stops straight away and says why, instead of starting with a setting nobody meant.

`APP_HOST` has to be `0.0.0.0` inside a container. If the app listened on `127.0.0.1` there, nothing from outside the container could reach it, even with a port mapping. The image sets this already. Running `python -m app` on my own computer defaults to `127.0.0.1`.

What each level shows:

- `DEBUG`: everything, including which patient a saved record belongs to
- `INFO`: startup, every request, every saved record
- `WARNING`: only problems, like rejected requests and unknown patients
- `ERROR` and `CRITICAL`: almost nothing, this API rarely logs at these levels

## The Dockerfile

```
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000 \
    LOG_LEVEL=INFO \
    APP_ENV=production

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --create-home appuser

COPY app/ ./app/

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python", "-m", "app.healthcheck"]

CMD ["python", "-m", "app"]
```

- `ENV`: the default settings. `docker run -e` overrides them.
- `COPY requirements.txt` and `pip install` come before copying the code. Docker caches each step, so changing the code does not reinstall the packages.
- `useradd` and `USER`: the app runs as a normal user, not root.
- `EXPOSE 8000`: a note that the app uses port 8000. It does not open the port by itself. `-p` does that.
- `HEALTHCHECK`: Docker calls `/health` every 30 seconds and shows `healthy` or `unhealthy` in `docker ps`.
- `CMD`: starts the app. `python -m app` reads the settings and starts uvicorn with the right host, port and log level.

`.dockerignore` keeps tests, samples, Git files and this README out of the image.

## Build and run

Docker Desktop must be running. Open a terminal in the project folder.

Build:

```
docker build -t patient-vitals-api .
```

Run on port 8000:

```
docker run -d --name vitals-api -p 8000:8000 patient-vitals-api
```

`-p 8000:8000` means host port 8000 goes to container port 8000. `-d` runs it in the background.

Open these in the browser:

- http://localhost:8000/docs (Swagger)
- http://localhost:8000/health

## Call the endpoints from my computer

On Windows PowerShell use `curl.exe`. On Mac or Linux, `curl` works the same way.

```
curl.exe http://localhost:8000/health

curl.exe -X POST http://localhost:8000/vitals -H "Content-Type: application/json" -d @samples/valid.json

curl.exe -X POST http://localhost:8000/vitals -H "Content-Type: application/json" -d @samples/valid_2.json

curl.exe http://localhost:8000/patients/P-1001/vitals

curl.exe "http://localhost:8000/patients/P-1001/vitals?limit=1"

curl.exe http://localhost:8000/patients/P-1001/summary
```

Error cases (add `-i` to see the status line):

```
curl.exe -i -X POST http://localhost:8000/vitals -H "Content-Type: application/json" -d @samples/bad_range.json

curl.exe -i -X POST http://localhost:8000/vitals -H "Content-Type: application/json" -d @samples/bad_types.json

curl.exe -i http://localhost:8000/patients/nobody/summary
```

The summary for P-1001 after the two valid posts:

```json
{
  "patient_id": "P-1001",
  "record_count": 2,
  "averages": { "systolic": 127.5, "diastolic": 84.0, "glucose": 102.75 }
}
```

The `requests.http` file has the same requests for the VS Code REST Client extension.

## Pass settings with environment variables

Run a second container on a different host port, with the log level and environment changed:

```
docker run -d --name vitals-debug -p 9000:8000 -e LOG_LEVEL=DEBUG -e APP_ENV=staging patient-vitals-api
```

Here host port 9000 goes to container port 8000, so the app is at http://localhost:9000/docs. The Swagger description now says `Environment: staging`.

Or put the settings in a file and pass the file (`.env.example` is a ready example):

```
docker run -d --name vitals-envfile -p 9100:8000 --env-file .env.example patient-vitals-api
```

Look at the logs and compare the two containers. Send the same requests to both first:

```
docker logs vitals-api
docker logs vitals-debug
docker logs -f vitals-debug
```

`-f` keeps following the log. Press Ctrl+C to stop following. The default container shows startup and requests at INFO. The debug one also shows the `DEBUG` lines with the patient id.

Try a wrong value. It should stop at once with exit code 2:

```
docker run --rm -e LOG_LEVEL=LOUD patient-vitals-api
```

Useful checks:

```
docker ps
docker exec vitals-api env
```

`docker ps` shows the port mapping and, after about 30 seconds, `(healthy)`. `docker exec ... env` lists the settings inside the running container.

Clean up when done:

```
docker stop vitals-api vitals-debug vitals-envfile
docker rm vitals-api vitals-debug vitals-envfile
```

Stopping and starting a container again empties the records, because they live in memory.

## Run without Docker

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
python -m app
```

On Mac or Linux, activate with `source .venv/bin/activate`. Settings work the same way. In PowerShell:

```
$env:LOG_LEVEL="DEBUG"
python -m app
```

## Tests

```
pytest
```

- `unit/test_config.py` checks defaults, overrides, case, spaces and bad values.
- `unit/test_logs.py` checks that the log level is applied once.
- `integration/test_logging.py` checks which messages appear at which level.
- `integration/test_entrypoint.py` starts the real server on a free port with different environment variables. It checks the health endpoint, the real endpoints, `APP_ENV` in the docs, INFO against WARNING output, bad settings, and the health check script.
- The Week 14 tests for validation, endpoints, storage and the summary are still here and unchanged.

## My results

*(Fill in after running.)*

- Did `docker build` finish, and how big is the image? (`docker images patient-vitals-api`)
- Which commands from my computer worked against the container? What did `/health` and the summary return?
- What changed in the logs between `LOG_LEVEL=INFO` and `LOG_LEVEL=DEBUG`?
- What does `-p 9000:8000` mean? Which URL did I open?
- What happened with `LOG_LEVEL=LOUD`?
- What did `docker ps` show for the status?

## What to submit

- The project folder (or a GitHub link).
- Screenshots of `docker build`, `docker run` with `docker ps`, a curl call from my computer, the Swagger page, and `docker logs`.
- This README with the results filled in.

## Takeaways

- A container has its own network. `-p host:container` is what connects it to my computer.
- Inside a container the app must listen on `0.0.0.0`, not `127.0.0.1`.
- Environment variables let one image run in different ways without a rebuild.
- Check settings at startup and stop with a clear message if one is wrong.
- Records live in memory, so a new container always starts empty.

## Limits

- The data is made up, and logs can contain patient ids at `DEBUG`. Do not use real patient data.
- No login. Anyone who can reach the port can use the API.
- `requirements.txt` uses minimum versions, so a rebuild next month can pull newer packages. For exact repeat builds, run `pip freeze` in the working venv and copy the versions for `fastapi` and `uvicorn` into `requirements.txt`.
- Rebuild the image after changing the code.
