from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_invested_project_before_delete,
    check_name_duplicate, check_new_amount_more_than_invested,
    check_project_exists, check_project_is_not_closed,
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.models import Donation
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
)
from app.services.investment_process import run_investment_process

router = APIRouter(prefix='/charity_project', tags=['Charity Projects'])


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_charity_projects(
        session: AsyncSession = Depends(get_async_session),
):
    """Получает список всех проектов."""
    db_objs = await charity_project_crud.get_multi(session)
    return db_objs


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_charity_project(
        new_project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров.

    Создает благотворительный проект.
    """
    await check_name_duplicate(new_project.name, session)
    project_db = await charity_project_crud.create(
        obj_in=new_project, session=session
    )
    invested_project = await run_investment_process(
        session=session,
        created_obj=project_db,
        investing_db_model=Donation,
    )
    return invested_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def delete_charity_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров.

    Удаляет проект. Нельзя удалить проект, в который уже были инвестированы
    средства, его можно только закрыть.
    """
    db_project = await check_project_exists(project_id, session)
    check_invested_project_before_delete(db_project)
    db_project = await charity_project_crud.remove(db_project, session)
    return db_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def update_charity_project(
        project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров.

    Закрытый проект нельзя редактировать,
    также нельзя установить требуемую сумму меньше уже вложенной.
    """
    db_project = await check_project_exists(project_id, session)
    check_project_is_not_closed(db_project)
    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)
    if obj_in.full_amount is not None:
        check_new_amount_more_than_invested(db_project, obj_in)
    db_project = await charity_project_crud.update(db_project, obj_in, session)
    return db_project
