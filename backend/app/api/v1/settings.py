from fastapi import APIRouter, Depends
from pydantic import field_validator
from sqlmodel import Session, SQLModel

from app.db.session import get_session
from app.services.expiration import get_warning_days, set_warning_days

router = APIRouter(prefix="/settings", tags=["settings"])

RANGE_ERROR = "El valor debe estar entre 0 y 365 días"


class SettingsRead(SQLModel):
    expiration_warning_days: int


class SettingsUpdate(SQLModel):
    expiration_warning_days: int

    @field_validator("expiration_warning_days")
    @classmethod
    def validate_range(cls, value: int) -> int:
        if not 0 <= value <= 365:
            raise ValueError(RANGE_ERROR)
        return value


@router.get("/", response_model=SettingsRead)
def read_settings(session: Session = Depends(get_session)):
    return SettingsRead(expiration_warning_days=get_warning_days(session))


@router.put("/", response_model=SettingsRead)
def update_settings(data: SettingsUpdate, session: Session = Depends(get_session)):
    return SettingsRead(expiration_warning_days=set_warning_days(session, data.expiration_warning_days))
