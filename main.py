from pydantic import BaseModel
import logging
from fastapi import FastAPI

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from crud import get_user, create_user, create_token_for_user

from database import SessionLocal

from wotcApi import WOTCApi
from schemas import WotcAuthResponse

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


class WotcRefreshToken(BaseModel):
    refresh_token: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


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


@app.post("/token", response_model=Token)
async def login_for_access_token(creds: WotcRefreshToken):
    login_results = WOTCApi().login(creds.refresh_token)
    db = SessionLocal()
    user = get_user(db, login_results['account_id'])
    if not user:
        user = create_user(db, login_results)

    user.token = create_token_for_user(db, user, login_results)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires)
    refresh_token = create_access_token(
        data={"sub": user.id}, expires_delta=timedelta(days=90))
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


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

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception

    user = get_user(db, username=token_data.username)
    if user is None:
        raise credential_exception

    return user


# async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


# async def wotc_login(refresh_token) -> WotcAuthResponse:
#     results = WOTCApi().login(refresh_token)
#     return results
