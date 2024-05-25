from pydantic import BaseModel, ConfigDict


# class ItemBase(BaseModel):
#     title: str
#     description: str | None = None


# class ItemCreate(ItemBase):
#     pass


class Device(BaseModel):
    device_id: str
    apns_token: str

# class UserBase(BaseModel):
#     email: str


# class UserCreate(UserBase):
#     password: str


# class User(BaseModel):
#     id: str
#     is_active: bool
#     devices: list[Device] = []

#     model_config = ConfigDict(from_attributes=True)


class WotcAuthResponse(BaseModel):
    access_token: str
    account_id: str
    client_id: str
    display_name: str
    domain_id: str
    expires_in: int
    game_id: str
    persona_id: str
    refresh_token: str
    token_type: str


class SaveWotcToken(BaseModel):
    access_token: str
    expires_in: int
    refresh_token: str


class SaveOstrichToken(BaseModel):
    access_token: str
    expires_in: int
    refresh_token: str


class OstrichBearerToken(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = 'bearer'


class LoginToken(BaseModel):
    wotc_login_token: str = None
    refresh_token: str = None


class OSTRichRefreshToken(BaseModel):
    refresh_token: str
