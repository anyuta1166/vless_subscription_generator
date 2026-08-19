import uuid as uuid_lib

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Server, ServerUser, User


router = APIRouter(
    prefix="/admin/assignments",
    tags=["admin-assignments"],
)

templates = Jinja2Templates(
    directory="app/templates",
)


def is_htmx(request: Request) -> bool:
    return request.headers.get("HX-Request") == "true"


async def get_user(
    db: AsyncSession,
    user_pk: int,
) -> User:
    user = await db.get(User, user_pk)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


async def get_server(
    db: AsyncSession,
    server_pk: int,
) -> Server:
    server = await db.get(Server, server_pk)

    if server is None:
        raise HTTPException(
            status_code=404,
            detail="Server not found",
        )

    return server


def normalize_uuid(value: str) -> str:
    value = value.strip()

    try:
        parsed = uuid_lib.UUID(value)
    except ValueError as exc:
        raise ValueError(
            "Некорректный UUID"
        ) from exc

    return str(parsed)


async def get_assignment(
    db: AsyncSession,
    *,
    user_pk: int,
    server_pk: int,
) -> ServerUser | None:
    result = await db.execute(
        select(ServerUser)
        .where(
            ServerUser.user_pk == user_pk,
            ServerUser.server_pk == server_pk,
        )
    )

    return result.scalar_one_or_none()


async def render_assignment_row(
    *,
    request: Request,
    db: AsyncSession,
    user: User,
    server: Server,
    error: str | None = None,
):
    assignment = await get_assignment(
        db,
        user_pk=user.id,
        server_pk=server.id,
    )

    return templates.TemplateResponse(
        request=request,
        name="assignments/_row.html",
        context={
            "user": user,
            "server": server,
            "assignment": assignment,
            "error": error,
        },
    )


@router.get(
    "",
    response_class=HTMLResponse,
)
async def assignments_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(
            User,
            func.count(ServerUser.id).label(
                "assignment_count"
            ),
        )
        .outerjoin(
            ServerUser,
            ServerUser.user_pk == User.id,
        )
        .group_by(User.id)
        .order_by(
            User.display_name,
            User.user_id,
        )
    )

    users = result.all()

    return templates.TemplateResponse(
        request=request,
        name="assignments/list.html",
        context={
            "users": users,
        },
    )


@router.get(
    "/{user_pk}",
    response_class=HTMLResponse,
)
async def assignments_user(
    request: Request,
    user_pk: int,
    db: AsyncSession = Depends(get_db),
):
    user = await get_user(
        db,
        user_pk,
    )

    result = await db.execute(
        select(
            Server,
            ServerUser,
        )
        .outerjoin(
            ServerUser,
            and_(
                ServerUser.server_pk == Server.id,
                ServerUser.user_pk == user_pk,
            ),
        )
        .order_by(
            Server.sort_order,
            Server.server_id,
        )
    )

    rows = result.all()

    return templates.TemplateResponse(
        request=request,
        name="assignments/user.html",
        context={
            "user": user,
            "rows": rows,
        },
    )


@router.post(
    "/{user_pk}/{server_pk}",
)
async def assignment_save(
    request: Request,
    user_pk: int,
    server_pk: int,
    uuid: str = Form(...),
    enabled: bool = Form(False),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user(
        db,
        user_pk,
    )

    server = await get_server(
        db,
        server_pk,
    )

    try:
        normalized_uuid = normalize_uuid(
            uuid
        )
    except ValueError as exc:
        if is_htmx(request):
            return await render_assignment_row(
                request=request,
                db=db,
                user=user,
                server=server,
                error=str(exc),
            )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    assignment = await get_assignment(
        db,
        user_pk=user_pk,
        server_pk=server_pk,
    )

    if assignment is None:
        assignment = ServerUser(
            user_pk=user_pk,
            server_pk=server_pk,
            uuid=normalized_uuid,
            enabled=enabled,
        )

        db.add(assignment)

    else:
        assignment.uuid = normalized_uuid
        assignment.enabled = enabled

    try:
        await db.commit()

    except IntegrityError:
        await db.rollback()

        if is_htmx(request):
            return await render_assignment_row(
                request=request,
                db=db,
                user=user,
                server=server,
                error=(
                    "Этот UUID уже используется "
                    "другим пользователем на данном сервере"
                ),
            )

        raise HTTPException(
            status_code=409,
            detail=(
                "Этот UUID уже используется "
                "другим пользователем на данном сервере"
            ),
        )

    if is_htmx(request):
        return await render_assignment_row(
            request=request,
            db=db,
            user=user,
            server=server,
        )

    return RedirectResponse(
        url=f"/admin/assignments/{user_pk}",
        status_code=303,
    )


@router.post(
    "/{user_pk}/{server_pk}/delete",
)
async def assignment_delete(
    request: Request,
    user_pk: int,
    server_pk: int,
    db: AsyncSession = Depends(get_db),
):
    user = await get_user(
        db,
        user_pk,
    )

    server = await get_server(
        db,
        server_pk,
    )

    assignment = await get_assignment(
        db,
        user_pk=user_pk,
        server_pk=server_pk,
    )

    if assignment is not None:
        await db.delete(assignment)
        await db.commit()

    if is_htmx(request):
        return await render_assignment_row(
            request=request,
            db=db,
            user=user,
            server=server,
        )

    return RedirectResponse(
        url=f"/admin/assignments/{user_pk}",
        status_code=303,
    )
