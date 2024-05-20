from pydantic import BaseModel
import logging
from fastapi import FastAPI

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext

from crud import get_user, create_user, create_or_update_wotc_token_for_user, create_ostrich_token_for_user

from database import SessionLocal

from wotcApi import WOTCApi
from schemas import SaveOstrichToken, SaveWotcToken, OstrichBearerToken, WotcRefreshToken

from os import getenv
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
db = SessionLocal()


# @app.on_event("startup")
# async def startup_event():
#     logger = logging.getLogger("uvicorn.access")
#     handler = logging.StreamHandler()
#     handler.setFormatter(logging.Formatter(
#         "%(asctime)s - %(levelname)s - %(message)s"))
#     logger.addHandler(handler)


class TokenData(BaseModel):
    username: str | None = None


# class User(BaseModel):
#     username: str
#     email: str or None = None
#     full_name: str or None = None
#     disabled: bool or None = None


# class UserInDB(User):
#     hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# @app.post("/register-device")
# def login_server(creds: Item):
#     results = WOTCApi().login(creds.refresh_token)

#     return {f"Registered token: {creds.refresh_token} with deviceId: {creds.deviceId}"}


@app.post("/token", response_model=OstrichBearerToken)
async def login_for_access_token(creds: WotcRefreshToken) -> OstrichBearerToken:
    # pass along user's authentication with wotc
    # if wotc verifies thier login, we consider them logged in
    login_results = WOTCApi().login(creds.refresh_token)

    # create or pull existing user
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
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_access_token(
        data={"sub": user.id}, expires_delta=timedelta(days=90))
    ostrich_token = SaveOstrichToken(
        expires_in=30,
        access_token=access_token,
        refresh_token=refresh_token,
    )
    ostrich_token = create_ostrich_token_for_user(db, user, ostrich_token)

    # return ostrich token, not wotc
    return OstrichBearerToken(**ostrich_token.__dict__)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


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


# async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user
