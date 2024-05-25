from os import getenv
from dotenv import load_dotenv
from typing import Annotated
from pydantic import BaseModel
import logging
from fastapi import FastAPI, Header

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer  # , OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext

from crud import get_user, create_user, create_or_update_wotc_token_for_user, create_ostrich_token_for_user, delete_ostrich_token, create_or_update_device

import database
from database import SessionLocal

from wotcApi import WOTCApi
from schemas import SaveOstrichToken, SaveWotcToken, OstrichBearerToken, LoginToken, Device
from apns_push_notifications import pushiOSMessage


load_dotenv()
SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_TOKEN_EXPIRE_DAYS = 90

app = FastAPI()
db = SessionLocal()


class TokenData(BaseModel):
    username: str | None = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth_2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couild not validate credentials",
        headers={"WWW_Authenticate": "Bearer"}
    )

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    if username is None:
        raise credential_exception
    token_data = TokenData(username=username)

    user = get_user(db, user_id=token_data.username)
    if user is None:
        raise credential_exception

    return user


@app.post("/register-device")
async def register_device(device_registration: Device, authorization: Annotated[str | None, Header()] = None):
    # splits "Bearer key" into "key"
    auth_key = authorization.split(' ', 1)[-1]
    user = await get_current_user(auth_key)
    device = create_or_update_device(db, user, device_registration)
    import time
    time.sleep(5)
    await pushiOSMessage(device.communication_token, alert_title="Time in round!", alert_body="Active player, finish your turn.")
    return 'OK'


@app.post("/token", response_model=OstrichBearerToken)
async def login_for_access_token(creds: LoginToken) -> OstrichBearerToken:
    if creds.refresh_token:
        user = await get_current_user(creds.refresh_token)
    else:
        # pass along user's authentication with wotc
        # if wotc verifies thier login, we consider them logged in
        login_results = WOTCApi().login(creds.wotc_login_token)
        user = get_user(db, login_results.account_id)
        if not user:
            user = create_user(db, login_results)
        # save wotc token for us to login with later
        wotc_token = SaveWotcToken(
            expires_in=login_results.expires_in,
            access_token=login_results.access_token,
            refresh_token=login_results.refresh_token,
        )
        wotc_token = create_or_update_wotc_token_for_user(db, user, wotc_token)

    # create ostric token for user to authenticate with us later
    access_token_expiry_time = datetime.now(timezone.utc) + \
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.id,
            "exp": access_token_expiry_time,
        }
    )
    refresh_token = create_access_token(
        data={
            "sub": user.id,
        }
    )
    ostrich_token = SaveOstrichToken(
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        access_token=access_token,
        refresh_token=refresh_token,
    )
    ostrich_token = create_ostrich_token_for_user(db, user, ostrich_token)
    if creds.refresh_token:
        delete_ostrich_token(db, creds.refresh_token)

    return OstrichBearerToken(
        refresh_token=ostrich_token.refresh_token,
        access_token=ostrich_token.access_token,
        expires_in=ostrich_token.expires_in,
    )


def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# @app.get("/users/me/", response_model=User)
# async def read_users_me(current_user: User = Depends(get_current_user)):
#     return current_user

# async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user
