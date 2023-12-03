from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.models import CharityProject, User
from app.schemas.donation import (
    DonationCreate, DonationDBFull, DonationDBShort
)
from app.services.investment_process import run_investment_process

router = APIRouter(prefix='/donation', tags=['Donations'])


@router.get(
    '/',
    response_model=list[DonationDBFull],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(
        session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров.

    Получает список всех пожертвований.
    """
    db_objs = await donation_crud.get_multi(session)
    return db_objs


@router.post(
    '/',
    response_model=DonationDBShort,
    response_model_exclude_none=True,
)
async def create_donation(
        new_donation: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):
    """Сделать пожертвование."""
    donation_db = await donation_crud.create(new_donation, session)
    invested_donation = await run_investment_process(
        session=session,
        created_obj=donation_db,
        investing_db_model=CharityProject,
    )
    return invested_donation


@router.get(
    '/my',
    response_model=list[DonationDBShort],
    response_model_exclude_none=True,
)
async def get_user_donations(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):
    """Получить список моих пожертвований."""
    donations = await donation_crud.get_by_user(session, user)
    return donations
