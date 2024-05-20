import uuid
from sqlalchemy.orm import Session

# from . import models, schemas
import models
from schemas import SaveOstrichToken, SaveWotcToken, WotcAuthResponse
from models import WotcToken, OstrichToken


def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: WotcAuthResponse):
    db_user = models.User(id=user.account_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_or_update_wotc_token_for_user(db: Session, user: models.User, incoming_token: SaveWotcToken):
    token = db.query(models.WotcToken).filter(
        models.WotcToken.user_id == user.id).first()
    if not token:
        token = models.WotcToken(
            id=str(uuid.uuid4()),
            access_token=incoming_token.access_token,
            expires_in=incoming_token.expires_in,
            refresh_token=incoming_token.refresh_token,
            user=user,
        )
    else:
        token.access_token = incoming_token.access_token
        token.refresh_token = incoming_token.refresh_token
        token.expires_in = incoming_token.expires_in

    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def create_ostrich_token_for_user(db: Session, user: models.User, incoming_token: SaveOstrichToken) -> OstrichToken:
    token = models.OstrichToken(
        id=str(uuid.uuid4()),
        access_token=incoming_token.access_token,
        expires_in=incoming_token.expires_in,
        refresh_token=incoming_token.refresh_token,
        user=user,
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


# def get_items(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Item).offset(skip).limit(limit).all()


# def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
#     db_item = models.Item(**item.model_dump(), owner_id=user_id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item
