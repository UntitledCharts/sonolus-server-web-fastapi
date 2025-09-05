from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, RedirectResponse
from starlette.staticfiles import StaticFiles

import yaml

from urllib.parse import urlparse, urljoin, urlunparse, urlencode
from pathlib import Path

with open("config.yml", "r", encoding="utf8") as f:
    config = yaml.load(f, yaml.Loader)

app = FastAPI()

dist_dir = Path(__file__).parent / "dist"

prefix = config["prefix"]

if not dist_dir.is_dir():
    raise ValueError(f"The 'dist' directory '{dist_dir}' does not exist.")

app.mount(f"{prefix}/dist", StaticFiles(directory=dist_dir), name="dist")


@app.get(f"{prefix}/{{path:path}}")
async def serve_spa(request: Request, path: str):
    if path.startswith("sonolus/"):
        if config["redirect-sonolus"]["enabled"]:
            redirect_base = config["redirect-sonolus"]["path"]
            target_scheme = "https" if config["https"] else "http"
            parsed_url = urlparse(redirect_base)

            query_params = request.query_params
            query_string = urlencode(query_params)

            if parsed_url.scheme and parsed_url.netloc:
                new_url = urljoin(redirect_base, path)
                if query_string:
                    new_url = f"{new_url}?{query_string}"
                parsed_url = urlparse(new_url)
                parsed_url = parsed_url._replace(scheme=target_scheme)
                full_redirect_url = urlunparse(parsed_url)
            else:
                base_url = str(request.base_url)
                full_url = urljoin(base_url, redirect_base)
                full_url = urljoin(full_url, path)
                if query_string:
                    full_url = f"{full_url}?{query_string}"
                parsed_url = urlparse(full_url)
                parsed_url = parsed_url._replace(scheme=target_scheme)
                full_redirect_url = urlunparse(parsed_url)
            return RedirectResponse(full_redirect_url, status_code=302)
    file_path = dist_dir / path
    if not file_path.exists():
        file_path = dist_dir / "index.html"
    elif file_path.is_dir():
        file_path = dist_dir / "index.html"
    return FileResponse(file_path)


@app.get(f"{prefix}/")
async def serve_index():
    return FileResponse(dist_dir / "index.html")


async def start_fastapi():
    import uvicorn

    config_server = uvicorn.Config("app:app", host="0.0.0.0", port=config["port"])
    server = uvicorn.Server(config_server)
    await server.serve()
