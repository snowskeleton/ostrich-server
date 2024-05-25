# from datetime import datetime, timedelta, timezone
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
# from jose import JWTError, ExpiredSignatureError

import main
from main import create_access_token, get_current_user, login_for_access_token, LoginToken, app
# from models import User, OstrichToken
# from schemas import WotcAuthResponse, SaveOstrichToken
from wotcApi import WOTCApi


client = TestClient(app)


@pytest.mark.asyncio
async def test_push_live_activity(monkeypatch):
    # def mock_create_ostrich_token_for_user(db, user, ostrich_token: SaveOstrichToken):
    #     return OstrichToken(
    #         access_token=ostrich_token.access_token,
    #         refresh_token=ostrich_token.refresh_token,
    #         expires_in=ostrich_token.expires_in
    #     )
    # monkeypatch.setattr(
    #     main,
    #     "create_ostrich_token_for_user",
    #     mock_create_ostrich_token_for_user,
    # )
    # monkeypatch.setattr(
    #     main,
    #     "get_user",
    #     lambda _, user_id: User(id=user_id),
    # )

    refresh_token = create_access_token(
        data={"sub": 'some_user_id', "exp": datetime.now(timezone.utc) +
              timedelta(minutes=30)})
    item = LoginToken(refresh_token=refresh_token)
    results = await login_for_access_token(item)
    assert all(k in results.model_dump()
               for k in ['access_token', 'refresh_token', 'token_type'])
