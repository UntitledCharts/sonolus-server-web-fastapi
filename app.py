from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path
from starlette.staticfiles import StaticFiles

import yaml

with open("config.yml", "r", encoding="utf8") as f:
    config = yaml.load(f, yaml.Loader)

app = FastAPI()

dist_dir = Path(__file__).parent / "dist"

prefix = config["prefix"]

if not dist_dir.is_dir():
    raise ValueError(f"The 'dist' directory '{dist_dir}' does not exist.")

app.mount(f"{prefix}/dist", StaticFiles(directory=dist_dir), name="dist")


@app.get(f"{prefix}/{{path:path}}")
async def serve_spa(path: str):
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
