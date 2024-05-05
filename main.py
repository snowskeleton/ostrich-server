from pydantic import BaseModel
import logging
from fastapi import FastAPI
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger("uvicorn.access")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


class Item(BaseModel):
    deviceId: str
    refreshToken: str


@app.post("/register-device")
def login_server(creds: Item):
    from wotcApi import WOTCApi
    results = WOTCApi().login(creds.refreshToken)
    return {f"Registered token: {creds.refreshToken} with deviceId: {creds.deviceId}"}
