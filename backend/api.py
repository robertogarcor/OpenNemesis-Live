"""Optional FastAPI process for backend health/status endpoints."""

from __future__ import annotations

import logging

from fastapi import FastAPI

from backend.livekit_agent.status import check_services


logger = logging.getLogger("OpenNemesis-Live.API")

app = FastAPI(title="OpenNemesis Backend API", version="1.0.0")


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("Starting backend API...")
    try:
        services = check_services()
        for name, value in services.items():
            logger.info("status %s: %s", name, value)
    except Exception as e:
        logger.warning("Could not collect startup status: %s", e)


@app.get("/health")
async def health() -> dict[str, bool]:
    return {"ok": True}


@app.get("/status")
async def status() -> dict[str, object]:
    services = check_services()
    return {
        "ok": True,
        "services": services,
    }
