from datetime import datetime
from typing import Type, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation

FINANCING_ENTITY = Union[CharityProject, Donation]


async def run_investment_process(
        session: AsyncSession,
        created_obj: FINANCING_ENTITY,
        investing_db_model: Union[Type[CharityProject], Type[Donation]],
) -> FINANCING_ENTITY:
    """Запускает процесс инвестирования"""
    invest_available_db_list = await get_not_fully_invested_objs(
        investing_db_model, session
    )

    for invest_available_obj in invest_available_db_list:
        await run_donation_to_project_invest(
            invest_available_obj, created_obj
        )
        session.add(invest_available_obj)
        if created_obj.full_amount:
            break
    session.add(created_obj)
    await session.commit()
    await session.refresh(created_obj)
    return created_obj


async def get_not_fully_invested_objs(
        db_model: Union[Type[CharityProject], Type[Donation]],
        session: AsyncSession
):
    """
    Получает список проектов или пожертвований, доступных для инвестирования.
    """
    invest_available_objs = await session.execute(
        select(db_model).where(
            db_model.fully_invested == 0
        ).order_by(db_model.create_date)
    )
    return invest_available_objs.scalars().all()


async def close_fully_invested_obj(obj: FINANCING_ENTITY):
    """Закрывает проект или пожертвование."""
    obj.invested_amount = obj.full_amount
    obj.fully_invested = True
    obj.close_date = datetime.now()


async def run_donation_to_project_invest(
        invest_available_obj: FINANCING_ENTITY,
        created_obj: FINANCING_ENTITY,
):
    """
     Если есть доступные пожертвования, инвестирует их в открытые проекты.
    """
    if invest_available_obj.balance > created_obj.balance:
        invest_available_obj.invested_amount += created_obj.balance
        await close_fully_invested_obj(created_obj)
    elif invest_available_obj.balance < created_obj.balance:
        created_obj.invested_amount += invest_available_obj.balance
        await close_fully_invested_obj(invest_available_obj)
    else:
        await close_fully_invested_obj(created_obj)
        await close_fully_invested_obj(invest_available_obj)
