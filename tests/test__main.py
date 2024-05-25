from datetime import datetime, timedelta, timezone
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from jose import JWTError, ExpiredSignatureError

import main
from main import create_access_token, get_current_user, login_for_access_token, LoginToken, app
from models import User, OstrichToken
from schemas import WotcAuthResponse, SaveOstrichToken
from wotcApi import WOTCApi


client = TestClient(app)


@pytest.mark.asyncio
async def test_login_for_access_token(monkeypatch):
    def mock_wotc_login(_, __) -> WotcAuthResponse:
        return WotcAuthResponse(
            access_token="some_token",
            account_id="some_account_id",
            client_id="some_client_id",
            display_name="some_display_name",
            domain_id="some_domain_id",
            expires_in=420,
            game_id="some_game_id",
            persona_id="some_persona_id",
            refresh_token="some_refresh_token",
            token_type="some_token_type"
        )

    monkeypatch.setattr(WOTCApi, "login", mock_wotc_login)
    item = LoginToken(wotc_login_token="foobar")
    results = await login_for_access_token(item)
    assert all(k in results.model_dump()
               for k in ['access_token', 'refresh_token', 'token_type'])


@pytest.mark.asyncio
async def test_login_for_access_token_with_refresh_token(monkeypatch):
    def mock_create_ostrich_token_for_user(db, user, ostrich_token: SaveOstrichToken):
        return OstrichToken(
            access_token=ostrich_token.access_token,
            refresh_token=ostrich_token.refresh_token,
            expires_in=ostrich_token.expires_in
        )
    monkeypatch.setattr(
        main,
        "create_ostrich_token_for_user",
        mock_create_ostrich_token_for_user,
    )
    monkeypatch.setattr(
        main,
        "get_user",
        lambda _, user_id: User(id=user_id),
    )

    refresh_token = create_access_token(
        data={"sub": 'some_user_id', "exp": datetime.now(timezone.utc) +
              timedelta(minutes=30)})
    item = LoginToken(refresh_token=refresh_token)
    results = await login_for_access_token(item)
    assert all(k in results.model_dump()
               for k in ['access_token', 'refresh_token', 'token_type'])


@pytest.mark.asyncio
async def test_get_current_user_bad_token():
    with pytest.raises(Exception) as e_info:
        await get_current_user('some garbage string')
    assert e_info.type == JWTError


@pytest.mark.asyncio
async def test_get_current_user_expired_token():
    expired_access_token = create_access_token(
        data={"sub": 'some_user_id', "exp": datetime.now(timezone.utc) +
              timedelta(minutes=-30)})
    with pytest.raises(Exception) as e_info:
        await get_current_user(expired_access_token)
    assert e_info.type == ExpiredSignatureError


@pytest.mark.asyncio
async def test_get_current_user_no_username():
    no_username_access_token = create_access_token(
        data={"some": "garbage", "exp": datetime.now(timezone.utc) +
              timedelta(minutes=30)})
    with pytest.raises(Exception) as e_info:
        await get_current_user(no_username_access_token)
    assert e_info.type == HTTPException


@pytest.mark.asyncio
async def test_get_current_user_not_in_db(monkeypatch):
    real_access_token_user_not_in_db = create_access_token(
        data={"sub": 'some_user_id', "exp": datetime.now(timezone.utc) +
              timedelta(minutes=30)})
    monkeypatch.setattr(main, "get_user", lambda _, user_id: None)
    with pytest.raises(Exception) as e_info:
        await get_current_user(real_access_token_user_not_in_db)
    assert e_info.type == HTTPException


@pytest.mark.asyncio
async def test_get_current_user(monkeypatch):
    real_access_token = create_access_token(
        data={"sub": 'some_user_id', "exp": datetime.now(timezone.utc) +
              timedelta(minutes=30)})
    monkeypatch.setattr(main, "get_user", lambda _, user_id: User(id=user_id))
    user = await get_current_user(real_access_token)
    assert user.id == 'some_user_id'


# @pytest.mark.asyncio
# async def test_read_users_me(monkeypatch):
#     real_access_token = create_access_token(
#         data={"sub": 'some_user_id'}, expires_delta=timedelta(30))
#     monkeypatch.setattr(main, "get_user", lambda _, user_id: User(id=user_id))
#     user = await test_read_users_me(real_access_token)
#     assert user.id == 'some_user_id'
