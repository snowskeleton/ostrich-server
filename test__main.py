from fastapi.testclient import TestClient
# import pytest_asyncio
import pytest
# import asyncio

# from wotcApi import WOTCApi, InvalidClientCredentials, WotcException, EmailAddressInUse, AgeRequirement
from schemas import WotcAuthResponse
from main import login_for_access_token, WotcRefreshToken
import main


from main import app

client = TestClient(app)


# @pytest.mark.asyncio
# async def test_login_for_access_token(monkeypatch):

#     # monkeypatch.setattr(WOTCApi, "login", lambda x, y: False)
#     # monkeypatch.setattr(WOTCApi, "login", mock_wotc_login)

#     # results = WOTCApi().login(refresh_token="someToken")
#     # print(results)
#     # assert results.access_token == "some_token"
#     item = WotcRefreshToken(refresh_token="some_token")
#     with pytest.raises(InvalidClientCredentials) as e_info:
#         await login_for_access_token(item)
#     print(e_info)
#     assert e_info.type == InvalidClientCredentials

#     # assert results.access_token == "some_token"
#     # assert results.access_token == "some_token"
#     # assert login_for_access_token(
#     # Item(deviceId="1234", refresh_token="someToken"))


async def mock_wotc_login(_, __) -> WotcAuthResponse:
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
