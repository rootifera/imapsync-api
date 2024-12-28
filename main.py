from fastapi import FastAPI, HTTPException, Body, Query
from pydantic import BaseModel
import subprocess
import os
import redis.asyncio as aioredis
import json
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_user = os.getenv("REDIS_USER", None)
    redis_password = os.getenv("REDIS_PASSWORD", None)
    redis_client = aioredis.from_url(
        f"redis://{redis_host}:{redis_port}",
        username=redis_user,
        password=redis_password,
        decode_responses=True
    )
    yield
    await redis_client.close()


app = FastAPI(lifespan=lifespan)


class ImapConfig(BaseModel):
    host1: str
    user1: str
    password1: str
    host2: str
    user2: str
    password2: str


@app.get("/")
async def root():
    return {"message": "imapsync: running"}


@app.post("/add_config/{label}")
async def add_config(label: str, config: ImapConfig):
    redis_key = f"imapsync:{label}"
    exists = await redis_client.exists(redis_key)
    if exists:
        raise HTTPException(status_code=400, detail="Configuration with this label already exists.")
    try:
        await redis_client.set(redis_key, json.dumps(config.model_dump()))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": f"Configuration '{label}' saved."}


@app.get("/run/{label}")
async def run_config(label: str, delete_source: bool = Query(False, description="Delete source emails after sync")):
    redis_key = f"imapsync:{label}"
    config_data = await redis_client.get(redis_key)
    if not config_data:
        raise HTTPException(status_code=404, detail="Configuration not found.")

    config = json.loads(config_data)
    command = [
        "/usr/local/bin/imapsync",
        "--host1", config["host1"],
        "--user1", config["user1"],
        "--password1", config["password1"],
        "--host2", config["host2"],
        "--user2", config["user2"],
        "--password2", config["password2"]
    ]

    if delete_source:
        command.append("--delete1")

    try:
        result = subprocess.run(command, capture_output=True, text=True)
        return {"label": label, "output": result.stdout}
    except Exception as e:
        return {"label": label, "error": str(e)}


@app.get("/runall")
async def run_all(delete_source: bool = Query(False, description="Delete source emails after sync")):
    labels = [key async for key in redis_client.scan_iter(match="imapsync:*")]
    if not labels:
        raise HTTPException(status_code=404, detail="No configurations found.")

    results = []
    for label in labels:
        config_data = await redis_client.get(label)
        config = json.loads(config_data)
        command = [
            "/usr/local/bin/imapsync",
            "--host1", config["host1"],
            "--user1", config["user1"],
            "--password1", config["password1"],
            "--host2", config["host2"],
            "--user2", config["user2"],
            "--password2", config["password2"]
        ]

        if delete_source:
            command.append("--delete1")

        try:
            result = subprocess.run(command, capture_output=True, text=True)
            results.append({label: result.stdout})
        except Exception as e:
            results.append({label: str(e)})

    return {"results": results}


@app.delete("/delete_config/{label}")
async def delete_config(label: str):
    redis_key = f"imapsync:{label}"
    exists = await redis_client.exists(redis_key)
    if not exists:
        raise HTTPException(status_code=404, detail="Configuration not found.")
    try:
        await redis_client.delete(redis_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": f"Configuration '{label}' deleted."}


@app.get("/get_labels")
async def get_labels():
    labels = [key async for key in redis_client.scan_iter(match="imapsync:*")]
    labels = [label.split("imapsync:")[1] for label in labels]
    return {"labels": labels}


@app.post("/run_labels")
async def run_labels(labels: list[str] = Body(...),
                     delete_source: bool = Query(False, description="Delete source emails after sync")):
    results = []
    for label in labels:
        redis_key = f"imapsync:{label}"
        config_data = await redis_client.get(redis_key)
        if not config_data:
            results.append({label: "Configuration not found."})
            continue

        config = json.loads(config_data)
        command = [
            "/usr/local/bin/imapsync",
            "--host1", config["host1"],
            "--user1", config["user1"],
            "--password1", config["password1"],
            "--host2", config["host2"],
            "--user2", config["user2"],
            "--password2", config["password2"]
        ]

        if delete_source:
            command.append("--delete1")

        try:
            result = subprocess.run(command, capture_output=True, text=True)
            results.append({label: result.stdout})
        except Exception as e:
            results.append({label: str(e)})

    return {"results": results}
